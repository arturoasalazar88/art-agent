---
name: context-close
description: Cierra la sesion actualizando next_steps, conversation_memory, artifacts_registry y, si aplica, project_state; luego limpia working_memory. Usalo al final de cada sesion para mantener la memoria consistente entre agentes.
compatibility: opencode
---

# Context Close

Cierra la sesion con la misma disciplina de memoria exigida en `CLAUDE.md` y `.claude/commands/context-close.md`.

## Cuando usarlo

Usalo al final de toda sesion. Es obligatorio.

## Instrucciones

### Paso 1 - Resumir la sesion

Lista:
- archivos creados o modificados
- decisiones tomadas
- problemas resueltos
- descubrimientos tecnicos

### Paso 2 - Actualizar `context/next_steps.md`

- mueve items completados
- agrega nuevos pendientes surgidos en la sesion
- actualiza fase actual si cambio
- agrega contexto tecnico util para la proxima sesion
- agrega preguntas de arranque para la siguiente sesion si aplica

### Paso 3 - Actualizar `context/conversation_memory.md`

Agrega cada decision significativa con:
- ID secuencial `DXX`
- contexto o trigger
- opciones
- decision
- por que
- descartado, si aplica

### Paso 4 - Actualizar `context/artifacts_registry.md`

Para cada archivo nuevo o modificado:
- agrega o actualiza su entrada
- usa estado y fecha correctos
- conserva artefactos historicos cuando corresponda

### Paso 5 - Actualizar `context/project_state.md` si aplica

Solo si hubo cambios en:
- equipo o roles
- infraestructura o configuracion
- metodologia
- riesgos activos
- glosario

### Paso 6 - Limpiar checkpoint

Si existe `context/working_memory.md`, eliminarlo o vaciarlo porque un cierre exitoso invalida el checkpoint.

### Paso 7 - Confirmar cierre

Resume:
- fecha de cierre
- archivos de memoria actualizados
- numero de decisiones nuevas
- si `context/project_state.md` cambio o no

## Notas

- Si algo no pudo persistirse, dilo explicitamente en el cierre.
- Recuerda al usuario que la proxima sesion debe empezar con `context-start`.
