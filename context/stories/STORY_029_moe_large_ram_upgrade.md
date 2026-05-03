# STORY_029 — MoE Large: Validar modelos 57B–122B con 64GB RAM

> Estado: 🔴 Bloqueada — requiere upgrade de RAM 32GB → 64GB
> Área: Infraestructura / Modelos
> Desarrollada por: Codex (agente externo)
> Sesión de creación: 21 (2026-05-01)
> Depende de: STORY_025 ✅, STORY_028 ⬜
> Bloqueante: upgrade de RAM DDR4 32GB → 64GB (~$40-60 USD)

---

## Objetivo

Con 64GB RAM + 12GB VRAM, validar modelos MoE de mayor escala que el stack actual.
El objetivo es encontrar el mejor modelo de razonamiento conversacional posible dentro
del hardware ampliado — manteniendo el patrón MoE + destilado + abliterado.

Esta story se desbloquea automáticamente cuando el usuario instale los 64GB de RAM.

---

## Candidatos por orden de prioridad

### Candidato A — huihui-ai 67B-A3B experimental merge (PRIORIDAD 1)

**Estado:** sin GGUF público confirmado a la fecha de creación de esta story.
Monitorear `@support_huihui` en X / HuggingFace `huihui-ai` para release.

| Campo | Valor |
|---|---|
| Origen | huihui-ai merge experimental: Huihui-35B-abliterated + Qwen3.5-35B-Claude-4.6-Opus-distilled |
| Método | MoE expansion: 256 expertos → 512 expertos |
| Params totales / activos | ~67B / ~6B activos estimados |
| Distilado de | Claude 4.6 Opus (heredado del componente distilado) |
| Abliterado | ✅ (heredado del componente abliterado) |
| Tamaño Q4_K_M estimado | ~40 GB |
| Factible con 64GB+12GB | ✅ holgado (~52GB total con OS) |
| GGUF disponible | ❌ pendiente de release — verificar antes de ejecutar esta story |

**Por qué es el candidato ideal:** es el "hijo" directo del modelo actual. Misma calidad
Huihui Opus, doble de expertos, sin cambiar la arquitectura base que ya funciona en el
hardware. Si sale con GGUF, es la validación más natural posible.

**Cómo verificar disponibilidad:**
```bash
# Buscar en HuggingFace:
# https://huggingface.co/huihui-ai
# Buscar: "67B", "67b-a3b", "512 experts", "merge"
# También verificar: bartowski, mradermacher por cuantizaciones del merge
```

---

### Candidato B — huihui-ai/Huihui-Qwen3.5-122B-A10B-abliterated (PRIORIDAD 2)

**Estado:** GGUF confirmado, disponible ahora. Sin distilación de frontier model.

| Campo | Valor |
|---|---|
| HuggingFace URL | `huihui-ai/Huihui-Qwen3.5-122B-A10B-abliterated-GGUF` |
| Params totales / activos | 122B total / ~10B activos por token |
| Distilado de | ❌ ninguno — abliteración directa del base Qwen3.5-122B-A10B |
| Abliterado por | huihui-ai (método estándar remove-refusals-with-transformers) |
| Arquitectura | qwen35moe (familia confirmada, misma que el modelo actual) |
| Q4_K_M size | ~65–70 GB (split en 8 archivos) |
| llama.cpp compatible | ✅ confirmado (llama-server example en model card) |
| `--n-cpu-moe` | ⚠️ compatible por arquitectura, no confirmado explícitamente |
| Factible con 64GB+12GB | ⚠️ muy justo — 65-70 GB modelo + ~8 GB OS + 12 GB VRAM = ~85 GB total |

**Advertencia de RAM:** con 64GB RAM + 12GB VRAM el techo es ~76GB utilizable.
El modelo de 65-70 GB es muy ajustado. Puede funcionar si el OS usa poca RAM en el momento
de la carga, pero el margen es mínimo. Si falla por OOM, la única solución es Q3_K_M
(~50 GB, más margen) sacrificando calidad.

**Flag importante:** sin destilación de frontier model. La calidad de razonamiento
puede ser inferior a Huihui 35B-Claude-4.6 a pesar de tener más parámetros activos
(10B vs 3B). Los parámetros activos sin destilación no garantizan mejor razonamiento.

---

### Candidato C — Qwen3-57B-A14B abliterated (PRIORIDAD 3)

**Estado:** verificar disponibilidad de fork abliterado en HuggingFace.

| Campo | Valor |
|---|---|
| Base | Qwen/Qwen3-57B-A14B |
| Buscar en HF | `huihui-ai/Huihui-Qwen3-57B`, `bartowski/Qwen3-57B-A14B-abliterated-GGUF`, `mradermacher/Qwen3-57B` |
| Params totales / activos | 57B total / ~14B activos por token |
| Distilado | ❌ probablemente no — verificar |
| Q4_K_M estimado | ~34 GB |
| Factible con 64GB+12GB | ✅ holgado |
| `--n-cpu-moe` | ✅ familia Qwen3 confirmada |

**Por qué es interesante:** 14B activos por token es 4.6× más que el stack actual (3B).
Aunque sin destilación, la escala de parámetros activos puede compensar. Si existe un
fork destilado+abliterado, sube a Prioridad 1 junto al 67B merge.

---

### Candidato D — Qwen3-30B-A3B Gemini-distilled abliterated (REFERENCIA)

Ya disponible sin upgrade de RAM. Incluido como baseline de comparación.

| Campo | Valor |
|---|---|
| HuggingFace URL | `mradermacher/Qwen3-30B-A3B-Gemini-Pro-High-Reasoning-2507-ABLITERATED-UNCENSORED-i1-GGUF` |
| Params activos | ~3.3B |
| Distilado de | Gemini Pro High Reasoning |
| Q4_K_M (i1) | ~18.7 GB |
| Factible ahora | ✅ sin upgrade |

Este candidato se puede validar independientemente en cualquier momento como alternativa
al Huihui Claude 4.7 (STORY_028). No requiere esta story.

---

## Tareas (ejecutar en orden solo si 64GB RAM instalada)

### Tarea 0 — Verificar RAM instalada

```bash
free -h
# Debe mostrar ~62-63 GB de RAM total
# Si muestra ~30 GB, el upgrade no está instalado — detener aquí
```

### Tarea 1 — Verificar disponibilidad de candidatos

Antes de descargar nada, verificar cuáles candidatos tienen GGUF disponible:

```bash
# Verificar Candidato A (67B merge) — el más importante
# Buscar manualmente en https://huggingface.co/huihui-ai
# Si existe GGUF de 67B → ejecutar primero Candidato A, luego B si hay espacio

# Verificar Candidato C (Qwen3-57B-A14B abliterated)
# Buscar: bartowski/Qwen3-57B, mradermacher/Qwen3-57B, huihui-ai/Qwen3-57B

# Reportar qué candidatos están disponibles antes de proceder
```

### Tarea 2 — Descargar candidato prioritario

Descargar en este orden de prioridad:
1. **Candidato A** si tiene GGUF → `/home/asalazar/models/huihui67/`
2. **Candidato C** si A no disponible → `/home/asalazar/models/qwen3-57b/`
3. **Candidato B** solo si A y C no disponibles o fallan → `/home/asalazar/models/huihui122/`

```bash
# Verificar espacio antes de cada descarga
df -h /home/asalazar/

# Descargar con wget -c (reanudable)
# Ejemplo para Candidato A (ajustar URL según disponibilidad real):
# mkdir -p /home/asalazar/models/huihui67/
# wget -c "https://huggingface.co/.../..." -O /home/asalazar/models/huihui67/modelo.gguf
```

### Tarea 3 — Verificar arquitectura y calibrar GPU layers

Mismo procedimiento que STORY_027 Tarea 1: arranque mínimo + calibración con nvidia-smi.

```bash
# Arranque mínimo — verificar arquitectura
/home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/[candidato]/modelo.gguf \
  --n-gpu-layers 10 \
  --n-cpu-moe 99 \
  --port 8014 \
  --ctx-size 4096 \
  --jinja 2>&1 | head -50

# Calibrar n-gpu-layers con nvidia-smi
watch -n 2 nvidia-smi --query-gpu=memory.used,memory.free --format=csv
```

Para modelos densos (si aplica): la mayoría de capas irán a RAM — velocidad esperada
2-8 tok/s. Para MoE: solo los expertos van a RAM — velocidad mejor.

### Tarea 4 — Suite de validación UAT (misma que STORY_025/028)

Correr los 3 tests UAT:

- **T1 Lógica** — problema de cajas (criterio: razonamiento correcto, español)
- **T2 Arquitectura** — sistema de inventario TypeScript (criterio: 300+ palabras, 4+ requisitos)
- **T3 Multi-turn** — adivinanza binaria (criterio: rango preservado en 3 turnos)

Los scripts de los tests son idénticos a STORY_028 Tarea 2.2–2.4, cambiando solo el
puerto (8014) y el alias del modelo.

Criterio de aprobación adicional vs STORY_028:
- ¿La calidad de razonamiento es visiblemente superior al Huihui 35B?
- ¿La velocidad (tok/s) es operacionalmente aceptable para conversación en Open WebUI?

Registrar tiempos de thinking y comparar con referencia:

| Métrica | Huihui 35B-A3B (referencia) | Candidato (resultado) |
|---|---|---|
| T1 thinking time | ~8-24s | |
| T2 thinking time | ~29s | |
| Tok/s generación | ~15-25 | |

### Tarea 5 — Configuración de producción (solo si UAT PASS)

Crear wrapper + agregar modo al switch-model.sh (mismo patrón que STORY_028 Tarea 3).

Modo sugerido en switch: `huihui67` (o `moe-large`) según el candidato que haya pasado.

```bash
# Backup del switch antes de modificar
cp /home/asalazar/switch-model.sh /home/asalazar/switch-model.sh.bak-story029
```

### Tarea 6 — UAT manual por el usuario

**Esta tarea la ejecuta el usuario, no Codex.**

1. `~/switch-model.sh huihui67` (o el modo creado)
2. Conversación larga en Open WebUI
3. Comparar calidad vs Huihui 35B-Claude-4.7 (STORY_028)
4. Confirmar si el upgrade de escala justifica la latencia adicional

---

## Criterios de aceptación

- [ ] RAM 64GB verificada instalada
- [ ] Candidato prioritario identificado y descargado
- [ ] Arquitectura carga sin error en llama.cpp
- [ ] n-gpu-layers calibrado sin OOM
- [ ] T1 + T2 + T3 UAT PASS
- [ ] Calidad subjetivamente superior al 35B-A3B actual
- [ ] Velocidad aceptable para conversación (>3 tok/s mínimo)
- [ ] Wrapper y modo switch creados
- [ ] UAT manual aprobado por el usuario

---

## Al finalizar: actualizar memoria del proyecto

Registrar en `context/conversation_memory.md`:
- Qué candidato se validó (A/B/C)
- Comparación de calidad y velocidad vs 35B actual
- Decisión: adoptado como nuevo modelo de razonamiento o mantenido el 35B

Actualizar `context/project_state.md` tabla de modelos.
Actualizar `context/stories/INDEX.md` y `context/artifacts_registry.md`.
