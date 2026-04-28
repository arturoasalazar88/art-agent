# Especificación de Workflow Creativo, Orquestador y Sistema de Memoria

## Propósito

Este documento consolida las decisiones de diseño tomadas para el proyecto narrativo y de videojuego survival horror. El objetivo es establecer una base operativa clara para un flujo creativo asistido por varios LLMs locales, una futura capa de orquestación hacia Unity y un sistema de memoria optimizado para novelización mutable con una ventana de contexto limitada.

El sistema se separa deliberadamente en dos dominios: **creación semántica sensible** y **orquestación técnica**. Unity MCP aporta herramientas para que un cliente de IA gestione assets, controle escenas, edite scripts y automatice tareas dentro del editor, por lo que encaja mejor como capa de ensamblaje interactivo que como autor primario del contenido narrativo o visual.[cite:77][cite:86][cite:194]

## Decisiones rectoras

La dirección narrativa parte de una **story bible** mutable antes de construir la experiencia interactiva. Una story bible funciona como documento vivo para alinear mundo, tono, personajes, reglas, cronología y flujo narrativo del proyecto.[cite:122][cite:125][cite:129]

La experiencia interactiva no se diseña desde cero en paralelo con la novela. Primero se construye canon narrativo; después se extraen escenas, beats, variables, decisiones y convergencias para adaptación interactiva, siguiendo principios habituales de narrativa ramificada e interactive fiction.[cite:127][cite:193][cite:198]

La creación de horror explícito, body horror, criaturas grotescas y material visual extremo no debe depender del modelo orquestador conectado a Unity. Esa parte debe residir en LLMs locales y pipelines locales para evitar dependencia de capas de moderación de proveedores externos.[cite:150][cite:158][cite:168]

La memoria contextual no debe intentar meter la novela completa en el prompt. Debe recuperar, comprimir, priorizar y podar contexto según la tarea activa, en línea con prácticas modernas de context engineering y memory management para agentes con contexto limitado.[cite:201][cite:206][cite:209][cite:212][cite:215]

## Modelos disponibles y roles

### Modelos uncensored

| Alias | Modelo | Rol principal | Salida primaria |
|---|---|---|---|
| SuperGemma | supergemma4-26b-uncensored-fast-v2-Q4_K_M | Ideación libre, escenas crudas, diálogo oscuro, lore, criaturas | Pasajes narrativos, capítulos, ideas de escenas, fichas crudas |
| TrevorJS | gemma-4-26B-A4B-it-uncensored-Q4_K_M | Grotesco visual, horror corporal, prompts visuales extremos | Briefs visuales extremos, variantes de criatura, conceptos sensoriales |

### Modelos censored o controlados

| Alias | Modelo | Rol principal | Salida primaria |
|---|---|---|---|
| Ornstein | Ornstein-26B-A4B-it-Q4_K_M | Estructura narrativa, prompts limpios, briefs técnicos, fichas 3D | Canon limpio, resúmenes, contratos estructurados, fichas técnicas |
| SuperGemma Vision | supergemma4-26b-abliterated-multimodal-Q4_K_M | Análisis visual de referencias | Composición, paleta, mood, intención de cámara, desglose técnico |

Todos los modelos corren en servidor Debian vía `llama-server` en puerto `8012`, alternando con `~/switch-model.sh`.

## Arquitectura conceptual

El sistema queda organizado en cinco capas:

1. **Capa de ideación y novelización**: conversación creativa, exploración de mundo, personajes, tono y capítulos.
2. **Capa de canon y memoria**: story bible, fichas de personajes, timeline, reglas del mundo, resúmenes de capítulos y change log.
3. **Capa de normalización**: conversión de salidas creativas en documentos estructurados, resúmenes operativos y contratos de handoff.
4. **Capa de orquestación**: ensamblaje técnico para convertir contenido aprobado en escenas, eventos, estados y objetos interactivos.
5. **Capa de implementación en motor**: Unity MCP y herramientas relacionadas para materializar escenas, assets, scripts, triggers y vínculos interactivos.[cite:77][cite:86][cite:174]

La responsabilidad creativa recae primero en los modelos locales. La responsabilidad de montaje, estructura ejecutable y automatización de editor recae después en la capa de orquestación técnica.[cite:77][cite:86]

## Workflow maestro

### Fase 1: Novelización mutable

Objetivo: construir una novela base o material de consulta vivo, no una novela cerrada e intocable.

Flujo:
1. Sesión de conversación con SuperGemma para explorar ideas, escenas, personajes, tensiones y tono.
2. Producción de fragmentos crudos: pasajes, escenas, diálogos, descripciones de mundo y lore.
3. Revisión con Ornstein para convertir el material en capítulos coherentes, resúmenes, listas de hechos, fichas y canon limpio.
4. Registro de nuevos hechos aprobados en la story bible y sistemas de memoria.
5. Generación de diffs narrativos: qué cambió, qué personajes afecta, qué escenas futuras podría tocar.

Resultado esperado:
- capítulos editables,
- resumen por capítulo,
- hechos nuevos aprobados,
- entidades actualizadas,
- efectos potenciales sobre continuidad.

### Fase 2: Consolidación del canon

Objetivo: impedir que la novelización mutable destruya coherencia global.

Artefactos principales:
- `story_bible.md`
- `world_rules.md`
- `timeline.md`
- `characters/*.md`
- `locations/*.md`
- `factions/*.md`
- `creatures/*.md`
- `chapters/*.md`
- `chapter_summaries/*.md`
- `change_log.json`
- `canon_index.json`

La story bible y sus derivados actúan como fuente única de verdad para el resto del pipeline.[cite:122][cite:125][cite:129]

### Fase 3: Extracción de interactividad

Objetivo: traducir canon aprobado a estructura interactiva sin reinventar el lore.

Flujo:
1. Tomar un capítulo o conjunto de escenas aprobadas.
2. Pedir a Ornstein que extraiga objetivos del jugador, conflictos, variables, flags, elecciones, consecuencias y posibles convergencias.
3. Generar un `InteractiveSceneSpec` por escena o beat.
4. Construir un `BranchGraphSpec` que indique bifurcaciones, fusiones y condiciones de entrada/salida.
5. Crear storyboards funcionales orientados a implementación.

Las narrativas interactivas escalan mejor cuando las ramas importantes convergen en puntos clave y cuando el estado del juego se expresa con variables y consecuencias explícitas, en lugar de ramificar todo indefinidamente.[cite:127][cite:193][cite:198]

### Fase 4: Generación de assets

Objetivo: producir material sensible sin exponer al orquestador a descripciones explícitas innecesarias.

Flujo por subtipo:
- **Narrativa y diálogo oscuro**: SuperGemma produce material crudo; Ornstein limpia y estructura.
- **Criaturas y horror corporal**: TrevorJS genera descripciones, variantes y briefs extremos.
- **Dirección visual y referencia**: Vision analiza referencias y extrae composición, paleta, luz y mood.
- **Fichas técnicas**: Ornstein convierte el material anterior a formatos técnicos reutilizables.

Resultado esperado:
- `AssetSpec3D`
- `TexturePackSpec`
- `MaterialProfile`
- `CreatureVariantCard`
- `LightingProfile`
- `AudioMoodSpec`
- `NarrativePropCard`

### Fase 5: Orquestación hacia Unity

Objetivo: ensamblar interactividad sin que el orquestador tenga que consumir horror explícito en lenguaje natural.

Unity MCP y servidores similares están pensados para que clientes de IA gestionen assets, escenas, objetos y scripts dentro del editor, por lo que el input óptimo son herramientas y contratos estructurados, no prosa libre.[cite:77][cite:86][cite:174]

Flujo:
1. El orquestador recibe contratos estructurados, no descripciones crudas.
2. Interpreta `scene_id`, `asset_refs`, `spawn_rules`, `player_goal`, `branch_flags`, `audio_cues`, `lighting_profile` y `unity_actions`.
3. Llama herramientas de Unity MCP para importar, crear, organizar, modificar o conectar recursos en el editor.[cite:77][cite:86]
4. Genera o ajusta scripts, GameObjects, triggers, colliders, cámaras, materiales, animaciones y secuencias según el contrato.[cite:77][cite:194]
5. Produce logs, snapshots y resultados de validación para retroalimentar al sistema.

## Regla de separación semántica

La arquitectura adopta una regla central:

> El orquestador no debe ver contenido horror explícito si esa semántica no es necesaria para la tarea técnica.

Por eso existe una **capa de normalización** entre creación local y montaje interactivo. Esa capa traduce contenido sensible a identificadores, perfiles y parámetros técnicos.

Ejemplo:
- Entrada creativa local: descripción explícita de criatura, mutación, daño corporal, texturas orgánicas, olor, sonido, comportamiento.
- Salida normalizada: `creature_id=C03`, `variant=decayed_alpha`, `material_profile=viscera_wet_v5`, `fear_level=8`, `spawn_context=hospital_basement`, `animation_hooks=[stagger, crawl, lunge]`.

## Sistema de memoria para novela mutable

### Principio general

Con una ventana de 8,192 tokens, el sistema debe operar por **contexto mínimo suficiente**. Context engineering moderno enfatiza presupuestar tokens, comprimir contexto, hacer retrieval selectivo y podar información irrelevante para la tarea activa.[cite:201][cite:206][cite:209][cite:215]

### Capas de memoria

| Capa | Función | Persistencia | Uso típico |
|---|---|---|---|
| Memoria global | Premisa, tono, tema, reglas del mundo, glosario, límites canónicos | Alta | Siempre comprimida |
| Memoria semántica | Personajes, lugares, criaturas, facciones, objetos, relaciones | Alta | Retrieval por entidad |
| Memoria episódica | Resumen de capítulos, escenas, eventos y consecuencias | Alta | Retrieval por capítulo/acto |
| Memoria de trabajo | Objetivo actual, instrucciones de edición, escena activa | Temporal | Siempre |
| Memoria de cambios | Retcons, ajustes locales, expansiones, impacto pendiente | Alta | Solo cuando aplica |

### Estrategia de ensamblaje de contexto

Cada prompt debe construirse con este orden:
1. objetivo de la tarea actual,
2. instrucciones del rol del modelo,
3. resumen canónico global mínimo,
4. entidades relevantes,
5. resumen del capítulo actual,
6. resumen del capítulo anterior y siguiente si afectan continuidad,
7. cambios recientes no reconciliados,
8. bloque opcional de estilo o tono,
9. espacio restante para respuesta.

La regla operativa es simple: si un bloque no cambia la decisión del modelo para esta tarea, no entra al prompt.[cite:201][cite:212][cite:215]

### Presupuesto sugerido de tokens

Para 8,192 tokens:
- 400–700 tokens: tarea actual e instrucciones.
- 500–900 tokens: canon global comprimido.
- 1,000–1,800 tokens: entidades relevantes.
- 800–1,500 tokens: resumen del capítulo activo.
- 400–800 tokens: continuidad vecina y cambios recientes.
- resto: generación o edición principal.

El sistema debe favorecer **resúmenes canónicos** y **factsheets** sobre historial bruto de conversación.[cite:206][cite:209][cite:212]

### Tipos de cambio

Todo cambio narrativo debe clasificarse como:
- **Expansión**: agrega detalle sin alterar hechos canónicos.
- **Ajuste local**: modifica una escena o capítulo sin impacto estructural amplio.
- **Retcon**: cambia hechos que obligan a reconciliar otras piezas del canon.

Esta clasificación permite que el sistema de memoria determine qué actualizar, qué invalidar y qué capítulos mandar a revisión.[cite:212][cite:215]

## Casos de uso por modelo

### 1. Ideación libre

- Modelo: SuperGemma.
- Input: idea general, tono, tema, personaje o situación.
- Output: escenas crudas, posibilidades narrativas, diálogos, conflictos.
- Postproceso: Ornstein resume, ordena y extrae hechos aprobables.

### 2. Escritura de capítulo

- Modelo: SuperGemma.
- Input: paquete contextual optimizado del capítulo objetivo.
- Output: borrador del capítulo o de la escena.
- Postproceso: Ornstein produce `chapter_summary`, `canon_facts`, `impact_notes`.

### 3. Reescritura o ajuste de capítulo

- Modelo: SuperGemma o Ornstein según sensibilidad.
- Input: capítulo actual, diff deseado, restricciones de continuidad.
- Output: nueva versión del capítulo.
- Postproceso: actualización de resúmenes, hechos y change log.

### 4. Diseño de criatura y horror visual

- Modelo: TrevorJS.
- Input: tipo de amenaza, función narrativa, contexto del nivel.
- Output: brief grotesco, variantes, rasgos materiales y sensoriales.
- Postproceso: Ornstein traduce a `CreatureVariantCard` y `AssetSpec3D`.

### 5. Análisis de referencias visuales

- Modelo: Vision.
- Input: imagen o referencia visual.
- Output: paleta, luz, composición, mood, enfoque de cámara, lectura formal.
- Postproceso: Ornstein convierte eso en `ArtDirectionBrief` o `LightingProfile`.

### 6. Extracción de interactividad

- Modelo: Ornstein.
- Input: capítulo o escena aprobada.
- Output: objetivos, decisiones, flags, ramas, condiciones, consecuencias.
- Postproceso: generación de `InteractiveSceneSpec` y `BranchGraphSpec`.

### 7. Ensamblaje técnico para motor

- Modelo: orquestador, local o externo, con acceso a contratos estructurados.
- Input: specs de escenas y assets ya normalizados.
- Output: acciones sobre Unity MCP, organización de escenas, imports y wiring.
- Restricción: no consume payload creativo explícito salvo necesidad estrictamente técnica.

## Formatos de handoff

### StoryBibleEntry

```json
{
  "entry_id": "lore.origin_hospital.001",
  "title": "Origen del hospital",
  "type": "world_lore",
  "canon_status": "approved",
  "summary": "Resumen canónico corto",
  "facts": ["hecho_1", "hecho_2"],
  "entities": ["hospital", "order_of_ash", "dr_morales"],
  "tone_tags": ["dread", "religious_decay"],
  "source_chapters": ["ch_01"],
  "change_class": "expansion"
}
```

### InteractiveSceneSpec

```json
{
  "scene_id": "hospital_b2_intro",
  "canon_refs": ["ch_03", "lore.origin_hospital.001"],
  "player_goal": "Encontrar el generador auxiliar",
  "scene_type": "exploration_horror",
  "required_entities": ["creature_c03", "nurse_log_02"],
  "branch_flags": ["heard_whispers", "generator_found"],
  "choices": [
    {"id": "inspect_door", "effect": ["fear+1"]},
    {"id": "follow_noise", "effect": ["route=alt_corridor"]}
  ],
  "convergence_to": "hospital_b2_generator_room",
  "audio_cues": ["low_hum", "wet_drag"],
  "lighting_profile": "fluorescent_decay_v2"
}
```

### AssetSpec3D

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
  "unity_prefab_target": "Enemies/Hospital/C03"
}
```

### ChapterMemoryRecord

```json
{
  "chapter_id": "ch_04",
  "summary_short": "Resumen de 120-180 tokens",
  "summary_medium": "Resumen de 300-500 tokens",
  "new_facts": ["fact_a", "fact_b"],
  "changed_facts": ["fact_c"],
  "affected_entities": ["protagonist", "creature_c03"],
  "continuity_risks": ["timeline_conflict_minor"],
  "change_class": "adjustment_local",
  "pending_reconciliation": ["ch_06", "timeline.ash_period"]
}
```

## Operación diaria recomendada

1. Elegir el objetivo del día: escribir, reescribir, consolidar canon, diseñar criatura, extraer interactividad o ensamblar escena.
2. Cambiar modelo local con `~/switch-model.sh` según la tarea.
3. Construir el paquete contextual mínimo para el modelo activo.
4. Generar salida primaria.
5. Pasar la salida por normalización con Ornstein.
6. Actualizar story bible, memorias y change log.
7. Si aplica, enviar contratos al orquestador para Unity.
8. Ejecutar acciones en Unity MCP y registrar resultados.
9. Producir evidencias: logs, screenshots, notas de revisión y nuevos impactos de continuidad.

## No objetivos actuales

- No construir todavía una plataforma general de orquestación de agentes.
- No intentar meter la novela completa dentro del contexto del modelo.
- No permitir que el orquestador actúe como autor primario de horror explícito.
- No acoplar novelización y ensamblaje técnico en el mismo prompt o el mismo modelo.

## Criterios de éxito

El enfoque se considerará exitoso si:
- la novela puede crecer y mutar sin romper continuidad,
- el canon puede consultarse y resumirse sin depender del historial completo del chat,
- los assets sensibles se generan localmente sin bloqueo por censura externa,
- el orquestador recibe solo contratos estructurados y puede montar interactividad en Unity,
- el sistema permite pasar de lore a escena interactiva con trazabilidad entre capítulo, asset y acción de editor.

## Resumen ejecutivo operativo

La estrategia aprobada para esta etapa del proyecto es la siguiente:
- primero se construye una novelización mutable como base canónica del juego;
- esa novelización vive en un sistema de memoria jerárquico y altamente comprimido;
- los LLMs locales especializados generan narrativa y assets sensibles;
- Ornstein actúa como normalizador estructural y traductor a contratos técnicos;
- el orquestador trabaja sobre metadatos y specs, no sobre horror explícito;
- Unity MCP se usa como capa de ensamblaje interactivo y automatización del editor.[cite:77][cite:86][cite:122][cite:127][cite:201][cite:215]
