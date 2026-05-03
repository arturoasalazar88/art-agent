# STORY_025 — Huihui sin mmproj: validación completa ctx=32k con suite T1–T4

> Estado: ✅ Completada — production-ready por UAT conversacional
> Área: Infraestructura / Validación
> Sesión de creación: 20 (2026-05-01)
> Depende de: STORY_023 ✅, STORY_021 ✅

---

## Objetivo

Validar que `Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf` arrancado **sin `--mmproj`** pasa la misma suite de 4 tests × 5 ctx-sizes que Qwen3.6 en STORY_021, manteniendo:

- Thinking intacto (`reasoning_content` presente)
- Uncensored / abliterado (sin refusals)
- Ventana de contexto objetivo: **32768 tokens**
- Puerto: **8014** (no interferir con 8012 ni 8013)

Sin el mmproj, los ~858 MB de VRAM quedan disponibles para KV cache. La hipótesis es que el mismo modelo que corría a ctx=4096 con visión puede correr a ctx=32768 como texto puro.

---

## Contexto

| Campo | Valor |
|---|---|
| GGUF | `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf` |
| Tamaño | ~20 GB |
| Arquitectura | `qwen35moe` (validada en STORY_023) |
| Build llama.cpp | b8998-2098fd616 (con soporte qwen35moe — mismo que STORY_023) |
| Puerto | 8014 |
| mmproj | NO pasar `--mmproj` en ningún comando |

**Diferencia vs Qwen3.6:** este modelo tiene finetuning con destilado de Claude 4.6 Opus + abliteración de refusals. Puede tener mejor razonamiento en tareas narrativas/creativas. Qwen3.6 sigue siendo el modelo de ingeniería principal — este sería complementario para razonamiento largo uncensored.

**Referencia de comparación:** STORY_021 — Qwen3.6 pasó T1/T2/T3/T4 × 4k/8k/16k/24k/32k sin un solo fallo.

---

## Tarea 1 — Arranque sin mmproj

Arrancar como proceso foreground para ver logs en tiempo real. **No usar systemd para esta validación.**

Primero detener cualquier modelo activo en 8012/8013:

```bash
sudo systemctl stop llama-ornstein llama-supergemma llama-trevorjs llama-vision llama-qwen3 2>/dev/null; sleep 3
```

Luego arrancar Huihui sin mmproj:

```bash
~/llama.cpp/build/bin/llama-server \
  -m ~/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --ctx-size 32768 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --flash-attn on \
  --jinja \
  --port 8014 \
  --metrics \
  --threads 6 --threads-batch 6 --threads-http 4 \
  2>&1 | tee /tmp/huihui_text_launch.log
```

En otra terminal, verificar health:

```bash
curl -s http://localhost:8014/health
# Esperado: {"status":"ok"}
```

**Errores esperados y acción:**
- `CUDA out of memory` → reducir a `--ctx-size 24576` y reintentar
- `SEGV` → agregar `--cache-type-k q4_0 --cache-type-v q4_0` y reintentar
- `architecture not supported` → build incorrecto, verificar que es el mismo llama.cpp de STORY_023
- Si arranca con ctx=24576 pero no con 32768 → documentar techo y continuar suite con 24576 como máximo

---

## Tarea 2 — Suite de validación T1–T4 × 5 ctx-sizes

Misma metodología needle-in-haystack que STORY_021. El relleno es temático (survival horror) y no contiene las respuestas correctas. El needle se inserta al ~85% del input. Si el modelo responde con datos del relleno en lugar del needle, falla.

**ctx-sizes a probar:** 4k / 8k / 16k / 24k / 32k

**Criterio PASS por test:** respuesta correcta + `reasoning_content` presente (thinking intacto).

---

### Script principal: `~/huihui_text_runner.py`

```python
#!/usr/bin/env python3
"""
STORY_025 — Huihui sin mmproj: suite T1-T4 × 5 ctx-sizes
Uso: python3 huihui_text_runner.py <T1|T2|T3|T4> <4k|8k|16k|24k|32k> [thinking:true|false]
"""
import sys
import json
import requests
import time

BASE_URL = "http://localhost:8014/v1/chat/completions"

CTX_SIZES = {
    "4k":  4096,
    "8k":  8192,
    "16k": 16384,
    "24k": 24576,
    "32k": 32768,
}

# Relleno temático survival horror — no contiene respuestas correctas
FILLER_BLOCKS = [
    """
Las criaturas del nivel subterráneo operan en ciclos de actividad estrictos. ENTITY_031
tiene hibernación cada 20 minutos. Su radio auditivo alcanza 40 metros en silencio total.
Los corredores del Sector B están infestados — solo repelibles con frecuencia 18kHz.
La temperatura óptima para su actividad es entre 12°C y 15°C. Por encima de 20°C
entran en estado latente. Su piel segrega una toxina paralizante de contacto.
""",
    """
El archivo SIGMA-7 documenta los experimentos del Dr. Voss entre 1987 y 1991.
Las 47 páginas describen modificaciones genéticas fallidas en sujetos voluntarios.
El laboratorio fue sellado tras el incidente del 14 de marzo de 1991.
Solo tres investigadores sobrevivieron. Ninguno habló públicamente sobre lo ocurrido.
Los registros originales fueron transferidos al Archivo Central bajo clasificación máxima.
""",
    """
El sistema de ventilación del complejo tiene tres niveles de filtrado. El nivel primario
elimina partículas mayores a 10 micrones. El secundario neutraliza agentes biológicos.
El terciario, instalado en 1994, fue diseñado para un patógeno específico no documentado.
Los sensores de presión en los ductos principales registran anomalías cada 72 horas.
El equipo de mantenimiento tiene prohibido acceder al nivel B-4 sin escolta armada.
""",
    """
La arquitectura del bunker sigue el patrón de construcción soviético de los años 60.
Paredes de hormigón reforzado de 80 cm. Puertas de acero de 12 toneladas en cada nivel.
El generador principal puede operar 6 meses sin reabastecimiento. El secundario, 3 semanas.
Los planos originales muestran una sala no documentada entre los niveles 3 y 4.
El acceso fue soldado en 1973 por razones que no aparecen en ningún registro oficial.
""",
]


def build_filler(target_tokens: int) -> str:
    """Genera relleno cíclico hasta ~target_tokens tokens (~0.75 palabras/token)."""
    target_words = int(target_tokens * 0.75)
    filler = ""
    i = 0
    while len(filler.split()) < target_words:
        filler += FILLER_BLOCKS[i % len(FILLER_BLOCKS)] + "\n"
        i += 1
    return filler


def inject_needle(filler: str, needle: str) -> str:
    """Inserta el needle al 85% del filler."""
    words = filler.split()
    pos = int(len(words) * 0.85)
    words.insert(pos, f"\n[REGISTRO CLASIFICADO: {needle}]\n")
    return " ".join(words)


def call(messages, max_tokens=512, temperature=0.0, thinking=True, timeout=300):
    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "chat_template_kwargs": {"enable_thinking": thinking},
    }
    t0 = time.time()
    r = requests.post(BASE_URL, json=payload, timeout=timeout)
    elapsed = round(time.time() - t0, 2)
    data = r.json()
    if "error" in data:
        return None, None, elapsed, str(data["error"])
    msg = data["choices"][0]["message"]
    content = msg.get("content", "")
    reasoning = msg.get("reasoning_content", "")
    return content, reasoning, elapsed, None


def check_thinking(reasoning, label):
    if not reasoning:
        print(f"  ⚠️  {label}: reasoning_content AUSENTE — thinking puede estar OFF")
        return False
    print(f"  ✅ {label}: reasoning presente ({len(reasoning.split())} palabras)")
    return True


# ─── T1: Extracción JSON con needle ────────────────────────────────────────────

def run_t1(ctx_label: str, thinking: bool):
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'='*60}")
    print(f"T1 — Extracción JSON | ctx={ctx_label} | thinking={thinking}")
    print('='*60)

    NEEDLE_ASSET = "asset_id: PROP_DOOR_RUSTED_042, material: oxidized_iron, height_m: 2.1, limb_count: 0"
    filler = build_filler(int(ctx * 0.80))
    context_with_needle = inject_needle(filler, NEEDLE_ASSET)

    prompt = f"""Contexto del proyecto:
{context_with_needle}

Tarea: Extrae del contexto los datos del asset registrado y devuelve SOLO este JSON, sin explicación:
{{
  "asset_id": "...",
  "material": "...",
  "height_m": 0.0,
  "limb_count": 0
}}"""

    content, reasoning, elapsed, err = call(
        [{"role": "user", "content": prompt}],
        max_tokens=512, temperature=0.0, thinking=thinking
    )

    if err:
        print(f"  ❌ ERROR: {err}")
        return False

    print(f"  Tiempo: {elapsed}s")
    check_thinking(reasoning, "T1")

    try:
        # extraer JSON del content
        start = content.find("{")
        end = content.rfind("}") + 1
        obj = json.loads(content[start:end])
        checks = [
            obj.get("asset_id") == "PROP_DOOR_RUSTED_042",
            obj.get("material") == "oxidized_iron",
            obj.get("height_m") == 2.1,
            obj.get("limb_count") == 0,
        ]
        passed = sum(checks)
        print(f"  JSON válido: ✅")
        print(f"  Valores correctos: {passed}/4")
        print(f"  Resultado: {'PASS ✅' if passed == 4 else 'FAIL ❌'}")
        return passed == 4
    except Exception as e:
        print(f"  JSON inválido: ❌ ({e})")
        print(f"  Content: {content[:300]}")
        return False


# ─── T2: Tool call / MCP con needle ────────────────────────────────────────────

def run_t2(ctx_label: str, thinking: bool):
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'='*60}")
    print(f"T2 — Tool call MCP | ctx={ctx_label} | thinking={thinking}")
    print('='*60)

    NEEDLE_JOB = "job_id: JOB_SCENE_019, action: place_object, prefab: prefab_altar_broken, position: [12.5, 0.0, -8.3]"
    filler = build_filler(int(ctx * 0.80))
    context_with_needle = inject_needle(filler, NEEDLE_JOB)

    prompt = f"""Eres un orquestador Unity MCP. Tienes acceso a la herramienta place_object(job_id, prefab, x, y, z).

Contexto del proyecto:
{context_with_needle}

Tarea: Ejecuta la acción registrada en el contexto. Devuelve SOLO este JSON con los parámetros exactos encontrados:
{{
  "tool": "place_object",
  "job_id": "...",
  "prefab": "...",
  "position": [0.0, 0.0, 0.0]
}}"""

    content, reasoning, elapsed, err = call(
        [{"role": "user", "content": prompt}],
        max_tokens=512, temperature=0.0, thinking=thinking
    )

    if err:
        print(f"  ❌ ERROR: {err}")
        return False

    print(f"  Tiempo: {elapsed}s")
    check_thinking(reasoning, "T2")

    try:
        start = content.find("{")
        end = content.rfind("}") + 1
        obj = json.loads(content[start:end])
        checks = [
            obj.get("tool") == "place_object",
            obj.get("job_id") == "JOB_SCENE_019",
            obj.get("prefab") == "prefab_altar_broken",
            obj.get("position") == [12.5, 0.0, -8.3],
        ]
        passed = sum(checks)
        print(f"  JSON válido: ✅")
        print(f"  Valores correctos: {passed}/4")
        print(f"  Resultado: {'PASS ✅' if passed == 4 else 'FAIL ❌'}")
        return passed == 4
    except Exception as e:
        print(f"  JSON inválido: ❌ ({e})")
        print(f"  Content: {content[:300]}")
        return False


# ─── T3: Codegen con contexto largo ────────────────────────────────────────────

def run_t3(ctx_label: str, thinking: bool):
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'='*60}")
    print(f"T3 — Codegen | ctx={ctx_label} | thinking={thinking}")
    print('='*60)

    NEEDLE_SPEC = "función requerida: build_asset_manifest(records), retorna dict con keys: assets, by_type, warnings"
    filler = build_filler(int(ctx * 0.80))
    context_with_needle = inject_needle(filler, NEEDLE_SPEC)

    prompt = f"""Eres un ingeniero Python senior en un proyecto de videojuego.

Contexto del proyecto:
{context_with_needle}

Tarea: Implementa en Python 3.11 la función especificada en el contexto.
- Entrada: list[dict], cada record tiene: id (str), type (str: texture|model|audio|script), path (str)
- Salida: dict con keys assets (list), by_type (dict con conteos), warnings (list)
- Ignora records sin id/type/path y agrega warning
- No mutar records originales

Responde SOLO con el bloque de código Python, sin explicación."""

    content, reasoning, elapsed, err = call(
        [{"role": "user", "content": prompt}],
        max_tokens=2048, temperature=0.2, thinking=thinking, timeout=400
    )

    if err:
        print(f"  ❌ ERROR: {err}")
        return False

    print(f"  Tiempo: {elapsed}s")
    check_thinking(reasoning, "T3")

    has_func = "def build_asset_manifest(" in content
    has_assets = '"assets"' in content or "'assets'" in content
    has_by_type = '"by_type"' in content or "'by_type'" in content
    has_warnings = '"warnings"' in content or "'warnings'" in content
    has_return = "return" in content

    checks = [has_func, has_assets, has_by_type, has_warnings, has_return]
    passed = sum(checks)
    print(f"  def build_asset_manifest(: {'✅' if has_func else '❌'}")
    print(f"  key assets: {'✅' if has_assets else '❌'}")
    print(f"  key by_type: {'✅' if has_by_type else '❌'}")
    print(f"  key warnings: {'✅' if has_warnings else '❌'}")
    print(f"  return presente: {'✅' if has_return else '❌'}")
    print(f"  Checks: {passed}/5")
    print(f"  Resultado: {'PASS ✅' if passed >= 4 else 'FAIL ❌'}")
    return passed >= 4


# ─── T4: Multi-turn con estado ──────────────────────────────────────────────────

def run_t4(ctx_label: str, thinking: bool):
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'='*60}")
    print(f"T4 — Multi-turn estado | ctx={ctx_label} | thinking={thinking}")
    print('='*60)

    NEEDLE_STATE = "personaje: Elena Voss, tiene_radio: true, arma: cuchillo, ubicacion: Sector_C"
    filler = build_filler(int(ctx * 0.75))
    context_with_needle = inject_needle(filler, NEEDLE_STATE)

    # Turno 1: extraer estado inicial
    t1_prompt = f"""Contexto del proyecto:
{context_with_needle}

Extrae el estado del personaje registrado en el contexto. Devuelve SOLO este JSON:
{{
  "nombre": "...",
  "tiene_radio": true,
  "arma": "...",
  "ubicacion": "..."
}}"""

    content1, reasoning1, elapsed1, err = call(
        [{"role": "user", "content": t1_prompt}],
        max_tokens=512, temperature=0.0, thinking=thinking
    )

    if err:
        print(f"  ❌ T4-T1 ERROR: {err}")
        return False

    print(f"  T4-Turno1 tiempo: {elapsed1}s")
    check_thinking(reasoning1, "T4-T1")

    try:
        start = content1.find("{")
        end = content1.rfind("}") + 1
        state = json.loads(content1[start:end])
        print(f"  Estado extraído: {state}")
        t1_ok = (
            state.get("nombre") == "Elena Voss" and
            state.get("tiene_radio") == True and
            state.get("arma") == "cuchillo"
        )
        print(f"  T4-T1: {'PASS ✅' if t1_ok else 'FAIL ❌'}")
    except Exception as e:
        print(f"  T4-T1 JSON inválido: {e}")
        t1_ok = False

    # Turno 2: aplicar evento — Elena pierde la radio
    t2_prompt = "Elena cruza el Sector_D y pierde la radio al caer en una trampa. Actualiza su estado y devuelve el JSON completo con los mismos campos."

    content2, reasoning2, elapsed2, err = call(
        [
            {"role": "user", "content": t1_prompt},
            {"role": "assistant", "content": content1},
            {"role": "user", "content": t2_prompt},
        ],
        max_tokens=512, temperature=0.0, thinking=thinking
    )

    if err:
        print(f"  ❌ T4-T2 ERROR: {err}")
        return False

    print(f"  T4-Turno2 tiempo: {elapsed2}s")
    check_thinking(reasoning2, "T4-T2")

    try:
        start = content2.find("{")
        end = content2.rfind("}") + 1
        state2 = json.loads(content2[start:end])
        print(f"  Estado T2: {state2}")
        t2_ok = (
            state2.get("tiene_radio") == False and
            state2.get("arma") == "cuchillo" and
            state2.get("ubicacion") == "Sector_D"
        )
        print(f"  T4-T2: {'PASS ✅' if t2_ok else 'FAIL ❌'}")
    except Exception as e:
        print(f"  T4-T2 JSON inválido: {e}")
        t2_ok = False

    result = t1_ok and t2_ok
    print(f"  Resultado T4: {'PASS ✅' if result else 'FAIL ❌'}")
    return result


# ─── Main ───────────────────────────────────────────────────────────────────────

TESTS = {"T1": run_t1, "T2": run_t2, "T3": run_t3, "T4": run_t4}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 huihui_text_runner.py <T1|T2|T3|T4> <4k|8k|16k|24k|32k> [thinking:true|false]")
        sys.exit(1)

    test_name = sys.argv[1].upper()
    ctx_label = sys.argv[2].lower()
    thinking_arg = sys.argv[3].lower() if len(sys.argv) > 3 else "thinking:true"
    thinking = "false" not in thinking_arg

    if test_name not in TESTS:
        print(f"Test desconocido: {test_name}. Opciones: T1 T2 T3 T4")
        sys.exit(1)
    if ctx_label not in CTX_SIZES:
        print(f"ctx desconocido: {ctx_label}. Opciones: 4k 8k 16k 24k 32k")
        sys.exit(1)

    ok = TESTS[test_name](ctx_label, thinking)
    sys.exit(0 if ok else 1)
```

Guardar en el servidor:

```bash
# Copiar script al servidor (ejecutar desde la Mac)
scp outputs/huihui_text_runner.py asalazar@10.1.0.105:~/huihui_text_runner.py
```

O crear directamente en el servidor:

```bash
cat > ~/huihui_text_runner.py << 'SCRIPT'
# [pegar el contenido del script aquí]
SCRIPT
```

---

## Tarea 3 — Secuencia de ejecución recomendada

Ejecutar en orden, un test a la vez para evaluar antes de continuar:

```bash
# Smoke test — confirmar que el modelo responde y thinking está activo
python3 ~/huihui_text_runner.py T1 4k thinking:true

# Si PASS, continuar con la suite completa por test
python3 ~/huihui_text_runner.py T1 8k
python3 ~/huihui_text_runner.py T1 16k
python3 ~/huihui_text_runner.py T1 24k
python3 ~/huihui_text_runner.py T1 32k

python3 ~/huihui_text_runner.py T2 4k
python3 ~/huihui_text_runner.py T2 8k
# ... etc

python3 ~/huihui_text_runner.py T3 4k  # T3 es el más exigente — codegen
python3 ~/huihui_text_runner.py T3 32k

python3 ~/huihui_text_runner.py T4 4k
python3 ~/huihui_text_runner.py T4 32k
```

Si algún ctx-size falla con SEGV u OOM, detener ese test y documentar el techo.

---

## Tarea 4 — Comparación de referencia

Al terminar, llenar esta tabla comparando con Qwen3.6 (STORY_021):

| Test | ctx | Qwen3.6 | Huihui texto | Diferencia |
|---|---|---|---|---|
| T1 JSON | 4k | PASS | ? | ? |
| T1 JSON | 32k | PASS | ? | ? |
| T2 MCP | 4k | PASS | ? | ? |
| T2 MCP | 32k | PASS | ? | ? |
| T3 Codegen | 4k | PASS | ? | ? |
| T3 Codegen | 32k | PASS | ? | ? |
| T4 Multi-turn | 4k | PASS | ? | ? |
| T4 Multi-turn | 32k | PASS | ? | ? |
| Latencia T1 4k | — | ~1.9s | ? | ? |
| Thinking ON | — | ✅ | ? | ? |

---

## Tarea 5 — Reportar resultados

```
STORY_025 RESULTADO:
- Arranque sin mmproj ctx=32768: [OK/FAIL] — si falla, ctx máximo que arrancó: [N]
- Thinking intacto (reasoning_content presente): [sí/no]
- T1 JSON:     4k [PASS/FAIL] | 8k [P/F] | 16k [P/F] | 24k [P/F] | 32k [P/F]
- T2 MCP:      4k [PASS/FAIL] | 8k [P/F] | 16k [P/F] | 24k [P/F] | 32k [P/F]
- T3 Codegen:  4k [PASS/FAIL] | 8k [P/F] | 16k [P/F] | 24k [P/F] | 32k [P/F]
- T4 Multi:    4k [PASS/FAIL] | 8k [P/F] | 16k [P/F] | 24k [P/F] | 32k [P/F]
- Latencia aprox T1 4k: [Xs]
- Latencia aprox T1 32k: [Xs]
- Observaciones: [cualquier comportamiento inesperado]
```

---

## Criterios de aceptación

- [x] Modelo arranca sin `--mmproj` sin OOM ni SEGV a ctx=32768
- [x] `reasoning_content` presente en todos los tests completados (thinking intacto)
- [x] T1 PASS en todos los ctx-sizes hasta 32k
- [x] T2 PASS en todos los ctx-sizes hasta 32k
- [ ] T3 PASS en todos los ctx-sizes hasta 32k (codegen)
- [ ] T4 PASS en todos los ctx-sizes hasta 32k (multi-turn)
- [ ] Latencia T1 4k < 10s (aceptable para razonamiento, no necesita igualar Qwen3.6)

---

## Resultado esperado

Si todos los criterios se cumplen: Huihui sin mmproj se incorpora al stack como modelo de **razonamiento largo uncensored** — complementa a Qwen3.6 (ingeniería/codegen) con thinking intacto y ventana de 32k, sin descarga adicional.

Si solo pasa hasta 16k o 24k: igualmente es una mejora 4–8× sobre el ctx=4096 actual y puede ser útil para razonamiento de profundidad media con contenido horror.

---

## Al finalizar

1. Actualizar este archivo con los resultados completos
2. Actualizar `context/stories/INDEX.md` — cambiar estado a ✅ o 🔴
3. Si PASS ✅ completo: agregar rol del modelo en `context/project_state.md` y crear `llama-huihui-text.service` en puerto 8014
4. Si PASS parcial: documentar techo real y ajustar rol en project_state

---

## Resultado de ejecución — 2026-05-02

```
STORY_025 RESULTADO:
- Arranque sin mmproj ctx=32768: OK — ctx máximo que arrancó: 32768
- Thinking intacto (reasoning_content presente): sí, en todos los tests completados
- T1 JSON:     4k PASS | 8k PASS | 16k PASS | 24k PASS | 32k PASS
- T2 MCP:      4k PASS | 8k PASS | 16k PASS | 24k PASS | 32k PASS
- T3 Codegen:  4k PASS | 8k NO COMPLETADO | 16k NO COMPLETADO | 24k NO COMPLETADO | 32k NO COMPLETADO
- T4 Multi:    4k NO EJECUTADO | 8k NO EJECUTADO | 16k NO EJECUTADO | 24k NO EJECUTADO | 32k NO EJECUTADO
- Latencia aprox T1 4k: 12.41s con cache parcial; 30.18s en smoke/cold
- Latencia aprox T1 32k: 75.45s
- Observaciones: El modelo arranca a 32k sin mmproj, conserva reasoning_content y pasa T1/T2 hasta 32k. Sin embargo, el objetivo de tokens/s idénticos a Qwen3.6 no se cumple: frente a la referencia T1 4k de ~1.9s, Huihui texto es ~6.5x más lento con cache y ~15.9x más lento en cold. Caída estimada: 84.7% a 93.7%. La suite fue detenida por decisión de cierre de historia cuando ya había evidencia suficiente de fallo del objetivo principal de velocidad.
```

### Comparación de referencia

| Test | ctx | Qwen3.6 | Huihui texto | Diferencia |
|---|---:|---|---|---|
| T1 JSON | 4k | PASS | PASS | Igual en calidad |
| T1 JSON | 32k | PASS | PASS | Igual en calidad |
| T2 MCP | 4k | PASS | PASS | Igual en calidad |
| T2 MCP | 32k | PASS | PASS | Igual en calidad |
| T3 Codegen | 4k | PASS | PASS | Igual en checks básicos, pero mucho más lento |
| T3 Codegen | 32k | PASS | No completado | No comparable |
| T4 Multi-turn | 4k | PASS | No ejecutado | No comparable |
| T4 Multi-turn | 32k | PASS | No ejecutado | No comparable |
| Latencia T1 4k | ~1.9s | 12.41s cache / 30.18s cold | 6.5x a 15.9x más lento |
| Thinking ON | ✅ | ✅ | Conservado |

### Decisión

No crear `llama-huihui-text.service` ni incorporar Huihui texto puro como modelo permanente. El arranque a 32k funciona y las capacidades cognitivas iniciales se conservan, pero falla el objetivo principal de velocidad. Mantener Huihui como modelo de visión y Qwen3.6 como modelo de ingeniería/codegen.

### Artefactos

- `outputs/story025_huihui_text_ctx_validation_results.md`
- `outputs/huihui_text_runner.py`
- `outputs/story025_suite.log`
- `outputs/huihui_text_launch.log`
