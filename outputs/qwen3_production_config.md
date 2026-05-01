# Config de Producción — Qwen3.6-35B-A3B

> Fecha de validación: 2026-05-01 (sesión 15)
> Referencia de resultados: `outputs/qwen3_validation_results.md`
> Hardware: NVIDIA RTX 3060 12GB | Intel i5-9600K | 32GB RAM | Debian Linux

---

## Modelo

| Campo | Valor |
|---|---|
| Archivo GGUF | `Qwen3.6-35B-A3B-Q4_K_M.gguf` |
| Ruta en servidor | `~/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf` |
| Alias | `qwen3-coder` |
| Arquitectura | qwen3_5_moe (MoE — 3B activos por token, 35B total) |
| Rol | Ingeniería y coding — scripts Python, AdonisJS, MCP tool use, razonamiento técnico largo |

---

## Comando de arranque (producción)

```bash
nohup ~/llama.cpp/build/bin/llama-server \
  --model ~/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf \
  --alias qwen3-coder \
  --host 0.0.0.0 --port 8013 \
  --ctx-size 40960 \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --flash-attn on \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --jinja \
  --threads 6 --threads-batch 24 \
  > ~/qwen3-live.log 2>&1 &
```

> **Puerto:** 8013 (Ornstein usa 8012 cuando está activo — nunca simultáneos, RTX 3060 12GB)
> **ctx-size:** 40960 necesario para dar margen a codegen largo (27k input + 5k output)
> **--n-cpu-moe 99:** todos los expertos MoE fríos a RAM — requiere 32GB RAM disponible

---

## Parámetros de inferencia por tarea

### Tareas determinísticas: extracción JSON, tool calls, MCP

```json
{
  "temperature": 0.1,
  "top_p": 0.80,
  "top_k": 20,
  "max_tokens": 2048,
  "chat_template_kwargs": {
    "enable_thinking": false,
    "preserve_thinking": false
  }
}
```

**Cuándo usar:** normalización de datos, extracción de entidades, tool calls de Unity MCP, cualquier tarea donde el output es JSON compacto y predecible.

**Por qué thinking=OFF:** 25x más rápido (1.9s vs 49s en 4k ctx) con accuracy idéntica. El razonamiento explícito no aporta para extracción directa.

---

### Tareas de razonamiento: codegen, debugging, arquitectura

```json
{
  "temperature": 0.3,
  "top_p": 0.95,
  "top_k": 20,
  "max_tokens": 5000,
  "chat_template_kwargs": {
    "enable_thinking": true,
    "preserve_thinking": false
  }
}
```

**Cuándo usar:** generación de scripts Python, implementación de endpoints AdonisJS, refactoring, cualquier tarea donde hay constraints técnicos a respetar.

**Por qué max_tokens=5000:** thinking consume ~2,000-3,000 tokens. Con menos tokens el código queda truncado.

---

### Tareas agentic multi-turn: flujos con tool results, estado entre turnos

```json
{
  "temperature": 0.2,
  "top_p": 0.95,
  "top_k": 20,
  "max_tokens": 2048,
  "chat_template_kwargs": {
    "enable_thinking": true,
    "preserve_thinking": true
  }
}
```

**Cuándo usar:** flujos de orquestación multi-paso con MCP Unity, cualquier conversación donde el modelo necesita mantener coherencia entre turnos con contexto largo.

**preserve_thinking=true:** recomendado por Qwen3 para flujos agentic — conserva el razonamiento histórico y mejora consistencia entre turnos.

---

## Reglas críticas

| Regla | Detalle |
|---|---|
| Un modelo a la vez | RTX 3060 12GB — no compartir VRAM con Ornstein / SuperGemma / TrevorJS / ComfyUI |
| Puerto 8013 | Ornstein corre en 8012. Nunca usar mismo puerto simultáneamente |
| thinking OFF para JSON | 25x speedup sin pérdida de accuracy en tareas de extracción |
| max_tokens≥5000 para codegen | thinking consume ~2-3k tokens; con menos el código se trunca |
| ctx-size 40960 | Margen para T3-tipo tasks donde input 27k + output 5k = 32k+ |

---

## Ventana de contexto validada

| ctx | T1 JSON | T2 MCP | T3 Codegen | T4 Multi-turn | Estado |
|---|---|---|---|---|---|
| 4k (1,150 tok) | ✅ 5/5 | ✅ 5/5 | ✅ 6/6 | ✅ 8/8 | CONFIABLE |
| 8k (5,775 tok) | ✅ 5/5 | ✅ 5/5 | ✅ 6/6 | ✅ 8/8 | CONFIABLE |
| 16k (13,072 tok) | ✅ 5/5 | ✅ 5/5 | ✅ 6/6 | ✅ 8/8 | CONFIABLE |
| 24k (20,358 tok) | ✅ 5/5 | ✅ 5/5 | ✅ 6/6 | ✅ 8/8 | CONFIABLE |
| 32k (27,696 tok) | ✅ 5/5 | ✅ 5/5 | ✅ 6/6 | ✅ 8/8 | CONFIABLE |

**ctx-size máximo confiable validado: 32k (27,696 tokens de input real).**
Límite teórico del modelo: 262,144 tokens. Límite práctico en esta GPU con estas flags: pendiente de validar más allá de 32k.

---

## Posición en el stack

| Modelo | Rol | Puerto | ctx |
|---|---|---|---|
| Ornstein (Gemma 4 26B) | Normalización JSON, contratos técnicos | 8012 | 24,576 |
| **Qwen3.6-35B-A3B** | **Ingeniería, codegen, MCP tool use** | **8013** | **40,960** |
| SuperGemma (Gemma 4 26B) | Escritura creativa uncensored | 8012 | 24,576 |
| TrevorJS (Gemma 4 26B) | Briefs técnicos 3D uncensored | 8012 | 24,576 |

Qwen3 no reemplaza ningún modelo actual — se añade como especialista en ingeniería y contexto largo.

---

## Runner de validación

```bash
python3 ~/qwen3_runner.py T1 32k qwen3-coder false   # extracción JSON
python3 ~/qwen3_runner.py T2 32k qwen3-coder false   # MCP tool call
python3 ~/qwen3_runner.py T3 32k qwen3-coder true    # codegen
python3 ~/qwen3_runner.py T4 32k qwen3-coder true    # multi-turn
```
