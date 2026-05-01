# Stories Index — Trabajo Pendiente

> Última actualización: 2026-04-30 (sesión 14)
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
| STORY_002 | ⬜ | MCP server — implementación FastMCP, 7 herramientas, puerto 8189 | STORY_001 |
| STORY_003 | ⬜ | Estructura ~/horror-game/ en servidor Debian | — |
| STORY_004 | 🔬 | Investigar Unity MCP — compatibilidad con pipeline local | — |

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
