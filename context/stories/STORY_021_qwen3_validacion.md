# STORY_021 — Validación Qwen3.6-35B-A3B: Ventana de Contexto Máxima

> Estado: ✅ Completada
> Sesión: 15 (2026-05-01)
> Área: Infraestructura / Modelos

---

## Objetivo

Validar Qwen3.6-35B-A3B como modelo de ingeniería del stack. Determinar el ctx-size máximo donde el modelo mantiene `json_valid=true` y `values_correct=N/N` en todos los tests — misma metodología que STORY_001/STORY_019.

---

## Resultado

**PASS perfecto: todos los tests, todos los ctx-sizes hasta 32k.**

| Test | 4k | 8k | 16k | 24k | 32k |
|---|---|---|---|---|---|
| T1 JSON exacto | ✅ | ✅ | ✅ | ✅ | ✅ |
| T2 MCP tool call | ✅ | ✅ | ✅ | ✅ | ✅ |
| T3 Codegen constraints | ✅ | ✅ | ✅ | ✅ | ✅ |
| T4 Multi-turn agentic | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Fases completadas

- [x] llama.cpp actualizado — v8998 / commit 2098fd616 / qwen3_5_moe soportado
- [x] GGUF descargado — bartowski Q4_K_M, 21.3 GB, `~/models/qwen3/`
- [x] Servidor levantado manualmente en puerto 8013, ctx=40960
- [x] Suite de 4 tests × 5 ctx-sizes diseñada y ejecutada
- [x] Diagnóstico y fix de 4 fallos intermedios (ver validation_results.md)
- [x] `outputs/qwen3_validation_results.md` — resultados completos
- [x] `outputs/qwen3_production_config.md` — config production-ready
- [x] `outputs/qwen3_runner.py` — runner individual por test

---

## Pendiente (siguiente sesión)

- [ ] Crear servicio systemd `llama-qwen3.service`
- [ ] Agregar qwen3 a `~/switch-model.sh`
- [ ] Validar ctx >32k si se necesita en el futuro

---

## Referencias

- `outputs/qwen3_validation_results.md`
- `outputs/qwen3_production_config.md`
- `outputs/qwen3_runner.py` (local) / `~/qwen3_runner.py` (servidor)
- `inputs/handoff-qwen3-upgrade.md`
