# Stories Index — Trabajo Pendiente

> Última actualización: 2026-05-02 (sesión 21)
> Trigger: Cada vez que se crea, actualiza o cierra una story.
> Formato individual: `context/stories/STORY_XXX_nombre.md`

## Leyenda
⬜ pendiente | 🟡 en progreso | 🔴 bloqueada | 🔬 research | ✅ completada | 🚫 cancelada

---

## Plataforma & Agentes

| ID | Estado | Título | Depende de |
|---|---|---|---|
| STORY_016 | ✅ | Diseño de agentes especializados + memoria atómica | STORY_001 |
| STORY_017 | ⬜ | Blueprint Compiler — Ornstein → SceneBlueprint sin arte | STORY_016 |
| STORY_018 | ⬜ | Plataforma de orquestación — arquitectura general | STORY_001, STORY_016 |

---

## Infraestructura

| ID | Estado | Título | Depende de |
|---|---|---|---|
| STORY_001 | ✅ | Validación modelos Ornstein — usabilidad, estabilidad, capacidad agéntica (4 bloques) | — |
| STORY_019 | ✅ | Validación modelos creativos — SuperGemma y TrevorJS (4 tests cualitativos, 4/4 PASS a ctx=24576) | STORY_001 |
| STORY_020 | ✅ | Agent Harness — sistema de reglas por rol + re-run 14 tests con harness | STORY_001 |
| STORY_021 | ✅ | Validación Qwen3.6-35B-A3B — ctx=32k, 4 tests × 5 sizes, PASS perfecto | STORY_001 |
| STORY_022 | ✅ | Servicios systemd completos: fix Ornstein thinking + crear qwen3 + reescribir switch-model.sh; vision bloqueado por falta de GGUF/mmproj | STORY_001, STORY_021 |
| STORY_023 | ✅ | Validación Huihui-Qwen3.5-35B-A3B: no reemplaza Qwen3.6 en ingeniería; adoptado como Vision vía mmproj | STORY_021, STORY_022 |
| STORY_024 | ✅ | Activar Vision en Open WebUI — superado por STORY_027. SuperGemma4 Vision adoptado y validado. Huihui Vision eliminado. | STORY_023, STORY_027 |
| STORY_027 | ✅ | Vision Upgrade — SuperGemma4-26B-abliterated-multimodal adoptado. UAT PASS. Thinking OFF (llama.cpp b8998 limitación). | STORY_023 ✅ |
| STORY_028 | ✅ | Huihui Claude 4.7 "Sage" — UAT 5/5 PASS. Adoptado como `sage` en switch-model.sh (puerto 8012, ctx=32768). Pendiente: eliminar Qwen3 si usuario confirma. | STORY_025 ✅ |
| STORY_029 | 🔴 | MoE Large (57B–122B) — validar modelos de mayor escala con 64GB RAM | RAM 64GB |
| STORY_025 | ✅ | Huihui sin mmproj ctx=32768: T1/T2 PASS, UAT-3 conversacional PASS — production-ready para razonamiento (velocidad UAT aceptable) | STORY_023 |
| STORY_002 | ⬜ | MCP server — implementación FastMCP, 7 herramientas, puerto 8189 | STORY_001 |
| STORY_003 | ⬜ | Estructura ~/horror-game/ en servidor Debian | — |
| STORY_004 | 🔬 | Investigar Unity MCP — compatibilidad con pipeline local | — |
| STORY_026 | ✅ | Open WebUI: Web Search (SearXNG) activado y validado en UAT — RAG de URL pendiente verificar | — |

---

## Pipeline Creativo

| ID | Estado | Título | Depende de |
|---|---|---|---|
| STORY_005 | 🟡 | Estética base del juego — vision + imágenes de referencia | — |
| STORY_006 | 🟡 | Afinar LoRA strengths por tipo de asset | — |
| STORY_007 | ⬜ | System prompts por modelo adaptados a horror workflow | STORY_001 |
| STORY_008 | ⬜ | Pipeline automatizado LLM → ComfyUI | STORY_002 |
| STORY_009 | ⬜ | Workflow storyboard con style lock en ComfyUI | — |
| STORY_010 | ⬜ | IPAdapter en ComfyUI para consistencia de personajes | — |
| STORY_011 | ⬜ | Script batch generation storyboard via API ComfyUI | STORY_008 |

---

## Game Development

| ID | Estado | Título | Depende de |
|---|---|---|---|
| STORY_012 | ⬜ | Estructura base Unity — escena inicial, player controller | STORY_004 |
| STORY_013 | ⬜ | Fichas de personaje con Ornstein | — |

---

## Housekeeping

| ID | Estado | Título | Depende de |
|---|---|---|---|
| STORY_014 | ⬜ | Autenticación --api-key en llama-server | — |
| STORY_015 | ⬜ | Hardware upgrade P40/3090 | [presupuesto] |
