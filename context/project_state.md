# Estado del Proyecto — Survival Horror Video Game

> Última actualización: 2026-05-01
> Trigger de actualización: Solo cuando equipo, alcance o metodología cambian.

---

## Proyecto

| Campo | Valor |
|---|---|
| Nombre | Survival Horror Video Game |
| Estudio | DArkkercornner Studios |
| Tipo | Videojuego survival horror — Unity + Unity MCP + Blender |
| Director | Arturo Salazar |
| Inicio | Abril 2026 |
| Fase actual | Pre-producción — infraestructura validada, agentes diseñados, plataforma VOID_ENGINE en construcción |

### Objetivo Estratégico

Construir un videojuego de survival horror con un pipeline de producción completamente local: LLMs para escritura creativa y prompts, ComfyUI para generación de assets 2D, Blender para modelado 3D, y Unity como motor del juego. Unity MCP actúa como capa de ensamblaje interactivo (gestión de assets, escenas, scripts y GameObjects desde un agente). El pipeline separa estrictamente las responsabilidades creativas (humano + modelos uncensored) de las técnicas (agentes de IA censored).

---

## Equipo y Roles

### Arturo Salazar — Director / Artista
- Toma todas las decisiones creativas
- Usa Open WebUI + llama-server para interactuar con modelos locales
- Define historia, estética, personajes, escenas
- Genera prompts visuales con modelos uncensored

### El Ingeniero — Agente IA (Claude Code / OpenCode / Gemini CLI / Codex)
- Ejecución técnica exclusivamente
- Arquitectura del juego, Unity + Unity MCP, pipeline Blender
- Orquestación de MCP y ComfyUI
- NUNCA genera contenido creativo (lore, prompts gore, historia)
- NUNCA lee campos `prompt` o `negative_prompt` de archivos JSON

### Modelos Locales LLM — Actores Creativos

| Alias | Modelo GGUF | Servicio systemd | Rol | Thinking |
|---|---|---|---|---|
| Ornstein | Ornstein-26B-A4B-it-Q4_K_M.gguf | llama-ornstein | Estructura narrativa, prompts limpios, briefs técnicos, fichas 3D | ❌ OFF (forzado via wrapper) |
| SuperGemma | supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf | llama-supergemma | Ideación libre, escenas crudas, diálogo oscuro, lore, criaturas | ✅ ON |
| TrevorJS | gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf | llama-trevorjs | Grotesco visual, horror corporal, prompts visuales extremos | ✅ ON |
| supergemma4-vision | supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf + mmproj-f16 | llama-vision | Análisis visual art direction — composición, paleta, iluminación, texturas, mood. Validado en sesión 22 (STORY_027). | ❌ OFF (llama.cpp b8998 no parsea channel markers de Gemma 4 multimodal) |
| Qwen3 | Qwen3.6-35B-A3B-Q4_K_M.gguf (MoE, 3B activos/token) | llama-qwen3 ✅ | Ingeniería: codegen, tool calls MCP, orquestación VOID_ENGINE (pipeline encadenado, JSON rápido) | ✅ ON (codegen) / ❌ OFF (JSON/tool calls) |
| Sage | Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q4_K_M.gguf (MoE, 3B activos/token) | llama-huihui47 ✅ | Razonamiento conversacional uncensored — diseño de sistemas, análisis narrativo, decisiones de arquitectura, multi-turn largo en Open WebUI. ctx=32768. | ✅ ON (min max_tokens=3000) |

### ComfyUI — Generación de Imágenes
- Checkpoint: Pony Diffusion V6 XL
- VAE: sdxl_vae.safetensors (mejora colores y sombras vs integrado)
- LoRAs: horror_style (0.7), gore_details (0.5), dark_fantasy_arch (0.4)
- Resolución: 1024×1024, 25 steps, CFG 7, sampler euler

---

## Infraestructura

### Host Principal — Servidor Debian

| Componente | Detalle |
|---|---|
| SO | Debian Linux |
| GPU | NVIDIA RTX 3060 12 GB GDDR6 (KO V2 OC Edition) |
| CPU | Intel Core i5-9600K, 3.7 GHz, 6 núcleos |
| RAM | 32 GB |
| Acceso | SSH: `asalazar@10.1.0.105` |
| Runtime LLM | llama.cpp server |
| Disco | 218 GB total, ~84 GB libres |

### Servicios

| Servicio | URL | Puerto | Estado |
|---|---|---|---|
| llama-server (creativos + visión) | `http://10.1.0.105:8012` | 8012 | ✅ Operativo (Ornstein/SuperGemma/TrevorJS/supergemma4-vision) |
| llama-server (ingeniería) | `http://10.1.0.105:8013` | 8013 | ✅ Operativo — Qwen3.6-35B-A3B vía llama-qwen3.service |
| Open WebUI | `http://10.1.0.105:3000` | 3000 | ✅ Operativo (Docker) |
| ComfyUI | `http://10.1.0.105:8188` | 8188 | ✅ Operativo (systemd) |
| SearXNG | `http://10.1.0.105:8080` | 8080 | ✅ Operativo (Docker, --restart unless-stopped) |
| MCP server | `http://10.1.0.105:8189` | 8189 | ⬜ Pendiente implementación |
| VOID_ENGINE | `localhost:3333` (dev) | 3333 | 🔧 En diseño — plataforma web de orquestación |

### Switch de Modos

```bash
~/switch-model.sh ornstein    # LLM estructura y briefs (thinking=OFF via wrapper)
~/switch-model.sh supergemma  # LLM creatividad horror crudo
~/switch-model.sh trevorjs    # LLM grotesco visual uncensored
~/switch-model.sh vision      # SuperGemma4 Vision multimodal (con mmproj, ctx=8192, thinking OFF)
~/switch-model.sh sage        # Sage (Huihui 4.7) — razonamiento conversacional uncensored, ctx=32768
~/switch-model.sh qwen3       # LLM ingeniería — codegen, MCP, orquestación (puerto 8013)
~/switch-model.sh image       # ComfyUI generación de imágenes
~/switch-model.sh             # muestra estado actual de todos los servicios
```

### Preset Base LLM (todos los servicios)

```
--ctx-size 8192 --n-gpu-layers 999 --n-cpu-moe 12 --flash-attn on --jinja
--metrics --slots --slot-save-path ~/llama-slots --threads 6 --threads-batch 6 --threads-http 4
```

### Preset Extendido — ctx=24576 (validado 2026-04-29)

```
--ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0
--n-gpu-layers 999 --n-cpu-moe 12 --flash-attn on --jinja
--metrics --slots --slot-save-path ~/llama-slots --threads 6 --threads-batch 6 --threads-http 4
```

> Requiere `--cache-type-k q4_0 --cache-type-v q4_0` para que el KV cache quepa en VRAM.
> Sin esos flags, SEGV a partir de ctx > 8192.

### Preset Qwen3 — ctx=40960 (validado 2026-05-01, STORY_021)

```
--ctx-size 40960 --cache-type-k q8_0 --cache-type-v q8_0
--n-gpu-layers 99 --n-cpu-moe 99 --flash-attn on --jinja
--port 8013 --metrics --slots --slot-save-path ~/llama-slots --threads 6 --threads-batch 6 --threads-http 4
```

> Modelo: `~/models/qwen3/Qwen3-235B-A22B-Q4_K_M.gguf` (o variante local)
> `--n-cpu-moe 99`: expertos MoE se ejecutan en RAM — permite 35B+ en 12GB GPU
> `--cache-type-k q8_0 --cache-type-v q8_0`: KV cache comprimido para 40k ctx en 12GB

### Preset Vision (SuperGemma4 Vision)

```
--ctx-size 8192 --n-gpu-layers 999 --n-cpu-moe 12 --override-tensor ".*=CPU"
--flash-attn on --jinja --chat-template-kwargs '{"enable_thinking":false}'
```

Nota: `--override-tensor ".*=CPU"` fuerza el mmproj a RAM (igual que Huihui Vision). Thinking OFF obligatorio — llama.cpp b8998 no parsea los channel markers de Gemma 4 multimodal y los emite como `|` en el output. Desde sesión 22, el backend activo de `llama-vision.service` es SuperGemma4 Vision.

### Rutas Importantes en Servidor

| Ruta | Contenido |
|---|---|
| `~/llama.cpp/build/bin/llama-server` | Binario llama.cpp |
| `~/models/gemma4/` | Modelos LLM (Ornstein, SuperGemma, TrevorJS) |
| `~/models/qwen3/` | Modelo Qwen3 (ingeniería/codegen) |
| `~/models/huihui47/` | Sage — Huihui Claude 4.7 Q4_K_M (21.3 GB) |
| `~/models/supergemma4-vision/` | SuperGemma4 Vision — GGUF Q4_K_M + mmproj F16 + chat_template.jinja |
| `~/ComfyUI/` | Entorno ComfyUI completo |
| `~/ComfyUI/models/checkpoints/` | Pony Diffusion V6 XL |
| `~/ComfyUI/models/vae/` | sdxl_vae.safetensors |
| `~/ComfyUI/models/loras/` | horror_style, gore_details, dark_fantasy_arch |
| `~/ComfyUI/workflows/` | Workflows JSON (pony_horror.json, pony_horror_lora.json) |
| `~/switch-model.sh` | Script de cambio de modelo |
| `~/llama-slots/` | Directorio de slots guardados |

### Servicios systemd

| Servicio | Archivo |
|---|---|
| llama-ornstein | `/etc/systemd/system/llama-ornstein.service` |
| llama-supergemma | `/etc/systemd/system/llama-supergemma.service` |
| llama-trevorjs | `/etc/systemd/system/llama-trevorjs.service` |
| llama-vision | `/etc/systemd/system/llama-vision.service` — SuperGemma4 Vision (validado sesión 22) |
| llama-qwen3 | `/etc/systemd/system/llama-qwen3.service` — ✅ creado en STORY_022 |
| llama-huihui47 | `/etc/systemd/system/llama-huihui47.service` — ✅ creado en STORY_028. Alias `sage` en switch-model.sh |
| comfyui | `/etc/systemd/system/comfyui.service` |

---

### Upgrade Hardware Pendiente (cuando haya presupuesto)

| Componente | Detalle | Costo estimado |
|---|---|---|
| Motherboard | ASUS Prime Z390-A LGA1151 | ~$150-200 USD segunda mano |
| GPU adicional | Tesla P40 24GB (datacenter) | ~$80-150 USD segunda mano |
| Cooler P40 | Adaptador activo obligatorio | ~$20-40 USD |
| Fuente | 750W+ si necesario | ~$60-80 USD |
| **Total** | **P40 + Z390-A** | **$310-470 USD** |

Resultado del upgrade: 36GB VRAM total, ctx-size 32768+, LLM + ComfyUI simultáneos, ~100-140 tok/s.

Alternativa superior: RTX 3090 24GB (~$600-800 USD) + mantener 3060 = misma VRAM pero arquitectura Ampere+Ampere, sin problemas de enfriamiento, más rápida.

**Bloqueante actual:** B365M-A es mATX con chipset B365 — solo 1 slot PCIe x16 eléctrico. Requiere cambio de motherboard obligatorio para dual GPU.

---

## Riesgos Activos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| VRAM al límite | 🔴 Alta | Usar presets validados (ctx=24576 KV-q4_0 para Gemma4, ctx=40960 KV-q8_0 para Qwen3). Ver sección Presets. Monitorear con `journalctl`. |
| Puerto único compartido (8012) | 🟡 Media | Solo un modelo activo a la vez. `switch-model.sh` previene conflictos. |
| Restart loop en SEGV | 🟡 Media | Servicios tienen `Restart=on-failure`. Monitorear con `journalctl -u llama-X -f`. |
| ComfyUI + llama-server simultáneos | 🔴 Alta | Imposible — RTX 3060 no tiene VRAM para ambos. Switch obligatorio. |
| Build llama.cpp sin SSL | 🟡 Media | No puede descargar imágenes por HTTPS. Usar base64 o Open WebUI para visión. |

---

## Restricciones de Hardware Validadas

| Parámetro | Límite | Consecuencia si excede |
|---|---|---|
| ctx-size con Q4_K_M | 8192 sin flags extra | SEGV — KV cache no cabe en VRAM |
| ctx-size con Q4_K_M + KV q4_0 (Gemma4) | **24576 validado** (STORY_001) | PASS en 3 configs; techo real >24576 sin probar |
| ctx-size Qwen3 MoE + KV q8_0 | **40960 validado** (STORY_021) | PASS T1-T4 × 4k-32k; --n-cpu-moe 99 obligatorio |
| ctx-size con Q3_K_M | ~16384 estimado | No validado — omitido, Q4_K_M+KV ya lo supera |
| `--n-cpu-moe` | 12 mínimo | Valores menores causan fallos de memoria |
| VRAM libre con modelo cargado | ~27 MB | No cabe mmproj en GPU — forzar a CPU |
| Vision ctx-size | 4096 | Reducido para liberar VRAM para mmproj |

### Tokens en 8192 (referencia)

| Contenido | Tokens aprox. |
|---|---|
| 1 página de texto normal | ~500 |
| Escena de guion detallada | ~800–1200 |
| Brief técnico 3D completo | ~600–900 |
| Conversación larga | ~2000–3000 |
| Guion de nivel completo | ~4000–6000 |

---

## Metodologías

### Separación Artista / Ingeniero
La regla fundamental del proyecto. El contenido creativo (lore, prompts, gore) lo generan los modelos locales uncensored. La ejecución técnica (código, pipelines, MCP, ComfyUI) la maneja el agente ingeniero. Los dos nunca se mezclan. Ver `/protocols.operational` en CLAUDE.md.

### Context Engineering
Agente con memoria persistente basada en archivos. Memoria separada en estable (`project_state.md`) y volátil (`next_steps.md`). Decisiones comprimidas en `conversation_memory.md`. Artefactos registrados en `artifacts_registry.md`. Skills de sesión para automatizar carga y guardado.

### VOID_ENGINE Design Workflow
La plataforma VOID_ENGINE se diseña desde guías propias y se implementa directamente en código. Los mocks generales generados con Gemini/Stitch quedan deprecados como fuente de verdad porque no respetan copy, workflows ni estructura exacta. Las pantallas se diseñan on demand usando `outputs/void_engine_layout_guide.md` y `outputs/void_engine_ui_ux_guide.md`; Stitch/Gemini puede usarse solo como exploración visual no vinculante.

### Pipeline de 5 Fases
1. **Novelización mutable** — SuperGemma genera fragmentos crudos; Ornstein estructura capítulos y canon
2. **Consolidación de canon** — story_bible, fichas, timeline, change_log; Ornstein como normalizador
3. **Extracción de interactividad** — Ornstein convierte capítulos aprobados en flags, choices, branches
4. **Generación de assets** — TrevorJS/Vision producen material; Ornstein traduce a specs técnicas (AssetSpec3D, CreatureVariantCard, etc.)
5. **Orquestación Unity** — contratos estructurados → Unity MCP → escenas, GameObjects, scripts en editor

### Regla de Separación Semántica
El orquestador técnico (Unity MCP) nunca recibe horror explícito en lenguaje natural. Solo recibe contratos normalizados: IDs, perfiles de material, flags, animation_hooks. Ornstein es la capa de traducción entre creación local y montaje técnico.

### Sistema de Memoria por Capas
- **Global**: premisa, tono, reglas del mundo, glosario — siempre comprimida en contexto
- **Semántica**: personajes, lugares, criaturas, facciones — retrieval por entidad
- **Episódica**: resúmenes de capítulos y escenas — retrieval por capítulo/acto
- **Trabajo**: objetivo actual, escena activa — temporal, siempre presente
- **Cambios**: retcons, ajustes, impacto pendiente — solo cuando aplica

### Tipos de Cambio Narrativo
- **Expansión**: agrega detalle sin alterar hechos canónicos
- **Ajuste local**: modifica escena o capítulo sin impacto estructural amplio
- **Retcon**: cambia hechos canónicos, obliga a reconciliar otras piezas

### Formatos de Handoff Definidos
| Formato | Origen | Descripción |
|---|---|---|
| `StoryBibleEntry` | Ornstein | Entrada canónica con hechos, entidades, tono, estado |
| `ChapterMemoryRecord` | Ornstein | Capítulo: resumen corto/medio, hechos, riesgos de continuidad |
| `InteractiveSceneSpec` | Ornstein | Escena interactiva: flags, choices, convergencias, audio, luz |
| `BranchGraphSpec` | Ornstein | Grafo de bifurcaciones, fusiones y condiciones de arco |
| `EncounterFlow` | Ornstein | Flujo de encuentro con jugador |
| `PlayerGoalMap` | Ornstein | Mapa de objetivos del jugador por escena |
| `NarrativeTriggerMap` | Ornstein | Triggers narrativos por evento |
| `AssetSpec3D` | Ornstein | Spec técnica: material, animaciones, spawn, prefab target Unity |
| `CreatureVariantCard` | Ornstein (de TrevorJS) | Ficha de criatura: variantes, materiales, spawn, animaciones |
| `MaterialProfile` | Ornstein (de TrevorJS) | Perfil de material y texturas |
| `ArtDirectionBrief` | Ornstein (de Vision) | Brief de dirección de arte desde análisis de referencia |
| `LightingProfile` | Ornstein (de Vision) | Perfil de iluminación extraído de referencias |
| `CameraMoodProfile` | Ornstein (de Vision) | Perfil de cámara y mood visual |
| `TextureReferenceCard` | Ornstein (de Vision) | Tarjeta de referencia de texturas |
| `UnityPlacementJob` | Ornstein | Job de ensamblaje: lista de acciones MCP para Unity Editor |
| `UnitySceneAssemblyJob` | Ornstein | Job completo de ensamblaje de escena en Unity |

### Trazabilidad Obligatoria (campos mínimos en todo artefacto)
```json
{
  "source_model": "SuperGemma",
  "normalized_by": "Ornstein",
  "source_refs": ["ch_04", "creatures.c03"],
  "change_log_refs": ["change_YYYY_MM_DD_NNN"],
  "unity_job_refs": ["job_scene_XXX"]
}
```

### Estructura de Directorios en Servidor (objetivo)
```
~/horror-game/
  canon/
    story_bible.md / world_rules.md / timeline.md
    canon_index.json / change_log.json
  chapters/          ch_01.md, ch_02.md...
  chapter_summaries/ ch_01.json, ch_02.json...
  entities/
    characters/ / locations/ / factions/ / creatures/
  scene_specs/       <scene_id>.json
  branch_graphs/     <arc_id>.json
  assets/            <asset_id>.json
  jobs/unity/        <job_id>.json
  validation/        reconciliation_report.json...
  refs/images/       referencias visuales
```

### Secuencias Diarias Operativas
- **Día de novelización**: SuperGemma → borrador → Ornstein → canon + memorias
- **Día de criaturas**: TrevorJS → brief extremo → Vision (si hay refs) → Ornstein → AssetSpec3D
- **Día de adaptación interactiva**: capítulo aprobado → Ornstein → InteractiveSceneSpec → UnityPlacementJob → orquestador → Unity MCP → validación

> Spec de alto nivel: `inputs/spec-workflow-creativo-orquestador-memoria.md`
> Workflows operativos detallados: `inputs/handoff-workflows-detallados-llms-orquestador.md`

---

## Glosario

| Término | Definición |
|---|---|
| Ornstein | Modelo LLM Gemma 4 26B para estructura y briefs técnicos |
| SuperGemma | Modelo LLM uncensored para ideación horror cruda |
| TrevorJS | Modelo LLM uncensored para grotesco visual |
| Sage | Modelo LLM razonamiento conversacional uncensored — Huihui Claude 4.7 (Qwen3.6-35B-A3B destilado de Opus 4.7, abliterado). Switch: `sage`, puerto 8012, ctx=32768 |
| Huihui Vision | Modelo multimodal para análisis de imágenes, activo en `llama-vision.service` |
| Pony Diffusion | Checkpoint SDXL para generación de imágenes en ComfyUI |
| LoRA | Adaptador de bajo rango — modifica estilo del modelo base |
| mmproj | Vision encoder — archivo separado que habilita procesamiento de imágenes |
| abliterated | Modelo al que se le removieron pesos de rechazo (uncensored) |
| Qwen3 | Modelo LLM MoE Qwen3.6-35B-A3B — rol de ingeniería en el stack |
| MoE | Mixture of Experts — arquitectura donde solo parte de los parámetros se activan |
| KV cache | Caché de key-value en VRAM — determina el tamaño de contexto posible |
| ctx-size | Tamaño de ventana de contexto en tokens |
| Q4_K_M | Cuantización de 4 bits — balance entre calidad y tamaño |
| Q3_K_M | Cuantización de 3 bits — menor calidad, permite más contexto |
| SEGV | Segmentation fault — crash por acceso a memoria inválida |
| switch-model.sh | Script bash para cambiar entre modos LLM/Vision/ComfyUI |
| style lock | Técnica de fijar parámetros visuales y solo variar el prompt |
| IPAdapter | Nodo ComfyUI que usa imagen de referencia como guía visual |
| MCP | Model Context Protocol — protocolo estándar para herramientas de agente |
| FastMCP | Framework Python para implementar servidores MCP |
| VOID_ENGINE | Plataforma web de orquestación del pipeline — AdonisJS 7.x + HTMX + Alpine.js + Tailwind + DaisyUI |
| DaisyUI | Librería de componentes UI para Tailwind CSS — HTML puro, sistema de temas via CSS custom properties, compatible con HTMX |
| HTMX | Librería JS que extiende HTML con atributos para partial page updates y SSE — reemplaza fetch/axios en el frontend |

---

## Decisión: Visión No Necesita Ser Uncensored

La censura solo importa en la etapa de generación del prompt, no en el análisis visual. Huihui Vision describe lo que ve como descripción técnica (composición, paleta, mood), no como contenido creativo. El contenido explícito lo genera SuperGemma/TrevorJS en el paso siguiente.

Modelos descartados para visión uncensored:
- Gemma 3 12B abliterated: mmproj no funciona correctamente con llama.cpp + Open WebUI
- Gemma 4 26B Uncensored MAX Q8_0: 26.9 GB, no cabe en hardware
- Gemma 4 E4B HauhauCS: Evaluado pero no necesario dado el flujo correcto
