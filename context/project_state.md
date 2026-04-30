# Estado del Proyecto — Survival Horror Video Game

> Última actualización: 2026-04-24
> Trigger de actualización: Solo cuando equipo, alcance o metodología cambian.

---

## Proyecto

| Campo | Valor |
|---|---|
| Nombre | Survival Horror Video Game |
| Tipo | Videojuego survival horror — Unity + Unity MCP + Blender |
| Director | Arturo Salazar |
| Inicio | Abril 2026 |
| Fase actual | Pre-producción — infraestructura validada, pipeline diseñado |

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

| Alias | Modelo GGUF | Servicio systemd | Rol |
|---|---|---|---|
| Ornstein | Ornstein-26B-A4B-it-Q4_K_M.gguf | llama-ornstein | Estructura narrativa, prompts limpios, briefs técnicos, fichas 3D |
| SuperGemma | supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf | llama-supergemma | Ideación libre, escenas crudas, diálogo oscuro, lore, criaturas |
| TrevorJS | gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf | llama-trevorjs | Grotesco visual, horror corporal, prompts visuales extremos |
| SuperGemma Vision | supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf + mmproj | llama-vision | Análisis de imágenes de referencia (composición, paleta, mood) |

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
| llama-server | `http://10.1.0.105:8012` | 8012 | ✅ Operativo (5 modelos) |
| Open WebUI | `http://10.1.0.105:3000` | 3000 | ✅ Operativo (Docker) |
| ComfyUI | `http://10.1.0.105:8188` | 8188 | ✅ Operativo (systemd) |
| MCP server | `http://10.1.0.105:8189` | 8189 | ⬜ Pendiente implementación |

### Switch de Modos

```bash
~/switch-model.sh ornstein    # LLM estructura y briefs
~/switch-model.sh supergemma  # LLM creatividad horror crudo
~/switch-model.sh trevorjs    # LLM grotesco visual uncensored
~/switch-model.sh vision      # Multimodal análisis de imágenes
~/switch-model.sh image       # ComfyUI generación de imágenes
~/switch-model.sh             # muestra estado actual de todos
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

### Preset Vision (supergemma-vision)

```
--ctx-size 4096 --override-tensor ".*=CPU"
```

Nota: `--mmproj-use-cpu` no existe en este build. Se usa `--override-tensor ".*=CPU"` como alternativa para forzar el mmproj a RAM.

### Rutas Importantes en Servidor

| Ruta | Contenido |
|---|---|
| `~/llama.cpp/build/bin/llama-server` | Binario llama.cpp |
| `~/models/gemma4/` | Modelos LLM (Ornstein, SuperGemma, TrevorJS) |
| `~/models/multimodal/` | Modelo vision + mmproj |
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
| llama-vision | `/etc/systemd/system/llama-vision.service` |
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
| VRAM al límite | 🔴 Alta | Nunca subir ctx-size de 8192 sin bajar a Q3_K_M. Monitorear con `journalctl`. |
| Puerto único compartido (8012) | 🟡 Media | Solo un modelo activo a la vez. `switch-model.sh` previene conflictos. |
| Restart loop en SEGV | 🟡 Media | Servicios tienen `Restart=on-failure`. Monitorear con `journalctl -u llama-X -f`. |
| ComfyUI + llama-server simultáneos | 🔴 Alta | Imposible — RTX 3060 no tiene VRAM para ambos. Switch obligatorio. |
| Build llama.cpp sin SSL | 🟡 Media | No puede descargar imágenes por HTTPS. Usar base64 o Open WebUI para visión. |

---

## Restricciones de Hardware Validadas

| Parámetro | Límite | Consecuencia si excede |
|---|---|---|
| ctx-size con Q4_K_M | 8192 sin flags extra | SEGV — KV cache no cabe en VRAM |
| ctx-size con Q4_K_M + KV q4_0 | **24576 validado** | PASS en 3 configs; techo real >24576 sin probar |
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
| SuperGemma Vision | Modelo multimodal para análisis de imágenes |
| Pony Diffusion | Checkpoint SDXL para generación de imágenes en ComfyUI |
| LoRA | Adaptador de bajo rango — modifica estilo del modelo base |
| mmproj | Vision encoder — archivo separado que habilita procesamiento de imágenes |
| abliterated | Modelo al que se le removieron pesos de rechazo (uncensored) |
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

---

## Decisión: Visión No Necesita Ser Uncensored

La censura solo importa en la etapa de generación del prompt, no en el análisis visual. SuperGemma Vision describe lo que ve sin necesitar ser uncensored porque su output es una descripción técnica (composición, paleta, mood), no contenido explícito. El contenido explícito lo genera SuperGemma/TrevorJS en el paso siguiente.

Modelos descartados para visión uncensored:
- Gemma 3 12B abliterated: mmproj no funciona correctamente con llama.cpp + Open WebUI
- Gemma 4 26B Uncensored MAX Q8_0: 26.9 GB, no cabe en hardware
- Gemma 4 E4B HauhauCS: Evaluado pero no necesario dado el flujo correcto
