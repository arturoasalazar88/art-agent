# Config de Producción — Ornstein

> Fecha de validación: 2026-04-30 (sesión 14)
> Referencia de resultados: `outputs/ornstein_validation_results.md`
> Hardware: NVIDIA RTX 3060 12GB | Intel i5-9600K | 32GB RAM | Debian Linux

---

## Modelo

| Campo | Valor |
|---|---|
| Archivo GGUF | `Ornstein-26B-A4B-it-Q4_K_M.gguf` |
| Ruta en servidor | `~/models/gemma4/Ornstein-26B-A4B-it-Q4_K_M.gguf` |
| Alias | `ornstein` |
| Rol | Normalización técnica — transforma prosa creativa en contratos JSON para Unity MCP |

---

## Comando de Arranque (producción)

```bash
nohup ~/llama.cpp/build/bin/llama-server \
  --model ~/models/gemma4/Ornstein-26B-A4B-it-Q4_K_M.gguf \
  --alias ornstein \
  --host 0.0.0.0 --port 8012 \
  --ctx-size 24576 \
  --cache-type-k q4_0 --cache-type-v q4_0 \
  --n-gpu-layers 999 --n-cpu-moe 12 \
  --jinja --flash-attn on \
  --chat-template-kwargs '{"enable_thinking":false}' \
  --threads 6 --threads-batch 6 --threads-http 4 \
  > ~/orn-live.log 2>&1 &
```

> **Nota crítica:** El flag `--chat-template-kwargs '{"enable_thinking":false}'` NO sobrevive el parsing de systemd (bug conocido). Usar arranque directo desde terminal o configurar via `EnvironmentFile` en el servicio. Verificar con `curl localhost:8012/health` antes de usar.

---

## Parámetros de Inferencia (API)

```json
{
  "temperature": 0,
  "max_tokens": 1024,
  "stream": false
}
```

### Reglas críticas

| Parámetro | Valor | Por qué |
|---|---|---|
| `temperature` | **0** | Outputs determinísticos — los contratos JSON deben ser predecibles y reproducibles |
| `max_tokens` | **1024** | Suficiente para JSON compacto. T1=192 tok, T2=411 tok, T3=343 tok en validación |
| `thinking` | **OFF** — obligatorio | Thinking ON causa goal-completion bias: el modelo "termina" la tarea antes de completar el JSON y produce prosa. Con OFF: JSON limpio en 100% de los runs |
| `stream` | false | Ornstein produce contratos completos — no hay beneficio UX en streaming |

---

## System Prompts por Contrato

Ornstein tiene 4 modos de operación. Cada uno usa un system prompt específico.

### Modo 1 — AssetSpec3D (normalización de criatura)

```
You are Ornstein, a technical normalization layer. Your job is to convert creature descriptions into structured JSON. You do not narrate, explain, or add prose. Output ONLY valid JSON.
```

**Schema:**
```json
{
  "asset_id": "string",
  "height_m": "number",
  "limb_count": "integer",
  "surface_type": "string",
  "attack_mode": "string",
  "animation_hooks": ["string"],
  "material_profile": { "base": "string", "opacity": "string", "shader_hint": "string" },
  "spawn_conditions": ["string"]
}
```

### Modo 2 — Extracción de Entidades

```
You are Ornstein, a technical normalization layer. Your job is to extract canonical entities from raw lore text. Output ONLY a JSON array. No prose, no explanation.
```

**Schema por entidad:**
```json
{
  "id": "string (slug)",
  "name": "string",
  "type": "character | location | object | faction",
  "attributes": {},
  "first_appearance": "string"
}
```

### Modo 3 — InteractiveSceneSpec

```
You are Ornstein, a technical normalization layer. Convert narrative scenes into structured JSON specs for Unity MCP. Output ONLY valid JSON. No prose.
```

**Schema:**
```json
{
  "scene_id": "string",
  "location_id": "string",
  "characters": ["string"],
  "player_choices": [
    { "choice_id": "string", "label": "string", "requires_flag": "string | null", "sets_flag": "string | null" }
  ],
  "flags_set": ["string"],
  "triggers": [
    { "trigger_id": "string", "condition": "string", "action": "string" }
  ]
}
```

### Modo 4 — Entity State Manager (multi-turno)

```
You are Ornstein, a technical normalization layer. Maintain entity state across turns. Output ONLY valid JSON. The CANONICAL_STATE block below is the authoritative source of truth — it overrides the conversation history.
```

**Schema de entidad:**
```json
{
  "id": "string",
  "name": "string",
  "type": "string",
  "attributes": {},
  "first_appearance": "string",
  "last_updated_turn": "integer"
}
```

---

## Harness de Producción — Canonical State Pattern

Ornstein es un transformador técnico, no un gestor de estado. Para flujos multi-turno, el harness externo es la fuente de verdad. El modelo **nunca** tiene autoridad final sobre campos de estado determinísticos.

### Por qué es necesario

En T4 de validación, `last_updated_turn` retornó `2` en T3 porque el modelo interpretó el campo semánticamente ("no cambié nada, no incremento"). Este comportamiento es consistente pero incorrecto para el schema. Sin harness, el estado se corrompe silenciosamente en flujos largos.

### Componentes del harness

#### 1. Estado canónico externo

```python
canonical_state = {}  # dict en el harness, NO en el modelo

def init_entity(entity_data: dict) -> dict:
    """Inicializa una entidad en el estado canónico."""
    canonical_state[entity_data["id"]] = entity_data
    return entity_data

def update_entity(entity_id: str, new_attributes: dict, turn: int) -> dict:
    """Aplica nuevos atributos al estado canónico. El modelo no decide qué cambia."""
    if entity_id not in canonical_state:
        raise KeyError(f"Entity {entity_id} not registered")
    canonical_state[entity_id]["attributes"].update(new_attributes)
    canonical_state[entity_id]["last_updated_turn"] = turn
    return canonical_state[entity_id]

def get_entity(entity_id: str) -> dict:
    return canonical_state[entity_id]
```

#### 2. Inyección de CANONICAL_STATE en el prompt

Antes de cada turno, el harness inyecta el estado actual como bloque separado del historial:

```python
def build_prompt_with_state(user_message: str, entity_id: str) -> str:
    entity = get_entity(entity_id)
    canonical_block = f"""
CANONICAL_STATE (authoritative — overrides conversation history):
{json.dumps(entity, indent=2)}

---

{user_message}
"""
    return canonical_block
```

El system prompt debe incluir: `"The CANONICAL_STATE block is the authoritative source of truth — it overrides the conversation history."`

#### 3. Post-generation patcher

Antes de aceptar el output del modelo, el harness sobreescribe los campos determinísticos:

```python
def patch_output(model_output: dict, entity_id: str, turn: int) -> dict:
    """El modelo nunca tiene autoridad final sobre campos de estado."""
    canonical = get_entity(entity_id)
    # Tomar atributos del modelo (puede haber agregado campos nuevos)
    merged_attrs = {**canonical["attributes"], **model_output.get("attributes", {})}
    # Sobreescribir con estado canónico para campos críticos
    model_output["attributes"] = merged_attrs
    model_output["last_updated_turn"] = turn  # siempre el harness controla esto
    # Actualizar estado canónico
    canonical_state[entity_id] = model_output
    return model_output
```

#### 4. Extractor de JSON robusto

El modelo envuelve el JSON en bloques ` ```json ... ``` `. Siempre extraer antes de parsear:

```python
import re, json

def extract_json(text: str):
    text = text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]+?)```', text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)
```

### Flujo completo multi-turno (ejemplo)

```python
# Turno 1 — registro inicial
t1_response = call_ornstein([
    {"role": "system", "content": SYSTEM_PROMPT_MODE4},
    {"role": "user", "content": build_prompt_with_state(t1_user_msg, "cassian-vorne")}
])
entity = extract_json(t1_response)
entity = patch_output(entity, "cassian-vorne", turn=1)
init_entity(entity)
history.append({"role": "assistant", "content": json.dumps(entity)})

# Turno 2 — actualización
update_entity("cassian-vorne", {"former_role": "meridian_technician"}, turn=2)
t2_response = call_ornstein(history + [
    {"role": "user", "content": build_prompt_with_state(t2_user_msg, "cassian-vorne")}
])
entity = extract_json(t2_response)
entity = patch_output(entity, "cassian-vorne", turn=2)
history.append({"role": "assistant", "content": json.dumps(entity)})
```

---

## Tiempos de Respuesta Esperados

| Contrato | Tokens output aprox. | Tiempo aprox. |
|---|---|---|
| AssetSpec3D | ~150–250 | 4–7s |
| Extracción entidades (4–6) | ~350–500 | 8–14s |
| InteractiveSceneSpec | ~300–400 | 7–12s |
| Entity state (por turno) | ~100–150 | 3–5s |

---

## Restricciones

| Restricción | Detalle |
|---|---|
| Un modelo a la vez | RTX 3060 12GB — no compartir VRAM con SuperGemma/TrevorJS/ComfyUI |
| thinking OFF obligatorio | Con thinking ON el modelo produce prosa antes del JSON y falla en producción |
| Temperature 0 | No usar temperature > 0 para contratos — introduce variación no determinística |
| max_tokens 1024 | No necesita más — JSON compacto. Aumentar solo si los schemas crecen mucho |

---

## Runner de Validación

```bash
python3 ~/orn_runner.py t1   # AssetSpec3D
python3 ~/orn_runner.py t2   # Extracción de entidades
python3 ~/orn_runner.py t3   # InteractiveSceneSpec
python3 ~/orn_runner.py t4   # Multi-turno estado
```
