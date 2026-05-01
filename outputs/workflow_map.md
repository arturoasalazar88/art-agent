# Mapa de Workflows — Procesos Creativos y de Generación de Assets

> Versión: 1.1
> Fecha: 2026-05-01 (actualizado con Qwen3.6-35B-A3B — sesión 15)
> Alcance: Procesos creativos, generación de assets y contratos de handoff entre actores.
> Este documento es la fuente de verdad para el diseño de la plataforma de orquestación.
> **No incluye MCP server** — esa capa se define por separado.

---

## 1. Actores del Sistema

### 1.1 Humanos

| Actor | Rol | Interfaz Principal | Restricciones |
|---|---|---|---|
| **Arturo (Director / Artista)** | Toma decisiones creativas, aprueba canon, define tono, escribe prompts visuales | Open WebUI (`10.1.0.105:3000`) | Nunca toca Unity directamente en la etapa de generación |

### 1.2 Agentes IA

| Actor | Rol | Interfaz Principal | Restricciones |
|---|---|---|---|
| **El Ingeniero** (Claude Code / OpenCode) | Ejecución técnica: scripts, pipelines, infra, orquestación | Claude Code CLI / Terminal | NUNCA lee campos `prompt`/`negative_prompt`. NUNCA genera contenido creativo. |

### 1.3 Modelos LLM Locales

| Actor | Modelo GGUF | Tipo | Servicio | Rol | Nunca hace |
|---|---|---|---|---|---|
| **SuperGemma** | supergemma4-26b-uncensored-fast-v2-Q4_K_M | Uncensored | `llama-supergemma` | Ideación libre, escenas crudas, diálogo oscuro, lore | Emitir comandos técnicos |
| **TrevorJS** | gemma-4-26B-A4B-it-uncensored-Q4_K_M | Uncensored | `llama-trevorjs` | Horror corporal, grotesco visual, prompts de imagen extremos | Normalizar, estructurar, emitir specs |
| **Ornstein** | Ornstein-26B-A4B-it-Q4_K_M | Censored | `llama-ornstein` | Estructura narrativa, normalización, contratos técnicos, fichas 3D | Generar contenido gore o prompts visuales explícitos |
| **SuperGemma Vision** | supergemma4-26b-abliterated-multimodal-Q4_K_M | Multimodal | `llama-vision` | Análisis de imágenes de referencia: paleta, composición, luz, mood | Generar horror por sí mismo |
| **Qwen3 Engineer** | Qwen3.6-35B-A3B-Q4_K_M | Censored / MoE | `llama-qwen3` (pendiente systemd) | Codegen (Python, AdonisJS/TS), MCP tool use, orquestación multi-turn, razonamiento técnico largo | Generar contenido creativo o lore |

### 1.4 Servicios y Herramientas

| Actor | Tipo | URL / Acceso | Rol |
|---|---|---|---|
| **llama-server (creativos/Ornstein)** | Runtime LLM | `10.1.0.105:8012` | Sirve Ornstein / SuperGemma / TrevorJS / Vision. Un solo modelo a la vez. |
| **llama-server (Qwen3)** | Runtime LLM | `10.1.0.105:8013` | Sirve Qwen3.6-35B-A3B. Puerto dedicado — nunca simultáneo con :8012 (VRAM). |
| **Open WebUI** | UI de chat | `10.1.0.105:3000` | Interfaz de Arturo para interactuar con LLMs |
| **ComfyUI** | Generador de imágenes | `10.1.0.105:8188` | Genera imágenes a partir de workflows JSON + prompts |
| **switch-model.sh** | Script bash | `~/switch-model.sh` | Árbitro de VRAM — detiene modelo activo, arranca el solicitado |
| **Filesystem** | Almacenamiento | `~/horror-game/` en servidor | Canal de contratos: JSON, markdown, capítulos, specs |
| **Unity Editor** | Motor de juego | Local (cliente) | Montaje de escenas, assets, scripts — pendiente Unity MCP |

---

## 2. Topología del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOMINIO CREATIVO                         │
│  (contenido sensible — solo Arturo + modelos locales)           │
│                                                                  │
│  ┌──────────┐   Open WebUI   ┌──────────────────────────────┐  │
│  │  Arturo  │◄──────────────►│  llama-server :8012          │  │
│  │(Director)│                │  (SuperGemma / TrevorJS /    │  │
│  └──────────┘                │   Ornstein / Vision)         │  │
│                               └──────────────────────────────┘  │
│                                           │                      │
│                                    switch-model.sh               │
│                                           │                      │
│                               ┌───────────────────────┐         │
│                               │  ComfyUI :8188         │         │
│                               │  (Pony Diffusion XL)  │         │
│                               └───────────────────────┘         │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                        CONTRATOS EN FILESYSTEM
                        ~/horror-game/ (JSON, MD)
                                   │
┌──────────────────────────────────┴──────────────────────────────┐
│                      DOMINIO TÉCNICO                             │
│  (sin contenido sensible — El Ingeniero puede operar aquí)       │
│                                                                  │
│  ┌───────────────────┐              ┌─────────────────────┐     │
│  │   El Ingeniero    │              │   Unity Editor      │     │
│  │  (Claude Code /   │─────────────►│  (pendiente Unity   │     │
│  │   OpenCode)       │   contratos  │   MCP)              │     │
│  └───────────────────┘  JSON        └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

**Regla central:** El dominio creativo y el dominio técnico se comunican **exclusivamente a través de archivos en el filesystem**. Nunca por canal directo. Los archivos actúan como contratos: el contenido sensible viaja opaco para el dominio técnico.

---

## 3. Reglas de Aislamiento

| Regla | Actor afectado | Descripción |
|---|---|---|
| **Prompts opacos** | El Ingeniero | Nunca lee, loguea ni procesa `prompt` o `negative_prompt` de ningún JSON |
| **Horror fuera del orquestador** | El Ingeniero, Unity | El orquestador solo recibe IDs, perfiles, flags — nunca prosa gore |
| **Un modelo a la vez** | Todos | La RTX 3060 no soporta dos modelos simultáneos. `switch-model.sh` es obligatorio |
| **ComfyUI exclusivo** | LLMs | Cuando ComfyUI está activo, ningún LLM puede correr (VRAM insuficiente) |
| **Canon antes que interactividad** | Arturo | Ninguna escena interactiva se diseña sin capítulo aprobado como base |
| **Ornstein como firewall** | Ornstein | Toda salida de SuperGemma o TrevorJS pasa por Ornstein antes de ir al dominio técnico |

---

## 4. Infraestructura de Ejecución

```bash
# Cambio de modelo (siempre antes de cada workflow)
~/switch-model.sh ornstein    # estructura, briefs, normalización — :8012, ctx=24576
~/switch-model.sh supergemma  # ideación libre, escritura de capítulos — :8012, ctx=24576
~/switch-model.sh trevorjs    # horror visual, diseño de criaturas — :8012, ctx=24576
~/switch-model.sh vision      # análisis de imágenes de referencia — :8012, ctx=24576
~/switch-model.sh image       # generación de imágenes con ComfyUI

# Qwen3 (pendiente integración a switch-model.sh — arranque manual por ahora)
nohup ~/llama.cpp/build/bin/llama-server \
  --model ~/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf --alias qwen3-coder \
  --port 8013 --ctx-size 40960 --n-gpu-layers 99 --n-cpu-moe 99 \
  --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --jinja \
  --threads 6 --threads-batch 24 > ~/qwen3-live.log 2>&1 &

# Ver estado actual
~/switch-model.sh
```

**Constraint VRAM crítica:**
- Stack Gemma 4 (:8012): ctx=24576 con `--cache-type-k q4_0 --cache-type-v q4_0`
- Qwen3 (:8013): ctx=40960 con `--cache-type-k q8_0 --cache-type-v q8_0 --flash-attn on`
- **Nunca simultáneos** — RTX 3060 12GB no soporta dos modelos activos al mismo tiempo

---

## 5. Estructura de Directorios de Trabajo

```
~/horror-game/
  canon/
    story_bible.md          ← fuente de verdad narrativa
    world_rules.md          ← reglas del mundo
    timeline.md             ← cronología canónica
    canon_index.json        ← índice de entradas canónicas
    change_log.json         ← registro de cambios con clasificación
  chapters/
    ch_01.md, ch_02.md...   ← capítulos aprobados
  chapter_summaries/
    ch_01.json...           ← resúmenes corto + medio por capítulo
  entities/
    characters/             ← fichas de personajes
    locations/              ← fichas de locaciones
    factions/               ← fichas de facciones
    creatures/              ← fichas de criaturas
  scene_specs/              ← InteractiveSceneSpec por escena
  branch_graphs/            ← BranchGraphSpec por arco narrativo
  assets/
    storyboard/             ← prompts de imagen + output generado
    characters/
    environments/
  jobs/unity/               ← UnityPlacementJob + UnitySceneAssemblyJob
  validation/               ← reconciliation_report.json
  refs/images/              ← imágenes de referencia visual
```

---

## 6. Workflows Creativos

### WF-01 — Ideación Libre de Mundo y Novela

**Objetivo:** Explorar ideas sin bloquear creatividad, sin contaminar canon aprobado todavía.
**Actor principal:** SuperGemma
**Interfaz de Arturo:** Open WebUI

```
Arturo ──[sesión Open WebUI]──► SuperGemma
         "explorar origen del hospital,
          vínculos con el culto"
                │
                ▼
         Pasajes crudos, hipótesis,
         opciones de escena (3–7),
         diálogo tentativo
                │
                ▼
Arturo ──[revisión manual]──► selecciona qué vale

        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Arturo ──[sesión Open WebUI]──► Ornstein
         "clasifica este material"
                │
                ▼
         approved_facts_candidate[]
         hypotheses[]
         discarded_or_unverified[]
         chapter_seed[]
         entity_updates_candidate[]
                │
                ▼
         ⚠️  NADA entra a canon sin aprobación explícita de Arturo
```

**Input mínimo para SuperGemma:**
```json
{
  "task_type": "free_ideation",
  "goal": "<objetivo narrativo>",
  "tone": ["<tono_1>", "<tono_2>"],
  "canon_constraints": ["<restricción_existente>"],
  "relevant_entities": ["<entidad_1>", "<entidad_2>"],
  "output_format": "raw_passages_and_options"
}
```

**Output hacia canon (solo tras aprobación de Arturo):**
- Actualización de `canon/story_bible.md`
- Nuevas entradas en `entities/`
- Entrada en `canon/change_log.json` con `change_class: expansion`

---

### WF-02 — Escritura de Capítulo

**Objetivo:** Producir un capítulo nuevo sin cargar la novela completa en contexto.
**Actor principal:** SuperGemma
**Interfaz de Arturo:** Open WebUI

```
Arturo construye paquete contextual mínimo:
  ├── objetivo de escritura
  ├── canon global comprimido     (~500-800 tokens)
  ├── fichas de entidades relevantes (~800-1500 tokens)
  ├── resumen capítulo anterior   (~400-600 tokens)
  ├── outline del capítulo actual (~300-500 tokens)
  └── cambios recientes aplicables (~300-600 tokens)

        ┌────────────────────────────────────────┐
        │  switch-model.sh supergemma            │
        └────────────────────────────────────────┘
                │
                ▼
SuperGemma ──► borrador del capítulo
               escenas internas
               beats emocionales
               hechos potenciales nuevos
                │
                ▼
Arturo ──[revisión]──► aprueba / pide ajustes

        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Ornstein ──► ChapterMemoryRecord
              chapter_summary.short
              chapter_summary.medium
              new_facts[]
              changed_facts[]
              affected_entities[]
              continuity_risks[]
              pending_reconciliation[]
                │
                ▼
Escritura a disco:
  chapters/ch_XX.md
  chapter_summaries/ch_XX.json
  canon/change_log.json  (nueva entrada)
  entities/ (si hay actualizaciones)
```

**Budget de tokens (8,192 total):**

| Bloque | Tokens |
|---|---|
| Sistema / instrucción | 300–500 |
| Canon global comprimido | 500–800 |
| Entidades relevantes | 800–1,500 |
| Capítulo previo + outline actual | 1,000–1,800 |
| Cambios recientes | 300–600 |
| Margen de generación | ~3,000–4,500 |

---

### WF-03 — Reescritura de Capítulo

**Objetivo:** Modificar capítulo existente con trazabilidad completa del cambio.
**Actor principal:** SuperGemma (cambio creativo/tonal) o Ornstein (cambio estructural)

```
Arturo clasifica el cambio:
  ├── expansion       → agrega detalle, no altera hechos
  ├── adjustment_local → modifica escena, sin impacto estructural amplio
  └── retcon          → cambia hechos canónicos, obliga reconciliación

        ┌────────────────────────────────────────┐
        │  switch-model.sh [supergemma|ornstein] │
        └────────────────────────────────────────┘
                │
                ▼
Input:
  capítulo actual (texto)
  rewrite_goal
  preserve[] (qué no tocar)
  do_not_break[] (continuidad crítica)
  affected_entities[]
                │
                ▼
Output: capítulo revisado
                │
                ▼
        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Ornstein compara versión anterior vs nueva:
  diff semántico
  hechos añadidos / eliminados
  riesgos de continuidad
  capítulos aguas abajo que requieren revisión
                │
                ▼
Escritura a disco:
  chapters/ch_XX.md  (actualizado)
  chapter_summaries/ch_XX.json  (actualizado)
  canon/change_log.json  (nueva entrada con change_class)
  entities/ (si aplica)
  validation/pending_reconciliation.json  (si es retcon)
```

---

### WF-04 — Extracción de Lore Canonizable

**Objetivo:** Convertir texto narrativo caótico en canon consultable y estructurado.
**Actor principal:** Ornstein

```
Input: pasaje o capítulo (aprobado por Arturo)
       entidades presentes
       nivel de certeza
       change_class

        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Ornstein extrae:
  story_bible_entries[]      → canon/story_bible.md
  entity_updates[]           → entities/
  timeline_updates[]         → canon/timeline.md
  world_rule_updates[]       → canon/world_rules.md
  ambiguities_to_keep[]      ← preservar deliberadamente
  ambiguities_to_resolve[]   ← marcar para sesión futura
                │
                ▼
Arturo ──[revisión]──► aprueba entradas canónicas
                │
                ▼
canon/canon_index.json  (actualizado)
```

**Regla:** No todo debe solidificarse en canon. La ambigüedad deliberada es parte del horror. Ornstein distingue entre lo que debe resolverse y lo que debe permanecer abierto.

---

### WF-05 — Diseño de Criaturas y Horror Visual

**Objetivo:** Generar diseño sensorial extremo para enemigos, props orgánicos y ambientes degradados.
**Actor principal:** TrevorJS

```
Arturo define:
  función narrativa de la criatura
  biología o pseudobiología
  contexto de aparición (qué nivel, qué escena)
  nivel de agresividad
  restricciones de silhouette o gameplay

        ┌────────────────────────────────────────┐
        │  switch-model.sh trevorjs              │
        └────────────────────────────────────────┘
                │
                ▼
TrevorJS genera (contenido sensible):
  descripción grotesca completa
  variantes (alpha, mutada, descompuesta, etc.)
  materiales sugeridos
  texturas emocionales
  sonidos sugeridos
  hooks visuales
                │
                ▼
Arturo ──[revisión]──► selecciona variante

        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Ornstein traduce a contratos técnicos:
  CreatureVariantCard
  AssetSpec3D
  MaterialProfile
  SpawnProfile
  AnimationHooks
                │
                ▼
entities/creatures/<creature_id>.md
assets/<creature_id>.json

⚠️  TrevorJS nunca produce specs técnicas directamente
⚠️  Ornstein nunca recibe el brief grotesco sin filtrar
```

**Input para TrevorJS:**
```json
{
  "task_type": "creature_design",
  "creature_role": "stalker_enemy",
  "location_context": "hospital_basement",
  "fear_profile": ["<perfil_1>", "<perfil_2>"],
  "movement_style": ["<movimiento_1>", "<movimiento_2>"],
  "gameplay_constraints": ["readable_silhouette", "mobile_performance_budget"]
}
```

**Output normalizado por Ornstein (AssetSpec3D):**
```json
{
  "asset_id": "creature_c03",
  "asset_type": "enemy",
  "variant": "decayed_alpha",
  "scene_role": "stalker_enemy",
  "material_profile": "viscera_wet_v5",
  "animation_hooks": ["stagger", "crawl", "lunge"],
  "spawn_context": ["hospital_b2", "operating_room"],
  "fear_level": 8,
  "canon_refs": ["creatures.c03"],
  "unity_prefab_target": "Enemies/Hospital/C03",
  "source_model": "TrevorJS",
  "normalized_by": "Ornstein"
}
```

---

### WF-06 — Análisis de Referencias Visuales

**Objetivo:** Extraer señales técnicas de imágenes de referencia para dirección de arte.
**Actor principal:** SuperGemma Vision

```
Arturo reúne imágenes de referencia:
  películas, concept art, fotografías, texturas
  → guardar en refs/images/

        ┌────────────────────────────────────────┐
        │  switch-model.sh vision                │
        └────────────────────────────────────────┘
                │
                ▼
Arturo envía imagen(es) vía Open WebUI con pregunta puntual:
  "¿qué tipo de iluminación usa esta imagen?"
  "¿qué dice esta paleta sobre el mood?"
  "¿cómo está construida la jerarquía focal?"
                │
                ▼
SuperGemma Vision extrae:
  paleta dominante (colores HEX o descriptivos)
  contraste (bajo / medio / alto)
  ritmo visual
  jerarquía focal (primer plano / medio / fondo)
  tipo de iluminación (lateral, contraluz, ambiente, etc.)
  lectura de materiales (húmedo, rugoso, metálico, etc.)
  emoción dominante
                │
                ▼
        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Ornstein convierte a:
  ArtDirectionBrief
  LightingProfile
  CameraMoodProfile
  TextureReferenceCard
                │
                ▼
Estos contratos alimentan:
  → prompts de ComfyUI (workflow de assets visuales)
  → specs de iluminación para Unity
  → dirección de arte para TrevorJS en WF-05
```

**Nota operativa:** Vision solo describe formalmente. No genera horror. La censura importa en la generación del prompt (TrevorJS), no en el análisis visual.

---

### WF-07 — Extracción de Interactividad desde Novela

**Objetivo:** Convertir capítulos aprobados en estructura interactiva sin reinventar el lore.
**Actor principal:** Ornstein
**Precondición:** El capítulo fuente debe estar aprobado en `chapters/`.

```
Input:
  chapters/ch_XX.md  (aprobado)
  chapter_summaries/ch_XX.json
  fichas de entidades implicadas
  objetivo de adaptación
  restricciones de complejidad

        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Ornstein extrae:
  objetivos del jugador por escena
  conflictos y tensiones
  variables de estado (flags)
  elecciones con consecuencias
  convergencias (puntos donde las ramas se unen)
  triggers narrativos
                │
                ▼
Output contracts:
  InteractiveSceneSpec    → scene_specs/<scene_id>.json
  BranchGraphSpec         → branch_graphs/<arc_id>.json
  EncounterFlow
  PlayerGoalMap
  NarrativeTriggerMap
                │
                ▼
Arturo ──[revisión]──► aprueba estructura interactiva
                │
                ▼
Listo para WF-08 (normalización hacia Unity)
```

**Regla:** El adaptador interactivo no inventa canon nuevo. Si detecta que necesita información no existente, devuelve una lista de gaps que Arturo debe resolver antes de continuar.

**Ejemplo InteractiveSceneSpec:**
```json
{
  "scene_id": "hospital_b2_intro",
  "canon_refs": ["ch_04", "lore.origin_hospital.001"],
  "player_goal": "restaurar energía auxiliar",
  "scene_type": "exploration_horror",
  "required_assets": ["creature_c03", "nurse_log_02", "generator_unit_01"],
  "branch_flags": ["heard_whispers", "generator_found"],
  "choices": [
    {"id": "inspect_locked_room", "effects": ["fear+1", "journal_hint"]},
    {"id": "follow_drag_marks", "effects": ["route=operating_theater"]}
  ],
  "convergence_to": "hospital_b2_generator_room",
  "trigger_hooks": ["audio_whisper_01", "light_flicker_03"],
  "source_model": "Ornstein",
  "source_refs": ["ch_04"]
}
```

---

## 7. Workflows de Producción de Assets

### WF-08 — Normalización para Contratos Técnicos

**Objetivo:** Preparar handoffs seguros para el dominio técnico (El Ingeniero, Unity).
**Actor principal:** Ornstein

Este workflow es el **firewall semántico** del sistema. Toma cualquier salida del dominio creativo y la traduce a representaciones neutrales y auditables.

```
Entradas válidas:
  pasajes narrativos de SuperGemma
  briefs visuales de TrevorJS
  análisis de Vision
  capítulos aprobados

Entradas inválidas (Ornstein rechaza):
  prosa gore libre sin estructura
  instrucciones ambiguas sin IDs ni entidades

        ┌────────────────────────────────────────┐
        │  switch-model.sh ornstein              │
        └────────────────────────────────────────┘
                │
                ▼
Ornstein produce contratos normalizados:
  StoryBibleEntry
  ChapterMemoryRecord
  InteractiveSceneSpec
  BranchGraphSpec
  AssetSpec3D
  MaterialProfile
  CreatureVariantCard
  UnityPlacementJob    ← solo tras WF-07 completo
  UnitySceneAssemblyJob
                │
                ▼
Contratos escritos a disco:
  assets/<asset_id>.json
  jobs/unity/<job_id>.json
  scene_specs/<scene_id>.json
                │
                ▼
El Ingeniero puede operar sobre estos contratos sin ver contenido sensible
```

**Trazabilidad obligatoria** en todo contrato:
```json
{
  "source_model": "SuperGemma | TrevorJS | Vision | Ornstein",
  "normalized_by": "Ornstein",
  "source_refs": ["ch_04", "creatures.c03"],
  "change_log_refs": ["change_2026_04_28_014"],
  "unity_job_refs": ["job_scene_hospital_b2_014"]
}
```

---

### WF-09 — Generación de Imágenes con ComfyUI

**Objetivo:** Producir assets visuales (storyboard, personajes, ambientes) a partir de prompts del Artista.
**Actor principal del lado creativo:** Arturo + (SuperGemma / TrevorJS para escribir el prompt)
**Actor principal del lado técnico:** El Ingeniero (solo opera la ejecución)

```
LADO ARTISTA (dominio creativo):
────────────────────────────────
Arturo define qué imagen necesita:
  tipo: storyboard / personaje / ambiente / criatura
  contexto narrativo de dónde va a usarse

        ┌────────────────────────────────────────┐
        │  switch-model.sh [supergemma|trevorjs] │
        └────────────────────────────────────────┘
                │
                ▼
Modelo genera el prompt visual (contenido opaco)
                │
                ▼
Arturo guarda el prompt en:
  ~/horror-game/assets/<categoría>/<nombre>.json
  (campos: prompt, negative_prompt, metadata, generation)

El Ingeniero NUNCA ve el contenido de prompt/negative_prompt
────────────────────────────────────────────────────────────

LADO INGENIERO (dominio técnico):
──────────────────────────────────
El Ingeniero lee:
  metadata (scene, characters, mood, notes)
  generation (workflow, width, height, steps, cfg, seed)

        ┌────────────────────────────────────────┐
        │  switch-model.sh image  (= ComfyUI)    │
        └────────────────────────────────────────┘
                │
                ▼
El Ingeniero ejecuta:
  1. Lee prompt JSON del disco
  2. Carga workflow JSON desde ~/ComfyUI/workflows/
  3. Inyecta prompt internamente en el workflow
  4. POST a ComfyUI :8188/prompt
  5. Polling a /history/{job_id}
  6. Guarda imagen en assets/<categoría>/<nombre>.png
  7. Actualiza campo output en el JSON
                │
                ▼
Arturo recibe ruta de imagen generada
Revisa, aprueba o solicita re-generación con ajustes
```

**Workflows ComfyUI disponibles:**

| Nombre | Descripción |
|---|---|
| `pony_horror.json` | Base — Pony Diffusion V6 XL + VAE, sin LoRAs |
| `pony_horror_lora.json` | Completo — Pony + VAE + horror_style + gore_details + dark_fantasy_arch |

**LoRAs y strengths:**

| LoRA | Strength | Uso |
|---|---|---|
| horror_style | 0.7 | Atmósfera general de horror |
| gore_details | 0.5 | Anatomía y detalle gore |
| dark_fantasy_arch | 0.4 | Arquitectura decadente, entornos |

---

### WF-10 — Ingeniería de Plataforma y Orquestación

**Objetivo:** Generar código funcional, scripts de automatización y secuencias de tool calls para VOID_ENGINE, el MCP server y el pipeline de Unity.
**Actor principal:** Qwen3 Engineer
**Interfaz de El Ingeniero:** Claude Code / terminal → Qwen3 :8013

```
Input: especificación técnica (puede ser larga — hasta 32k tokens)
  ├── spec de endpoint AdonisJS / servicio TypeScript
  ├── spec de script Python de pipeline
  ├── brief de escena Unity con protocolo de tool calls
  └── arquitectura de orquestación (VOID_ENGINE, STORY_018)

        ┌────────────────────────────────────────┐
        │  llama-server :8013  (Qwen3 manual)    │
        └────────────────────────────────────────┘
                │
      thinking=OFF para tool calls / JSON compacto
      thinking=ON  para codegen y razonamiento largo
                │
                ▼
Qwen3 produce:
  código TypeScript / Python funcional
  secuencias de MCP tool calls (JSON)
  scripts de orquestación (batch, pipeline)
  notas de constraints respetados (notes[])
                │
                ▼
El Ingeniero revisa, integra al repo, prueba
```

**Regla de aislamiento:** Qwen3 solo recibe especificaciones técnicas. Nunca recibe lore narrativo, prosa de capítulos, briefs gore ni prompts visuales. Opera exclusivamente en el dominio técnico.

**Parámetros por subtarea:**

| Subtarea | Temperature | Thinking | max_tokens |
|---|---|---|---|
| Tool call / JSON compacto | 0.1 | OFF | 2,048 |
| Codegen Python / AdonisJS | 0.3 | ON | 5,000 |
| Multi-turn orquestación | 0.2 | ON + preserve | 2,048/turno |

---

## 8. Secuencias Diarias Operativas

### Caso A — Día de Novelización

```
1. switch-model.sh supergemma
2. WF-01: Arturo explora ideas con SuperGemma vía Open WebUI
3. WF-02: SuperGemma produce borrador de capítulo
4. switch-model.sh ornstein
5. WF-04: Ornstein extrae canon (lore, entidades, hechos)
6. Arturo aprueba entradas canónicas
7. Escritura a: chapters/, chapter_summaries/, canon/, entities/
```

### Caso B — Día de Criaturas y Assets Visuales

```
1. switch-model.sh trevorjs
2. WF-05: TrevorJS genera briefs extremos de criaturas
3. [opcional] switch-model.sh vision
   WF-06: Vision analiza referencias visuales si las hay
4. switch-model.sh ornstein
5. WF-08: Ornstein normaliza → AssetSpec3D, CreatureVariantCard, MaterialProfile
6. switch-model.sh image  (= activa ComfyUI)
7. WF-09: El Ingeniero ejecuta generación de imágenes
8. Arturo revisa imágenes generadas
```

### Caso C — Día de Adaptación Interactiva

```
1. Cargar capítulo aprobado de chapters/
2. switch-model.sh ornstein
3. WF-07: Ornstein extrae InteractiveSceneSpec + BranchGraphSpec
4. Arturo aprueba estructura interactiva
5. WF-08: Ornstein genera UnityPlacementJob
6. El Ingeniero recibe job (domain técnico, sin contenido sensible)
7. [pendiente] El Ingeniero ejecuta sobre Unity MCP
8. Registrar resultados en jobs/unity/ y validation/
```

### Caso D — Día de Ingeniería (VOID_ENGINE / MCP / Scripts)

```
1. Levantar Qwen3 manualmente en :8013
   (asegurarse de que :8012 está detenido — VRAM exclusivo)
2. WF-10: El Ingeniero envía spec técnica a Qwen3 vía API
3. Qwen3 genera código / tool call sequence / script
4. El Ingeniero revisa e integra al repo (Claude Code o directamente)
5. Si el output requiere ejecutar en Unity: WF-08 (job Unity)
6. Apagar Qwen3 antes de levantar cualquier modelo :8012
```

**Nota:** Qwen3 no usa Open WebUI — el canal es API directa desde El Ingeniero.
El contexto de 32k permite pasar specs de arquitectura completas sin fragmentar.

---

## 9. Contratos de Handoff — Catálogo Completo

| Contrato | Origen | Destino | Archivo |
|---|---|---|---|
| `StoryBibleEntry` | Ornstein | canon/story_bible.md | JSON incrustado en MD |
| `ChapterMemoryRecord` | Ornstein | chapter_summaries/ | `ch_XX.json` |
| `InteractiveSceneSpec` | Ornstein | scene_specs/ | `<scene_id>.json` |
| `BranchGraphSpec` | Ornstein | branch_graphs/ | `<arc_id>.json` |
| `EncounterFlow` | Ornstein | scene_specs/ | campo en scene spec |
| `PlayerGoalMap` | Ornstein | scene_specs/ | campo en scene spec |
| `NarrativeTriggerMap` | Ornstein | scene_specs/ | campo en scene spec |
| `AssetSpec3D` | Ornstein (de TrevorJS) | assets/ | `<asset_id>.json` |
| `CreatureVariantCard` | Ornstein (de TrevorJS) | entities/creatures/ | `<creature_id>.json` |
| `MaterialProfile` | Ornstein (de TrevorJS/Vision) | assets/ | campo en asset spec |
| `ArtDirectionBrief` | Ornstein (de Vision) | refs/ | `art_direction_<id>.json` |
| `LightingProfile` | Ornstein (de Vision) | assets/ | campo en scene spec |
| `CameraMoodProfile` | Ornstein (de Vision) | assets/ | campo en scene spec |
| `TextureReferenceCard` | Ornstein (de Vision) | refs/ | `texture_ref_<id>.json` |
| `UnityPlacementJob` | Ornstein | jobs/unity/ | `<job_id>.json` |
| `UnitySceneAssemblyJob` | Ornstein | jobs/unity/ | `<job_id>.json` |

**Ejemplo UnityPlacementJob:**
```json
{
  "job_id": "job_scene_hospital_b2_014",
  "scene_id": "hospital_b2_intro",
  "actions": [
    {"tool": "import_prefab", "params": {"asset_id": "creature_c03", "target": "Enemies/Hospital"}},
    {"tool": "place_object",  "params": {"prefab": "Enemies/Hospital/C03", "position": [12, 0, -4]}},
    {"tool": "assign_material", "params": {"object": "C03_Instance_A", "material_profile": "viscera_wet_v5"}},
    {"tool": "add_trigger", "params": {"object": "CorridorTrigger_02", "event": "audio_whisper_01"}}
  ],
  "validation": ["prefab_exists", "material_exists", "scene_loads_clean"],
  "canon_refs": ["ch_04", "creatures.c03"],
  "source_model": "Ornstein",
  "normalized_by": "Ornstein"
}
```

---

## 10. Sistema de Memoria

### 10.1 Capas de Memoria

| Capa | Contenido | Ubicación | Persistencia | Uso |
|---|---|---|---|---|
| **Global** | Premisa, tono, reglas del mundo, glosario | canon/story_bible.md + world_rules.md | Alta | Siempre comprimida en contexto |
| **Semántica** | Personajes, locaciones, criaturas, facciones | entities/ | Alta | Retrieval por entidad específica |
| **Episódica** | Resúmenes de capítulos y escenas | chapter_summaries/ | Alta | Retrieval por capítulo/acto |
| **Trabajo** | Objetivo actual, escena activa, tarea | contexto del prompt (temporal) | Temporal | Siempre presente en el prompt activo |
| **Cambios** | Retcons, ajustes, impacto pendiente | canon/change_log.json | Alta | Solo cuando hay cambios no reconciliados |

### 10.2 Política de Contexto para 8,192 Tokens

**Orden de prioridad al construir un prompt:**
1. Tarea activa e instrucciones del rol
2. Restricciones de canon (qué no romper)
3. Entidades necesarias para esta tarea
4. Escena o capítulo relevante
5. Cambios recientes no reconciliados
6. Estilo o tono
7. Contexto opcional (si queda espacio)

**Regla operativa:** Si un bloque no cambia la decisión del modelo para esta tarea, no entra al prompt.

**Artefactos de compresión obligatorios** (siempre deben existir):
- Resumen corto por capítulo (~120–180 tokens)
- Resumen medio por capítulo (~300–500 tokens)
- Ficha por entidad (comprimida)
- Timeline comprimido
- World rules comprimidas
- Diff por cambio canónico

### 10.3 Tipos de Cambio Narrativo

| Tipo | Descripción | Impacto | Qué actualizar |
|---|---|---|---|
| `expansion` | Agrega detalle sin alterar hechos | Bajo | Story bible, entity afectada |
| `adjustment_local` | Modifica escena o capítulo, sin impacto estructural amplio | Medio | Capítulo, chapter_summary, change_log |
| `retcon` | Cambia hechos canónicos, obliga reconciliación | Alto | Todo lo anterior + capítulos aguas abajo + validation/ |

---

## 11. Matriz Actor × Workflow

| Workflow | Arturo | SuperGemma | TrevorJS | Ornstein | Vision | ComfyUI | El Ingeniero |
|---|---|---|---|---|---|---|---|
| WF-01 Ideación libre | ✅ aprueba | ✅ genera | — | ✅ clasifica | — | — | — |
| WF-02 Escritura capítulo | ✅ revisa | ✅ escribe | — | ✅ normaliza | — | — | — |
| WF-03 Reescritura capítulo | ✅ revisa | ✅ reescribe | — | ✅ diff semántico | — | — | — |
| WF-04 Extracción lore | ✅ aprueba | input | — | ✅ extrae | — | — | — |
| WF-05 Criaturas | ✅ revisa | — | ✅ diseña | ✅ normaliza | opcional | — | — |
| WF-06 Referencias visuales | ✅ provee imágenes | — | — | ✅ convierte | ✅ analiza | — | — |
| WF-07 Extracción interactividad | ✅ aprueba | — | — | ✅ extrae | — | — | — |
| WF-08 Normalización técnica | — | input | input | ✅ normaliza | input | — | ✅ consume |
| WF-09 Generación imágenes | ✅ aprueba prompt | ✅ escribe prompt | ✅ escribe prompt | — | — | ✅ ejecuta | ✅ opera |

---

## 12. Flujo Maestro End-to-End

De idea a escena interactiva con asset generado:

```
Arturo tiene idea narrativa
        │
        ▼
WF-01 — SuperGemma: ideación libre
        │
        ▼
Arturo aprueba material
        │
        ▼
WF-02 — SuperGemma: escribe capítulo
        │
        ▼
Arturo revisa capítulo
        │
        ├─── WF-04 ──► Ornstein: extrae canon → story_bible, entities
        │
        ├─── WF-05 ──► TrevorJS: diseña criatura → brief visual
        │              └──► Ornstein: normaliza → AssetSpec3D, CreatureVariantCard
        │
        ├─── WF-06 ──► Vision: analiza referencias → datos técnicos
        │              └──► Ornstein: normaliza → ArtDirectionBrief, LightingProfile
        │
        ├─── WF-09 ──► prompt visual (SuperGemma/TrevorJS) → opaco en JSON
        │              └──► El Ingeniero: ejecuta ComfyUI → imagen generada
        │
        └─── WF-07 ──► Ornstein: extrae interactividad → InteractiveSceneSpec
                       └──► WF-08 ──► Ornstein: genera UnityPlacementJob
                                      └──► El Ingeniero: ejecuta sobre Unity (pendiente)
```

---

## 13. Gaps Identificados (Input para Diseño de Plataforma)

Estos son los puntos de fricción actuales que la plataforma de orquestación deberá resolver:

| Gap | Descripción | Impacto |
|---|---|---|
| **Cambio manual de modelo** | `switch-model.sh` es manual — Arturo debe recordar cambiar antes de cada workflow | Alto: error humano frecuente |
| **Sin estado de workflow** | No hay tracking de qué workflow está activo, en qué paso, qué quedó pendiente | Alto: sesiones incompletas |
| **Coordinación Artista-Ingeniero manual** | El Artista guarda en disco, el Ingeniero verifica manualmente — sin notificación | Medio |
| **Sin validación de precondiciones** | No hay verificación automática de que el capítulo fuente exista y esté aprobado antes de WF-07 | Medio |
| **Presupuesto de tokens manual** | El Artista construye el paquete contextual manualmente — riesgo de exceder 8,192 | Alto |
| **Sin queue de generación** | Si hay múltiples prompts pendientes, el Ingeniero los ejecuta uno a uno manualmente | Medio |
| **Sin reconciliación automática** | Los retcons producen `pending_reconciliation[]` pero nadie los persigue si no hay sesión activa | Alto |
| **ComfyUI y LLM no pueden coexistir** | Restricción de VRAM obliga a flujo secuencial — no hay paralelismo posible | Bajo (hardware) |
| **Trazabilidad manual** | Los 5 campos de trazabilidad se agregan manualmente en cada contrato | Medio |
| **Unity MCP no implementado** | WF-07/08 producen jobs pero no hay executor todavía | Alto: bloquea fase 5 |

---

## 14. No Objetivos Actuales

- No construir una plataforma genérica multiagente compleja en esta etapa
- No permitir que el orquestador actúe como autor primario de horror
- No colapsar creatividad, normalización y ejecución en el mismo modelo o prompt
- No meter la novela completa en el contexto de ningún modelo
- No depender del historial bruto de chat como memoria principal
