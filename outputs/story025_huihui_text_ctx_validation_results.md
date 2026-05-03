# STORY_025 — Huihui sin mmproj ctx validation results

> Fecha: 2026-05-02
> Servidor: `asalazar@10.1.0.105`
> Modelo: `Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf`
> Modo: texto puro, sin `--mmproj`
> Puerto de prueba: `8014`
> Estado final: 🔴 cerrado — falla objetivo de velocidad

---

## Resultado

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

---

## Arranque

Comando usado:

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
  --threads 6 --threads-batch 6 --threads-http 4
```

Evidencia de launch:

```text
llama_context: n_ctx         = 32768
llama_context: n_ctx_seq     = 32768
llama_kv_cache:      CUDA0 KV buffer size =   340.00 MiB
srv          init: init: chat template, thinking = 1
main: model loaded
main: server is listening on http://127.0.0.1:8014
```

Conclusión: la hipótesis de liberar VRAM quitando `mmproj` para arrancar a 32k se confirma.

---

## Resultados ejecutados

| Test | ctx | Resultado | Tiempo | Prompt tokens | Completion tokens | Reasoning |
|---|---:|---|---:|---:|---:|---|
| T1 JSON | 4k | PASS | 12.41s | 4,234 | 374 | presente |
| T1 JSON | 8k | PASS | 45.19s | 8,259 | 330 | presente |
| T1 JSON | 16k | PASS | 78.23s | 16,277 | 350 | presente |
| T1 JSON | 24k | PASS | 78.85s | 24,295 | 324 | presente |
| T1 JSON | 32k | PASS | 75.45s | 32,313 | 210 | presente |
| T2 MCP | 4k | PASS | 31.57s | 4,283 | 409 | presente |
| T2 MCP | 8k | PASS | 45.99s | 8,308 | 352 | presente |
| T2 MCP | 16k | PASS | 78.60s | 16,326 | 362 | presente |
| T2 MCP | 24k | PASS | 76.77s | 24,344 | 264 | presente |
| T2 MCP | 32k | PASS | 77.43s | 32,362 | 257 | presente |
| T3 Codegen | 4k | PASS | 40.80s | 4,284 | 686 | presente |

La suite estaba ejecutando `T3 8k` cuando se decidió cerrar la historia. Se detuvieron runner y servidor para no dejar procesos vivos.

---

## Comparación vs Qwen3.6

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
| Thinking ON | sí | sí | Conservado |

---

## Decisión

Huihui texto puro no se incorpora como servicio permanente `llama-huihui-text.service`.

Razón:

- Cumple arranque a 32k.
- Conserva thinking.
- Conserva precisión funcional en T1/T2 hasta 32k.
- Pero no cumple el goal de tokens/s idénticos o cercanos a los actuales.
- La caída estimada frente a Qwen3.6 es de 84.7% a 93.7% según cold/cache.

Rol recomendado:

- Mantener Huihui como backend de visión (`llama-vision.service`) y análisis multimodal.
- Mantener Qwen3.6 en puerto 8013 como modelo de ingeniería/codegen.
- No crear servicio texto permanente para Huihui salvo que se acepte un uso batch lento para razonamiento largo uncensored.

---

## Artefactos

- Runner: `outputs/huihui_text_runner.py`
- Log suite: `outputs/story025_suite.log`
- Log launch: `outputs/huihui_text_launch.log`
