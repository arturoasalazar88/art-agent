rom pathlib import Path
content = r'''# Handoff Técnico: Workflows Detallados por LLM, Interacciones y Orquestador

## 1. Objetivo

Este documento describe con detalle técnico el flujo operativo completo para novelización mutable, consolidación de canon, extracción de interactividad, generación de assets y ensamblaje con orquestador hacia Unity MCP. El objetivo es que cualquier agente colaborador (por ejemplo, Art Companion) pueda reconstruir la lógica del sistema, entender los roles de cada modelo y operar sobre los mismos contratos de handoff.

## 2. Infraestructura actual

- Host de modelos: servidor Debian.
- Runtime de modelos: `llama-server`.
- Puerto activo: `8012`.
- Cambio de modelo: `~/switch-model.sh`.
- Restricción fuerte: ventana de contexto operativa de 8,192 tokens.
- Principio de arquitectura: separar creación semántica sensible de orquestación técnica.

## 3. Modelos y responsabilidades

### 3.1 Uncensored

#### SuperGemma
- Modelo: `supergemma4-26b-uncensored-fast-v2-Q4_K_M`
- Dominio: ideación libre, escenas crudas, diálogo oscuro, lore, criaturas.
- Rol principal: generador semántico creativo de alto nivel.
- Tipo de salida: capítulos, escenas, pasajes, world lore, character beats, raw dialogue.
- Nunca entrega directamente comandos a Unity.

#### TrevorJS
- Modelo: `gemma-4-26B-A4B-it-uncensored-Q4_K_M`
- Dominio: grotesco visual, horror corporal, prompts visuales extremos.
- Rol principal: diseñador sensorial y morfológico de horror.
- Tipo de salida: creature briefs, mutation specs, gore texture concepts, material ideas, visual prompt packs.
- Nunca entrega directamente comandos a Unity.

### 3.2 Censored / controlados

#### Ornstein
- Modelo: `Ornstein-26B-A4B-it-Q4_K_M`
- Dominio: estructura narrativa, limpieza semántica, briefs técnicos, fichas 3D.
- Rol principal: normalizador, estructurador, traductor de contenido creativo a contratos técnicos.
- Tipo de salida: resúmenes, canon facts, scene specs, branch graphs, asset cards, handoff JSON.
- Es el principal puente entre creatividad y ejecución.

#### SuperGemma Vision
- Modelo: `supergemma4-26b-abliterated-multimodal-Q4_K_M`
- Dominio: análisis de imágenes de referencia.
- Rol principal: extracción de señales técnicas de material visual externo.
- Tipo de salida: composición, paleta, lighting cues, focal hierarchy, mood analysis, silhouette notes.
- No genera horror por sí mismo; describe formalmente.

## 4. Entidades del sistema

### 4.1 Documentos canónicos
- `story_bible.md`
- `world_rules.md`
- `timeline.md`
- `canon_index.json`
- `change_log.json`
- `characters/<character_id>.md`
- `locations/<location_id>.md`
- `factions/<faction_id>.md`
- `creatures/<creature_id>.md`
- `chapters/<chapter_id>.md`
- `chapter_summaries/<chapter_id>.json`
- `scene_specs/<scene_id>.json`
- `branch_graphs/<arc_id>.json`
- `assets/<asset_id>.json`

### 4.2 Tipos de memoria
- Memoria global.
- Memoria semántica por entidad.
- Memoria episódica por capítulo/escena.
- Memoria de trabajo por tarea activa.
- Memoria de cambios para retcons y reconciliación.

### 4.3 Tipos de cambio
- `expansion`
- `adjustment_local`
- `retcon`

## 5. Principio rector del sistema

La novela es mutable. Por lo tanto, ninguna pieza narrativa se considera aislada. Cada escritura o reescritura produce no solo texto, sino un paquete de memoria derivada con:
- resumen corto,
- resumen medio,
- hechos nuevos,
- hechos cambiados,
- entidades afectadas,
- riesgos de continuidad,
- capítulos que deben reconciliarse.

## 6. Flujo maestro de punta a punta

1. Usuario define objetivo narrativo o visual.
2. Se selecciona modelo según la naturaleza de la tarea.
3. Se arma un paquete contextual mínimo para 8,192 tokens.
4. El modelo genera salida primaria.
5. Ornstein normaliza o estructura la salida.
6. Se actualizan canon y memorias.
7. Si la salida ya es implementable, se genera contrato para orquestador.
8. Orquestador interpreta contratos, nunca prosa cruda extrema.
9. Orquestador ejecuta acciones técnicas sobre Unity MCP.
10. Se capturan resultados, logs, screenshots y estado del editor.
11. Se retroalimenta al sistema para nueva iteración.

## 7. Workflow 1: ideación libre de mundo y novela

### 7.1 Objetivo
Explorar ideas sin bloquear creatividad y sin contaminar directamente el canon aprobado.

### 7.2 Modelo principal
- SuperGemma.

### 7.3 Entradas mínimas
- Premisa del proyecto.
- Tono buscado.
- Tema emocional.
- Restricciones de canon ya existentes.
- Objetivo de la sesión: escena, personaje, capítulo, lugar, criatura o arco.

### 7.4 Prompt packet sugerido
```json
{
  "task_type": "free_ideation",
  "goal": "explorar origen del hospital y su vínculo con el culto",
  "tone": ["dread", "religious_decay", "body_horror"],
  "canon_constraints": ["no romper timeline aprobado", "mantener ambigüedad de la entidad principal"],
  "relevant_entities": ["hospital", "order_of_ash", "dr_morales"],
  "output_format": "raw_passages_and_options"
}
```

### 7.5 Salidas primarias
- 3 a 7 opciones de escena.
- Pasajes narrativos crudos.
- Ideas de capítulos.
- Nuevas hipótesis de lore.
- Diálogo tentativo.

### 7.6 Postproceso obligatorio
Ornstein toma esa salida y la divide en:
- `approved_facts_candidate[]`
- `hypotheses[]`
- `discarded_or_unverified[]`
- `chapter_seed[]`
- `entity_updates_candidate[]`

### 7.7 Regla
Nada de esta fase entra al canon sin pasar por normalización y aprobación explícita.

## 8. Workflow 2: escritura de capítulo

### 8.1 Objetivo
Escribir un capítulo nuevo sin cargar la novela completa en contexto.

### 8.2 Modelo principal
- SuperGemma.

### 8.3 Context assembly
Orden exacto del contexto:
1. objetivo de escritura,
2. instrucciones de estilo,
3. canon global comprimido,
4. entidades relevantes,
5. resumen capítulo previo,
6. resumen del capítulo objetivo,
7. cambios recientes que afectan continuidad,
8. escena puntual a escribir,
9. límite de salida.

### 8.4 Budget recomendado
- sistema/instrucción: 300-500 tokens
- canon global: 500-800 tokens
- entidades: 800-1500 tokens
- capítulo previo + actual: 1000-1800 tokens
- cambios recientes: 300-600 tokens
- margen de generación: resto disponible

### 8.5 Input contract
```json
{
  "task_type": "write_chapter",
  "chapter_id": "ch_04",
  "chapter_goal": "revelar el origen del ala quirúrgica sin explicar demasiado",
  "narrative_mode": "close_third_person",
  "tone_profile": ["claustrophobic", "wet_decay", "religious_fear"],
  "canon_global_compact": "...",
  "entity_cards": ["protagonist", "dr_morales", "hospital_b2"],
  "prev_chapter_summary": "...",
  "current_chapter_outline": ["scene_a", "scene_b", "scene_c"],
  "recent_changes": ["retcon_ash_ritual_02"],
  "output_target": "full_draft"
}
```

### 8.6 Salidas primarias
- borrador del capítulo,
- escenas internas,
- beats emocionales,
- nuevos hechos potenciales.

### 8.7 Postproceso con Ornstein
Generar:
- `chapter_summary.short`
- `chapter_summary.medium`
- `new_facts[]`
- `changed_facts[]`
- `affected_entities[]`
- `continuity_risks[]`
- `pending_reconciliation[]`

### 8.8 Archivos actualizados
- `chapters/ch_04.md`
- `chapter_summaries/ch_04.json`
- `change_log.json`
- entidades afectadas

## 9. Workflow 3: reescritura de capítulo

### 9.1 Objetivo
Modificar un capítulo existente sin perder trazabilidad.

### 9.2 Modelo principal
- SuperGemma si el cambio es creativo o tonal.
- Ornstein si el cambio es estructural o de continuidad.

### 9.3 Tipos de solicitud
- expansión,
- ajuste local,
- retcon.

### 9.4 Input contract
```json
{
  "task_type": "rewrite_chapter",
  "chapter_id": "ch_04",
  "change_class": "adjustment_local",
  "rewrite_goal": "hacer más ambigua la presencia de la criatura",
  "current_text": "...",
  "preserve": ["evento del generador", "diario de enfermería", "tono de paranoia"],
  "do_not_break": ["timeline_hospital", "motivation_protagonist"],
  "affected_entities": ["creature_c03", "protagonist"],
  "expected_output": "revised_chapter_with_minimal_disruption"
}
```

### 9.5 Postproceso
Ornstein compara versión anterior vs nueva y emite:
- diff semántico,
- hechos añadidos/eliminados,
- riesgo de continuidad,
- lista de capítulos aguas abajo a revisar.

## 10. Workflow 4: extracción de lore canonizable

### 10.1 Objetivo
Convertir texto rico y caótico en canon consultable.

### 10.2 Modelo principal
- Ornstein.

### 10.3 Entrada
- pasaje o capítulo,
- entidades presentes,
- nivel de certeza,
- clasificación de cambio.

### 10.4 Salida
```json
{
  "story_bible_entries": [],
  "entity_updates": [],
  "timeline_updates": [],
  "world_rule_updates": [],
  "ambiguities_to_keep": [],
  "ambiguities_to_resolve": []
}
```

### 10.5 Regla
No todo debe solidificarse en canon. El sistema debe preservar ambigüedad deliberada cuando sirve al horror.

## 11. Workflow 5: diseño de criaturas y horror visual

### 11.1 Objetivo
Generar diseño sensorial y corporal extremo para amenazas, props orgánicos o ambientes degradados.

### 11.2 Modelo principal
- TrevorJS.

### 11.3 Entradas
- función narrativa de la criatura,
- biología o pseudobiología,
- contexto de aparición,
- nivel de agresividad,
- restricciones de silhouette o gameplay.

### 11.4 Input contract
```json
{
  "task_type": "creature_design",
  "creature_role": "stalker_enemy",
  "location_context": "hospital_basement",
  "fear_profile": ["wet", "surgical", "half-human"],
  "movement_style": ["crawl", "stagger", "burst_lunge"],
  "gameplay_constraints": ["readable silhouette", "mobile_performance_budget"],
  "output_target": "extreme_visual_brief"
}
```

### 11.5 Salidas primarias
- descripción grotesca,
- variantes,
- materiales sugeridos,
- texturas emocionales,
- sonidos sugeridos,
- hooks visuales.

### 11.6 Postproceso con Ornstein
Traducción a:
- `CreatureVariantCard`
- `AssetSpec3D`
- `MaterialProfile`
- `SpawnProfile`
- `AnimationHooks`

### 11.7 Regla
TrevorJS nunca escribe comandos de implementación. Su función termina al entregar semántica creativa extrema.

## 12. Workflow 6: análisis de referencias visuales

### 12.1 Objetivo
Leer imágenes de referencia y extraer señales útiles para arte y dirección.

### 12.2 Modelo principal
- SuperGemma Vision.

### 12.3 Entradas
- imagen o conjunto de imágenes,
- pregunta puntual,
- necesidad: composición, paleta, luz, cámara, mood, formas.

### 12.4 Salidas
- paleta dominante,
- contraste,
- ritmo visual,
- jerarquía focal,
- tipo de iluminación,
- lectura material,
- emoción dominante.

### 12.5 Postproceso con Ornstein
Convertir a:
- `ArtDirectionBrief`
- `LightingProfile`
- `CameraMoodProfile`
- `TextureReferenceCard`

## 13. Workflow 7: extracción de interactividad desde novela

### 13.1 Objetivo
Convertir capítulos o escenas aprobadas en estructura interactiva.

### 13.2 Modelo principal
- Ornstein.

### 13.3 Entrada
- capítulo aprobado,
- resúmenes,
- entidades implicadas,
- objetivo de adaptación,
- restricciones de complejidad.

### 13.4 Salidas
- `InteractiveSceneSpec`
- `BranchGraphSpec`
- `EncounterFlow`
- `PlayerGoalMap`
- `NarrativeTriggerMap`

### 13.5 Output contract ejemplo
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
  "difficulty_notes": ["short_mobile_session", "high_tension_low_combat"]
}
```

### 13.6 Regla
El adaptador interactivo no inventa canon nuevo salvo autorización explícita.

## 14. Workflow 8: normalización para orquestador

### 14.1 Objetivo
Preparar handoffs seguros para el modelo orquestador y para Unity MCP.

### 14.2 Modelo principal
- Ornstein.

### 14.3 Operación
Tomar salidas narrativas o visuales y convertirlas a representaciones neutrales y técnicas.

### 14.4 Tipos de handoff
- `StoryBibleEntry`
- `ChapterMemoryRecord`
- `InteractiveSceneSpec`
- `BranchGraphSpec`
- `AssetSpec3D`
- `TexturePackSpec`
- `MaterialProfile`
- `UnityPlacementJob`
- `UnitySceneAssemblyJob`

### 14.5 Ejemplo de UnityPlacementJob
```json
{
  "job_id": "job_scene_hospital_b2_014",
  "scene_id": "hospital_b2_intro",
  "actions": [
    {"tool": "import_prefab", "params": {"asset_id": "creature_c03", "target": "Enemies/Hospital"}},
    {"tool": "place_object", "params": {"prefab": "Enemies/Hospital/C03", "position": [12,0,-4]}},
    {"tool": "assign_material", "params": {"object": "C03_Instance_A", "material_profile": "viscera_wet_v5"}},
    {"tool": "add_trigger", "params": {"object": "CorridorTrigger_02", "event": "audio_whisper_01"}}
  ],
  "validation": ["prefab_exists", "material_exists", "scene_loads_clean"],
  "canon_refs": ["ch_04", "creatures.c03"]
}
```

## 15. Workflow 9: orquestador

### 15.1 Objetivo
Montar interactividad y estructura técnica sin generar semántica horror explícita.

### 15.2 Naturaleza del orquestador
- Puede ser local o externo.
- Debe operar sobre contratos ya normalizados.
- Debe ser auditable.
- Debe mantener trazabilidad con canon y assets.

### 15.3 Entradas válidas
- scene specs,
- branch graphs,
- placement jobs,
- asset specs,
- validaciones,
- estado actual del proyecto.

### 15.4 Entradas inválidas
- prosa gore libre,
- capítulos sin normalizar,
- prompts creativos extremos,
- instrucciones ambiguas sin IDs ni entidades resueltas.

### 15.5 Responsabilidades
- ordenar secuencia de ensamblaje,
- llamar herramientas MCP,
- verificar precondiciones,
- generar tareas técnicas faltantes,
- registrar resultados,
- pedir reintentos o correcciones.

### 15.6 Bucle operativo
1. leer estado del proyecto,
2. leer contrato actual,
3. validar dependencias,
4. generar plan de acciones,
5. ejecutar herramientas MCP,
6. inspeccionar respuesta del editor,
7. decidir si termina, corrige o escala error.

### 15.7 Estado interno mínimo
```json
{
  "current_job": "job_scene_hospital_b2_014",
  "scene_id": "hospital_b2_intro",
  "dependencies_ok": true,
  "executed_actions": ["import_prefab", "place_object"],
  "failed_actions": [],
  "pending_actions": ["assign_material", "add_trigger"],
  "validation_state": "running"
}
```

## 16. Workflow 10: Unity MCP

### 16.1 Objetivo
Recibir acciones estructuradas y operar sobre Unity Editor.

### 16.2 Tipos de acción esperados
- importar assets,
- crear objetos,
- instanciar prefabs,
- asignar materiales,
- editar scripts,
- conectar triggers,
- organizar escenas,
- modificar componentes,
- lanzar validaciones.

### 16.3 Contrato de ida y vuelta
Entrada del orquestador:
- nombre de herramienta,
- parámetros,
- objetivo,
- validación esperada.

Respuesta del motor:
- éxito/error,
- rutas afectadas,
- objetos creados/modificados,
- mensajes de consola,
- warnings,
- IDs de escenas u objetos.

### 16.4 Regla de seguridad
Cualquier acción sobre el motor debe referenciar assets o entidades ya registradas, nunca texto libre ambiguo.

## 17. Workflow 11: validación y reconciliación

### 17.1 Objetivo
Detectar errores de continuidad y errores técnicos tras cada iteración.

### 17.2 Validación narrativa
- ¿rompió canon?
- ¿rompió motivaciones?
- ¿rompió timeline?
- ¿aumentó o disminuyó ambigüedad no deseada?
- ¿el capítulo actualizado obliga a revisar otros?

### 17.3 Validación técnica
- ¿scene spec tiene todos los asset refs?
- ¿existen prefabs?
- ¿faltan materiales o scripts?
- ¿la escena carga limpia?
- ¿hay errores de consola?
- ¿hay elementos fuera de budget móvil?

### 17.4 Salida
- `reconciliation_report.json`
- `technical_validation_report.json`
- actualizaciones a `change_log.json`

## 18. Secuencia diaria recomendada

### Caso A: día de novelización
1. cambiar a SuperGemma,
2. explorar ideas,
3. producir borrador,
4. cambiar a Ornstein,
5. extraer canon y memorias,
6. actualizar archivos.

### Caso B: día de criaturas
1. cambiar a TrevorJS,
2. generar briefs extremos,
3. cambiar a Vision si hay referencias,
4. cambiar a Ornstein,
5. emitir `AssetSpec3D` y `MaterialProfile`.

### Caso C: día de adaptación interactiva
1. cargar capítulo aprobado,
2. usar Ornstein para `InteractiveSceneSpec`,
3. generar `UnityPlacementJob`,
4. pasar al orquestador,
5. ejecutar en Unity MCP,
6. validar scene result.

## 19. Política de contexto para 8,192 tokens

### 19.1 Reglas duras
- Nunca enviar novela completa.
- Nunca enviar todos los capítulos.
- Nunca enviar historial bruto largo del chat.
- Preferir resúmenes, entity cards y diffs.
- Un prompt = una tarea.

### 19.2 Prioridad de contexto
1. tarea activa,
2. restricciones de canon,
3. entidades necesarias,
4. escena/capítulo relevante,
5. cambios pendientes,
6. estilo,
7. contexto opcional.

### 19.3 Artefactos de compresión obligatorios
- resumen corto por capítulo,
- resumen medio por capítulo,
- ficha por entidad,
- timeline comprimido,
- world rules comprimidas,
- diff por cambio.

## 20. Estructura propuesta de directorios

```text
project_root/
  canon/
    story_bible.md
    world_rules.md
    timeline.md
    canon_index.json
    change_log.json
  chapters/
    ch_01.md
    ch_02.md
  chapter_summaries/
    ch_01.json
    ch_02.json
  entities/
    characters/
    locations/
    factions/
    creatures/
  scene_specs/
  branch_graphs/
  assets/
  jobs/
    unity/
  validation/
  refs/
    images/
```

## 21. Trazabilidad obligatoria

Cada artefacto debe poder contestar:
- ¿de qué capítulo salió?
- ¿qué entidad lo originó?
- ¿qué modelo lo produjo?
- ¿qué modelo lo normalizó?
- ¿qué cambio canónico introdujo?
- ¿qué job de Unity lo implementó?

### 21.1 Campos mínimos de trazabilidad
```json
{
  "source_model": "SuperGemma",
  "normalized_by": "Ornstein",
  "source_refs": ["ch_04", "creatures.c03"],
  "change_log_refs": ["change_2026_04_28_014"],
  "unity_job_refs": ["job_scene_hospital_b2_014"]
}
```

## 22. No objetivos actuales

- No crear todavía una plataforma genérica multiagente compleja.
- No usar el orquestador como generador primario de horror.
- No colapsar creatividad, normalización y ejecución en un solo paso.
- No depender del historial del chat como memoria principal.

## 23. Resumen operativo final

- SuperGemma crea novela y semántica narrativa cruda.
- TrevorJS crea semántica visual extrema y diseño de horror corporal.
- Vision analiza referencias y extrae señales visuales formales.
- Ornstein convierte todo lo anterior en canon limpio, memoria compacta y contratos técnicos.
- El orquestador solo consume contratos estructurados.
- Unity MCP recibe acciones concretas y auditablemente trazables.
- La memoria del sistema vive en archivos persistentes y resúmenes, no en el contexto bruto.
'''
Path('output').mkdir(exist_ok=True)
path = Path('output/handoff-workflows-detallados-llms-orquestador.md')
path.write_text(content, encoding='utf-8')
print(str(path))