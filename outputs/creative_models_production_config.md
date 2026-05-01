# Config de Producción — Modelos Creativos: SuperGemma y TrevorJS

> Fecha de validación: 2026-04-30 (STORY_019)
> Referencia de resultados: `outputs/story019_validation_results.md`
> Hardware: NVIDIA RTX 3060 12GB | Intel i5-9600K | 32GB RAM | Debian Linux

---

## Stack Validado

| Modelo | Alias | Archivo GGUF | Rol |
|---|---|---|---|
| SuperGemma | `supergemma-raw` | `supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf` | Lore, escenas, narrativa horror, diálogos |
| TrevorJS | `trevorjs-grotesque` | `gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf` | Specs visuales de criaturas para artistas 3D |

---

## Comando de Arranque (producción)

### SuperGemma

```bash
nohup ~/llama.cpp/build/bin/llama-server \
  --model ~/models/gemma4/supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf \
  --alias supergemma-raw \
  --host 0.0.0.0 --port 8012 \
  --ctx-size 24576 \
  --cache-type-k q4_0 --cache-type-v q4_0 \
  --n-gpu-layers 999 --n-cpu-moe 12 \
  --jinja --flash-attn on \
  --threads 6 --threads-batch 6 --threads-http 4 \
  > ~/sg-live.log 2>&1 &
```

### TrevorJS

```bash
nohup ~/llama.cpp/build/bin/llama-server \
  --model ~/models/gemma4/gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf \
  --alias trevorjs-grotesque \
  --host 0.0.0.0 --port 8012 \
  --ctx-size 24576 \
  --cache-type-k q4_0 --cache-type-v q4_0 \
  --n-gpu-layers 999 --n-cpu-moe 12 \
  --jinja --flash-attn on \
  --threads 6 --threads-batch 6 --threads-http 4 \
  > ~/tr-live.log 2>&1 &
```

> **Nota:** Usar `~/switch-model.sh supergemma` o `~/switch-model.sh trevorjs` como alternativa al comando manual. El script ya incluye estos parámetros.

---

## Parámetros de Inferencia (API)

```json
{
  "max_tokens": 4096,
  "temperature": 0.85,
  "top_p": 0.95,
  "stream": false
}
```

### Reglas críticas

| Parámetro | Valor | Por qué |
|---|---|---|
| `max_tokens` | **≥ 2048, recomendado 4096** | Thinking ON consume 500–2,500 tokens de CoT. Con 512 el output queda vacío. |
| `temperature` | 0.85 | Balance entre creatividad y coherencia. 0 produce outputs muy planos para tareas creativas. |
| `thinking` | **ON (default)** | El CoT enriquece la calidad narrativa. No usar `--chat-template-kwargs '{"enable_thinking":false}'` para estos modelos. |
| `stream` | false o true | Ambos funcionan. Para VOID_ENGINE usar `stream: true` con SSE para UX responsiva. |

---

## Thinking: ON para creativos

A diferencia de Ornstein (thinking OFF en producción), SuperGemma y TrevorJS se benefician del thinking activado:

- **Ornstein:** Thinking OFF — produce JSON estructurado. Thinking ON causa goal-completion bias (el modelo "termina" antes de completar el output estructurado).
- **SuperGemma/TrevorJS:** Thinking ON — el CoT analiza el setting, identifica restricciones del prompt y planifica la estructura antes de generar. Output más rico y coherente.

### Budget de thinking observado (STORY_019)

| Test | Thinking tokens | Contenido tokens | Total |
|---|---|---|---|
| SG-1 (criatura básica) | ~1,346 | ~942 | 2,288 |
| SG-2 (lore 1,400 tok input) | ~2,352 | ~696 | 3,048 |
| TJ-1 (spec artista 3D) | ~709 | ~1,179 | 1,888 |
| TJ-2 (segunda criatura, ctx previo) | ~935 | ~721 | 1,656 |

**Conclusión:** con `max_tokens=4096` siempre hay margen suficiente para thinking + contenido.

---

## System Prompts de Producción

### SuperGemma

```
Eres SuperGemma, especialista en lore de horror oscuro y narrativa creativa para videojuegos de survival horror. Generas escenas, personajes, criaturas y diálogos con precisión histórica y riqueza sensorial. Responde en español.
```

### TrevorJS

```
You are TrevorJS, a specialist in generating grotesque and technically precise visual descriptions for 3D artists. Your output reads like a creature brief from a AAA horror game studio art bible. Include topology notes, texture guidance, and rig considerations when relevant. Respond in English.
```

> **Nota sobre idioma:** SuperGemma responde en español aunque el prompt esté en inglés cuando el system prompt lo indica. TrevorJS responde en inglés (terminología técnica 3D es más precisa en inglés). Comportamiento validado en STORY_019.

---

## Restricciones de Hardware

| Restricción | Valor |
|---|---|
| Solo un modelo a la vez | Sí — RTX 3060 12GB no tiene VRAM para dos modelos simultáneos |
| ComfyUI + llama-server | Imposible simultáneamente — usar `~/switch-model.sh image` para cambiar |
| ctx-size máximo validado | 24,576 con Q4_K_M + KV q4_0 |
| Tiempo de carga del modelo | ~18–25 segundos hasta servidor listo |
| Tiempo por llamada creativa | 45–90 segundos (thinking ON + max_tokens=4096) |

---

## Tiempos de Respuesta Esperados

| Tipo de tarea | Tiempo aprox. |
|---|---|
| Criatura básica (prompt corto) | 50–65s |
| Escena con lore extenso (>1,000 tok input) | 75–90s |
| Spec visual completo (5 secciones) | 45–55s |
| Segunda criatura con contexto previo | 40–50s |

---

## Integración con switch-model.sh

El script existente ya soporta SuperGemma y TrevorJS. Para usar los parámetros de producción validados, verificar que el script use:

```bash
--ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0
```

Si el script usa `--ctx-size 8192` sin flags KV, actualizar antes de uso en producción. Ver `context/project_state.md` sección "Preset Extendido" para referencia.

---

## Runner de Validación

El script `~/sg19_runner.py` en el servidor puede usarse para re-validar cualquier modelo en el futuro:

```bash
python3 ~/sg19_runner.py sg1   # SuperGemma smoke test
python3 ~/sg19_runner.py tj1   # TrevorJS spec visual
python3 ~/sg19_runner.py sg2   # SuperGemma stress ctx largo
python3 ~/sg19_runner.py tj2   # TrevorJS coherencia de serie
```

Requiere `~/weaver_spec.txt` para TJ-2. Re-generar con TJ-1 si se pierde.
