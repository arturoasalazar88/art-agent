---
name: context-save
description: Persiste decisiones, descubrimientos, artefactos o cambios operativos en la memoria del proyecto sin esperar al cierre de sesion. Usalo cuando haya que actualizar los archivos de context durante la sesion.
compatibility: opencode
---

# Context Save

Guarda memoria estructurada durante la sesion con la misma intencion de `.claude/commands/context-save.md`.

## Cuando usarlo

Usalo cuando:
- el usuario pida guardar una decision o descubrimiento
- se tome una decision importante que no deba perderse
- cambie el estado operativo del proyecto
- se cree o modifique un artefacto relevante

## Instrucciones

### Paso 1 - Clasificar lo que se va a guardar

Determina si el nuevo contexto corresponde a:
- decision significativa
- artefacto nuevo o modificado
- cambio de infraestructura o metodologia
- cambio de estado operativo

### Paso 2 - Actualizar el archivo correcto

#### Si es una decision

Actualiza `context/conversation_memory.md` con:
- siguiente ID secuencial `DXX`
- contexto o trigger
- opciones consideradas
- decision tomada
- por que
- descartado, si aplica

#### Si es un artefacto nuevo o modificado

Actualiza `context/artifacts_registry.md` con:
- ruta exacta
- estado
- fecha
- descripcion breve

#### Si es un cambio de proyecto o infraestructura

Actualiza `context/project_state.md` solo si cambio equipo, infraestructura, metodologia, riesgos o glosario.

#### Si es un cambio de estado operativo o de tarea

Actualiza `context/stories/INDEX.md` cambiando el estado de la story afectada (⬜→🟡, 🟡→✅, etc.) o agregando una nueva story con el siguiente ID en secuencia.

Actualiza `context/next_steps.md` solo si cambio el foco de sesion o hay nuevo contexto tecnico critico.

### Paso 3 - Confirmar

Resume que archivos se actualizaron y que informacion quedo persistida.

## Notas

- No uses este skill para limpiar checkpoints; eso corresponde a `context-close`.
- No registres creatividad ni prompts opacos; mantente en metadatos y contexto tecnico.
