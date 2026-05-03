---
id: STORY_015
title: Hardware upgrade P40/3090
status: pending
priority: low
created: 2026-04-26
updated: 2026-05-02
depends_on: "[presupuesto]"
---

# STORY_015 — Hardware Upgrade

Upgrade de hardware para superar las limitaciones actuales de VRAM (12GB) que impiden correr LLM + ComfyUI simultáneamente y limitan el ctx-size máximo.

---

## Objetivo

Seleccionar e implementar el upgrade de hardware más costo-efectivo según el presupuesto disponible. Hay dos dimensiones independientes: RAM (bajo costo, alto impacto en MoE) y GPU (mayor costo, desbloquea uso simultáneo).

---

## Opciones de upgrade

### Opción A — RAM 32→64GB DDR4 (PRIORITARIO)
- **Costo:** ~$40–60 USD (dos módulos DDR4 SO-DIMM o DIMM según slot disponible)
- **Beneficio:** Desbloquea STORY_029 — modelos MoE 57B–122B con --n-cpu-moe 99
- **Sin riesgo de incompatibilidad** — solo agregar RAM al mismo tipo/velocidad
- **Resultado:** Qwen3-57B-A14B viable (14B activos/token vs 3B actuales)

### Opción B — GPU adicional Tesla P40 24GB + Z390-A
- **Costo:** ~$310–470 USD (P40 $80-150 + Z390-A $150-200 + cooler $20-40 + fuente $60-80 si necesario)
- **Beneficio:** 36GB VRAM total, LLM + ComfyUI simultáneos, ctx=32768+ para modelos densos
- **Riesgo:** B365M-A actual es incompatible (D24) — cambio de motherboard obligatorio
- **Complejidad:** Alta — reinstalación SO o migración

### Opción C — GPU RTX 3090 24GB (reemplaza 3060)
- **Costo:** ~$600–800 USD segunda mano
- **Beneficio:** 24GB VRAM, arquitectura Ampere (mejor que P40 Pascal), sin cambio de MB
- **Resultado:** ctx=32768 con modelos densos, ComfyUI de alta resolución
- **Limitación:** Solo 24GB (P40+3060=36GB, pero más complejo)

---

## Prioridad de implementación

1. **RAM primero** — mínimo costo, máximo impacto inmediato, sin riesgo de compatibilidad
2. **P40/3090 después** — cuando haya presupuesto y tiempo para la migración

---

## Criterios de aceptación (RAM)

- [ ] 64GB RAM instalados y reconocidos por el sistema (`free -h` muestra ~62GB)
- [ ] STORY_029 desbloqueada — Qwen3-57B-A14B o equivalente cargable
- [ ] Ningún servicio existente degradado

## Criterios de aceptación (GPU, cuando aplique)

- [ ] Segunda GPU reconocida por CUDA (`nvidia-smi` muestra dos GPUs)
- [ ] llama.cpp configurado con `--tensor-split` para distribuir capas
- [ ] LLM + ComfyUI corriendo simultáneamente sin OOM
- [ ] Velocidad de inferencia medida y comparada con baseline actual

---

## Notas

- Verificar tipo de RAM del servidor antes de comprar: `sudo dmidecode -t memory`
- Para P40: requiere adaptador activo de refrigeración (el P40 no tiene cooler propio)
- Para Z390-A: verificar compatibilidad con i5-9600K (socket LGA1151 — compatible)
