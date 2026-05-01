# Especificación de Agentes Especializados y Memoria Atómica

> Versión: 1.0
> Fecha: 2026-04-30
> Story: STORY_016
> Basado en: context/agent_harness.md, context/validation_results_complete.md, outputs/workflow_map.md
> Input principal para: STORY_017 (Blueprint Compiler), STORY_018 (Plataforma de orquestación)

---

## 0. Premisa de Diseño

Un **agente** en este sistema no es solo un modelo LLM. Es la composición de cuatro componentes:

```
AGENTE = modelo LLM
       + harness (control de invocación, retries, format enforcement)
       + Memory Compiler (construye el artifact compilado para el prompt)
       + Canonical State Manager (fuente de verdad para estado de entidades)
```

El modelo produce texto. Los otros tres garantizan que ese texto sea correcto, estructurado y coherente con el estado real del mundo narrativo. La calidad del sistema depende del harness, no solo del modelo.

---

## 1. Roles del Sistema

La unidad de diseño es **(modelo, rol)** — no el modelo solo. Ornstein opera en múltiples roles con bloques de memoria distintos en cada uno.

| Rol ID | Modelo | Workflows | Output | Multi-turn | Confianza |
|---|---|---|---|---|---|
| `ornstein_normalizer` | Ornstein | WF-04, WF-08 | JSON puro | No | ✅ Validado (harness v2) |
| `ornstein_chapter_analyst` | Ornstein | WF-02 (post-escritura) | JSON (ChapterMemoryRecord) | No | ✅ Validado (N1–N5) |
| `ornstein_interactivity` | Ornstein | WF-07 | JSON (InteractiveSceneSpec, BranchGraphSpec) | No | ✅ Validado (W1–W5) |
| `ornstein_visual_spec` | Ornstein | WF-05, WF-06 (normalización) | JSON (AssetSpec3D, MaterialProfile) | No | ✅ Validado (V1–V4) |
| `supergemma_writer` | SuperGemma | WF-01, WF-02, WF-03 | Narrativa libre + JSON resumen | Sí | ⚠️ Preliminar — pending STORY_019 |
| `trevorjs_visual` | TrevorJS | WF-05 | Narrativa extrema (briefs gore) | Posible | ⚠️ Preliminar — pending STORY_019 |
| `engineer_session` | El Ingeniero | Todos (modo técnico) | Código, scripts, configs | No | — (agente censored, distinto) |
| `engineer_unity_exec` | El Ingeniero | WF-08 (ejecución Unity) | Comandos MCP | No | — (solo ve contratos normalizados) |

**Regla crítica:** El Ingeniero en modo `engineer_unity_exec` nunca recibe lore, prosa narrativa ni contenido de `prompt`/`negative_prompt`. Solo recibe: job contract JSON + memoria técnica mínima (infra, paths, puertos).

---

## 2. Bloques de Memoria Atómica

Cada bloque es una unidad compilable independiente. El Memory Compiler los ensambla según el rol y el workflow activo.

| Bloque | Contenido | Budget | Fuente |
|---|---|---|---|
| `IDENTITY` | Rol, modelo, restricciones absolutas | 100–200 tok | Fijo por rol |
| `OPERATING_RULES` | Thinking OFF, format enforcement, retry policy | 200–400 tok | `context/agent_harness.md` |
| `CANON_GLOBAL` | world_rules + premisa comprimida + glosario | 400–600 tok | `canon/world_rules.md` (comprimido) |
| `CANON_ENTITIES` | Fichas de entidades relevantes para la tarea | 500–2000 tok | `entities/<tipo>/<id>.md` (selección) |
| `CANON_CHAPTERS` | Resúmenes corto+medio de capítulos relevantes | 500–2000 tok | `chapter_summaries/<id>.json` |
| `ACTIVE_GOALS` | Tarea activa + objetivo + restricciones específicas | 100–300 tok | Runtime (construido por el harness) |
| `OPEN_LOOPS` | Retcons pendientes + reconciliaciones no cerradas | 200–500 tok | `canon/change_log.json` (filtrado) |
| `RECENT_DECISIONS` | Últimas 3–5 decisiones de canon que afectan la tarea | 200–400 tok | `conversation_memory.md` (filtrado) |
| `EXAMPLES` | 1–2 ejemplos de output correcto para format compliance | 300–700 tok | Fijo por rol — validados en harness |
| `CANONICAL_STATE` | Estado canónico de entidades (solo en multi-turn) | 200–600 tok | Canonical State Manager (runtime) |

---

## 3. Presupuestos de Tokens por Rol

ctx disponible: **24,576 tokens** con `Q4_K_M + --cache-type-k q4_0 --cache-type-v q4_0`.

**Regla de diseño:** No diseñar para el techo. El prefill a ctx≥20k toma ~31s. Para multi-turn: budget ≤ 12k. Para one-shot pesado: hasta 20k.

### 3.1 ornstein_normalizer (WF-04, WF-08)

```
IDENTITY              ~150 tok
OPERATING_RULES       ~300 tok
CANON_GLOBAL          ~500 tok
CANON_ENTITIES        ~800 tok   (solo entidades mencionadas en el input)
ACTIVE_GOALS          ~200 tok
OPEN_LOOPS            ~300 tok
EXAMPLES              ~500 tok   (1 ejemplo normalizer correcto)
────────────────────────────────
OVERHEAD TOTAL        ~2,750 tok

INPUT (texto a normalizar)   ~1,000–3,000 tok
OUTPUT (JSON normalizado)    ~300–800 tok
────────────────────────────────
TOTAL EN USO          ~4,000–6,500 tok   ✅ dentro de 12k
```

### 3.2 ornstein_chapter_analyst (WF-02 post-escritura)

```
IDENTITY              ~150 tok
OPERATING_RULES       ~300 tok
CANON_GLOBAL          ~500 tok
CANON_ENTITIES        ~1,500 tok  (personajes y locations del capítulo)
ACTIVE_GOALS          ~200 tok
OPEN_LOOPS            ~300 tok
RECENT_DECISIONS      ~400 tok
EXAMPLES              ~600 tok   (1 ejemplo ChapterMemoryRecord)
────────────────────────────────
OVERHEAD TOTAL        ~3,950 tok

INPUT (capítulo completo)    ~1,500–3,000 tok
OUTPUT (ChapterMemoryRecord) ~500–900 tok
────────────────────────────────
TOTAL EN USO          ~6,000–8,000 tok   ✅ dentro de 12k
```

### 3.3 ornstein_interactivity (WF-07)

One-shot pesado — carga el capítulo completo más entidades.

```
IDENTITY              ~150 tok
OPERATING_RULES       ~300 tok
CANON_GLOBAL          ~500 tok
CANON_ENTITIES        ~2,000 tok  (todos los personajes + locations de la escena)
CANON_CHAPTERS        ~1,500 tok  (resumen del capítulo anterior + capítulo activo)
ACTIVE_GOALS          ~250 tok
OPEN_LOOPS            ~400 tok
RECENT_DECISIONS      ~400 tok
EXAMPLES              ~700 tok   (1 ejemplo InteractiveSceneSpec completo)
────────────────────────────────
OVERHEAD TOTAL        ~6,200 tok

INPUT (capítulo fuente completo)     ~4,000–6,000 tok
OUTPUT (InteractiveSceneSpec + BranchGraph)  ~1,000–2,500 tok
────────────────────────────────
TOTAL EN USO          ~11,000–15,000 tok   ✅ dentro de 20k
```

### 3.4 ornstein_visual_spec (WF-05, WF-06)

```
IDENTITY              ~150 tok
OPERATING_RULES       ~300 tok
CANON_GLOBAL          ~400 tok   (mínimo — no necesita capítulos)
CANON_ENTITIES        ~600 tok   (whitelist de IDs técnicos disponibles)
ACTIVE_GOALS          ~200 tok
EXAMPLES              ~600 tok   (1 ejemplo AssetSpec3D correcto)
────────────────────────────────
OVERHEAD TOTAL        ~2,250 tok

INPUT (brief normalizado de TrevorJS/Vision)  ~500–1,500 tok
OUTPUT (AssetSpec3D / MaterialProfile)        ~400–800 tok
────────────────────────────────
TOTAL EN USO          ~3,000–4,500 tok   ✅ dentro de 12k
```

### 3.5 supergemma_writer (WF-01, WF-02) — ⚠️ PRELIMINAR

Multi-turn — budget conservador para no penalizar con prefill largo en cada turno.

```
IDENTITY              ~150 tok
OPERATING_RULES       ~250 tok   (adaptado a escritura narrativa, no JSON)
CANON_GLOBAL          ~600 tok
CANON_ENTITIES        ~1,200 tok (personajes y locations relevantes)
CANON_CHAPTERS        ~800 tok   (resumen capítulo anterior)
ACTIVE_GOALS          ~200 tok   (outline del capítulo + objetivo de sesión)
OPEN_LOOPS            ~300 tok
RECENT_DECISIONS      ~350 tok
CANONICAL_STATE       ~400 tok   (estado de entidades — inyectado por turno)
────────────────────────────────
OVERHEAD TOTAL        ~4,250 tok

INPUT por turno       ~300–600 tok
OUTPUT por turno      ~1,500–3,000 tok (escritura creativa)
────────────────────────────────
TOTAL TURNO 1         ~6,000–8,000 tok
TOTAL TURNO 3         ~9,000–12,000 tok  (historial acumulado)
TARGET: ≤ 12k en turno 3  ✅ viable
```

**Nota:** Si la sesión excede 3-4 turnos, el harness debe comprimir el historial o abrir nueva sesión. El Canonical State Manager reconstruye el estado desde el canonical dict, no del historial.

### 3.6 trevorjs_visual (WF-05) — ⚠️ PRELIMINAR

```
IDENTITY              ~150 tok
OPERATING_RULES       ~200 tok   (mínimo — modelo uncensored, restricciones solo de gameplay)
CANON_GLOBAL          ~300 tok   (mínimo — restricciones de silhouette y gameplay)
ACTIVE_GOALS          ~200 tok   (función narrativa + contexto de aparición)
────────────────────────────────
OVERHEAD TOTAL        ~850 tok

INPUT (brief de diseño de criatura)  ~400–800 tok
OUTPUT (brief grotesco libre)        ~1,000–3,000 tok
────────────────────────────────
TOTAL EN USO          ~2,000–4,500 tok   ✅ dentro de 12k
```

**Nota:** TrevorJS recibe el mínimo de canon deliberadamente. El brief grotesco no requiere coherencia interna profunda — su output siempre pasa por Ornstein antes de llegar a cualquier spec técnica.

---

## 4. Matriz Roles × Bloques

✅ = siempre presente | ○ = opcional/condicional | — = nunca

| Bloque | ornstein_normalizer | ornstein_chapter_analyst | ornstein_interactivity | ornstein_visual_spec | supergemma_writer | trevorjs_visual |
|---|---|---|---|---|---|---|
| IDENTITY | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OPERATING_RULES | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CANON_GLOBAL | ✅ | ✅ | ✅ | ○ (whitelist IDs) | ✅ | ○ (gameplay only) |
| CANON_ENTITIES | ○ (whitelist) | ✅ | ✅ | ✅ (IDs técnicos) | ✅ | — |
| CANON_CHAPTERS | — | — | ✅ | — | ✅ | — |
| ACTIVE_GOALS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OPEN_LOOPS | ✅ | ✅ | ✅ | — | ✅ | — |
| RECENT_DECISIONS | — | ✅ | ✅ | — | ✅ | — |
| EXAMPLES | ✅ | ✅ | ✅ | ✅ | — | — |
| CANONICAL_STATE | — | — | — | — | ✅ (por turno) | — |

---

## 5. Spec del Memory Compiler

El Memory Compiler es un script determinístico (no LLM) que produce el artifact compilado para el prompt. Inputs → proceso → output.

### 5.1 Inputs

```
compiler_input = {
  "role_id": "ornstein_interactivity",
  "workflow_id": "WF-07",
  "task_context": {
    "source_chapter": "ch_04",
    "target_scene": "hospital_b2_intro",
    "entities_involved": ["char_elena", "char_ivan", "loc_hospital_b2"],
    "active_retcons": ["change_2026_04_30_001"]
  },
  "canonical_state": {                    // solo si multi-turn
    "char_elena": {"has_radio": false, ...}
  }
}
```

### 5.2 Proceso

1. **Cargar plantilla del rol** — `templates/<role_id>.yaml` define qué bloques incluir y sus budgets.
2. **Resolver fuentes** — para cada bloque marcado como ✅/○:
   - `CANON_GLOBAL` → leer `canon/world_rules.md` (versión comprimida)
   - `CANON_ENTITIES` → leer `entities/<tipo>/<id>.md` para cada entidad en `entities_involved`
   - `CANON_CHAPTERS` → leer `chapter_summaries/<id>.json` (resumen corto si hay espacio, medio si hay margen)
   - `OPEN_LOOPS` → filtrar `canon/change_log.json` por `status: "pending_reconciliation"` y entidades relevantes
   - `RECENT_DECISIONS` → últimas 3–5 entradas de `conversation_memory.md` que mencionen entidades del task_context
   - `EXAMPLES` → cargar desde `templates/examples/<role_id>.json`
3. **Aplicar presupuesto** — si un bloque excede su budget, aplicar compresión de fuente (resumen corto en lugar de medio, top-N entidades por relevancia).
4. **Ensamblar artifact** — concatenar bloques en orden fijo:
   ```
   [IDENTITY]
   [OPERATING_RULES]
   [CANON_GLOBAL]
   [CANON_ENTITIES]
   [CANON_CHAPTERS]
   [ACTIVE_GOALS]
   [OPEN_LOOPS]
   [RECENT_DECISIONS]
   [CANONICAL_STATE]   ← solo si multi-turn
   [EXAMPLES]          ← siempre al final, cerca del input
   ```
5. **Validar budget total** — contar tokens del artifact. Si supera el budget del rol, eliminar bloques opcionales en orden inverso de prioridad.
6. **Retornar** — artifact como string (system prompt compilado) + metadata (tokens usados, bloques incluidos).

### 5.3 Output

```python
{
  "compiled_prompt": "<system prompt listo para enviar a llama-server>",
  "metadata": {
    "role_id": "ornstein_interactivity",
    "blocks_included": ["IDENTITY", "OPERATING_RULES", "CANON_GLOBAL", ...],
    "blocks_omitted": [],
    "total_tokens": 5843,
    "budget_used_pct": 94.4,
    "entities_resolved": ["char_elena", "char_ivan", "loc_hospital_b2"],
    "chapters_included": ["ch_04"]
  }
}
```

### 5.4 Responsabilidades que NO tiene el Memory Compiler

- No invoca al modelo LLM — solo prepara el prompt.
- No valida el output del modelo — eso es el harness.
- No mantiene estado canónico — eso es el Canonical State Manager.
- No decide qué entidades son relevantes más allá del `task_context` recibido — esa decisión la toma el orquestador antes de llamar al compiler.

---

## 6. Canonical State Manager

El Canonical State Manager vive en el harness. Es un dict Python simple + un reducer determinístico.

### 6.1 Cuándo activar

Solo en roles multi-turn con state tracking: actualmente `supergemma_writer`. En roles one-shot (todos los roles de Ornstein), no aplica — el estado se injeta en el input directamente.

### 6.2 Estructura

```python
# Estado inicial — construido por el harness al inicio de la sesión
canonical = {
    "char_elena": {
        "has_radio": True,
        "location": "loc_basement",
        "inventory": ["flashlight", "radio"],
        "revision": 0,
        "last_changed_turn": None
    },
    # ... otras entidades
}
```

### 6.3 Ciclo por turno

```
1. Memory Compiler inyecta CANONICAL_STATE en el prompt del turno N
2. Modelo responde
3. Harness extrae JSON del output (extract_json_robust)
4. Reducer evalúa: ¿el prompt de este turno especificó eventos determinísticos?
   - Si sí → reducer aplica independientemente del output del modelo
   - Si no → tomar el estado propuesto por el modelo (si es coherente)
5. Post-generation patcher sobreescribe entity_states[] con canonical
6. canonical["revision"] += 1, "last_changed_turn" = N
7. Ir al turno N+1 con canonical actualizado
```

### 6.4 Cuándo NO usar Canonical State

- Campos semánticos como `tone`, `change_type`, `emotional_beat` — el modelo debe inferirlos.
- Campos opcionales sin valor determinístico predefinido.

---

## 7. Configuración de Invocación por Rol

### 7.1 Flags llama.cpp (comunes a todos los roles de Ornstein)

```bash
# Cargar antes de cualquier rol Ornstein:
~/switch-model.sh ornstein

# Config runtime:
--ctx-size 24576
--cache-type-k q4_0
--cache-type-v q4_0
--n-gpu-layers 999
--n-cpu-moe 12
--flash-attn on
--jinja
--threads 6 --threads-batch 6 --threads-http 4
--chat-template-kwargs '{"enable_thinking":false}'   ← OBLIGATORIO para todos los roles estructurados
```

### 7.2 Parámetros de API por rol

| Rol | temperature | max_tokens | stream |
|---|---|---|---|
| ornstein_normalizer | 0 | 1500 | false |
| ornstein_chapter_analyst | 0 | 2000 | false |
| ornstein_interactivity | 0 | 3000 | false |
| ornstein_visual_spec | 0 | 1500 | false |
| supergemma_writer | 0.7 | 4000 | true (UX) |
| trevorjs_visual | 0.8 | 4000 | true (UX) |

**Nota:** temperature=0 para todos los roles agénticos con output estructurado. SuperGemma y TrevorJS usan temperatura alta porque su output es narrativa libre — la variabilidad es deseable.

### 7.3 Retry policy (validada en harness v2)

```python
RETRY_POLICY = {
    "ornstein_normalizer":      {"format_retries": 1, "on_failure": "log_and_skip"},
    "ornstein_chapter_analyst": {"format_retries": 1, "on_failure": "log_and_skip"},
    "ornstein_interactivity":   {"format_retries": 1, "on_failure": "log_and_skip"},
    "ornstein_visual_spec":     {"format_retries": 1, "on_failure": "log_and_skip"},
    "supergemma_writer":        {"format_retries": 0, "on_failure": "continue"},
    "trevorjs_visual":          {"format_retries": 0, "on_failure": "continue"},
}
# Nunca escalar más allá de 1 retry para roles estructurados.
# Si falla el segundo intento → fallo semántico, no de infraestructura.
```

---

## 8. Reglas de Invocación por Workflow

Qué rol invocar en cada workflow y qué bloques son obligatorios en ese contexto.

| Workflow | Rol | Bloques obligatorios adicionales | Budget target |
|---|---|---|---|
| WF-01 Ideación libre | supergemma_writer | CANON_GLOBAL, ACTIVE_GOALS | ≤ 8k |
| WF-02 Escritura capítulo | supergemma_writer | CANON_GLOBAL, CANON_ENTITIES, CANON_CHAPTERS, CANONICAL_STATE | ≤ 12k |
| WF-02 Normalización post-escritura | ornstein_chapter_analyst | CANON_GLOBAL, CANON_ENTITIES, RECENT_DECISIONS | ≤ 12k |
| WF-03 Reescritura | supergemma_writer o ornstein_chapter_analyst | CANON_CHAPTERS (capítulo anterior + actual) | ≤ 12k |
| WF-04 Extracción lore | ornstein_normalizer | CANON_GLOBAL, CANON_ENTITIES, OPEN_LOOPS | ≤ 8k |
| WF-05 Criaturas (TrevorJS) | trevorjs_visual | ACTIVE_GOALS (restricciones gameplay) | ≤ 6k |
| WF-05 Normalización (Ornstein) | ornstein_visual_spec | CANON_ENTITIES (whitelist IDs técnicos), EXAMPLES | ≤ 8k |
| WF-06 Referencias visuales (Vision) | — (Open WebUI, no harness) | — | — |
| WF-06 Normalización (Ornstein) | ornstein_visual_spec | CANON_GLOBAL, EXAMPLES | ≤ 6k |
| WF-07 Extracción interactividad | ornstein_interactivity | CANON_GLOBAL, CANON_ENTITIES, CANON_CHAPTERS, OPEN_LOOPS, EXAMPLES | ≤ 20k |
| WF-08 Normalización técnica | ornstein_normalizer u ornstein_visual_spec | según tipo de contrato | ≤ 8k |
| WF-09 Generación imágenes | engineer_unity_exec | job contract JSON únicamente | mínimo |

---

## 9. El Agente El Ingeniero — Dos Modos

### Modo Sesión (engineer_session)

Memoria completa del proyecto. Usado en sesiones de trabajo técnico (arquitectura, código, infra, debugging).

```
Carga en memoria:
  context/project_state.md
  context/agent_harness.md
  context/next_steps.md
  context/stories/INDEX.md
```

**Restricciones absolutas:** nunca lee `prompt`/`negative_prompt`. Nunca genera contenido creativo.

### Modo Ejecución Unity (engineer_unity_exec)

Memoria técnica mínima. Usado cuando El Ingeniero ejecuta un job contra Unity MCP.

```
Carga en memoria:
  job contract JSON (UnityPlacementJob o UnitySceneAssemblyJob)
  infra técnica: paths, puertos, modelo activo, estado de VRAM
```

**Nunca carga:** lore, capítulos, story bible, fichas de personajes, escenas narrativas.

**Invariante:** El orquestador (STORY_018) es responsable de construir el paquete de ejecución correcto — El Ingeniero no selecciona qué leer, recibe exactamente lo que necesita.

---

## 10. Ejemplos de Output Correcto (seed para EXAMPLES block)

Estos ejemplos son los que validaron score=4 en harness v2. Son el seed para el bloque EXAMPLES de cada rol.

### ornstein_normalizer — N1 (extracción de facts canónicos)

**Prompt de test:** Texto narrativo con 3 entidades mencionadas, una fuera de whitelist.
**Output correcto:**
```json
{
  "story_bible_entries": [
    {"fact_id": "lore.hospital.origin.001", "content": "El hospital fue construido sobre un antiguo ritual de purificación", "certainty": "confirmed", "source_refs": ["ch_01"]},
    {"fact_id": "lore.cult.001", "content": "El culto operaba desde los sótanos antes de 1943", "certainty": "implied", "source_refs": ["ch_01"]}
  ],
  "unknown_references": ["el_doctor_anónimo"],
  "ambiguities_to_keep": ["fecha exacta del primer ritual"],
  "status": "ok"
}
```

### ornstein_visual_spec — V2 (AssetSpec3D con IDs técnicos)

**Output correcto:**
```json
{
  "asset_id": "ast_creature_c03_alpha",
  "asset_type": "enemy",
  "material_profiles": ["mat_viscera_wet_v5", "mat_bone_dry_v2"],
  "rig_hooks": ["rig_spine_flex", "rig_jaw_detach"],
  "spawn_params": ["sp_hospital_b2", "sp_operating_room"],
  "fx_sockets": ["fx_blood_drip_01", "fx_steam_exhale"],
  "compatibility_issues": [],
  "status": "ok"
}
```

---

## 11. Limitaciones Conocidas

| Limitación | Descripción | Mitigación |
|---|---|---|
| W2 (multi-turn state) | El modelo puede perder estado de entidades entre turnos sin canonical injection | Canonical State Manager — mandatory para supergemma_writer |
| SuperGemma/TrevorJS sin validación | Specs preliminares sin evidencia empírica de scores | Pendiente STORY_019 — no usar en producción hasta validar |
| Prefill lento en ctx alto | ctx≥20k → ~31s en primera llamada | Usar 20k solo para WF-07 one-shot. Multi-turn ≤ 12k |
| Un modelo a la vez | RTX 3060 no permite dos modelos simultáneos | switch-model.sh es obligatorio antes de cada invocación |
| Memory Compiler no implementado | Este documento es la spec — la implementación es STORY_017 | No invocar agentes con bloques compilados hasta STORY_017 |

---

## 12. Dependencias y Próximos Pasos

| Paso | Story | Descripción |
|---|---|---|
| Implementar Memory Compiler | STORY_017 | Script Python ~150 líneas — produce compiled_prompt desde compiler_input |
| Validar SuperGemma/TrevorJS | STORY_019 | Re-descargar modelos, correr suite de 9 tests, confirmar specs o ajustar |
| System prompts por workflow | STORY_007 | Expandir OPERATING_RULES + IDENTITY de cada rol con prompts específicos por workflow |
| Plataforma de orquestación | STORY_018 | Scheduler, queue, switch-model.sh automático, notificaciones Artista-Ingeniero |
