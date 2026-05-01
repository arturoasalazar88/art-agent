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

### Paso 2 - Actualizar `context/stories/INDEX.md` y `context/next_steps.md`

**INDEX.md** (fuente de verdad de tareas):
- actualiza estado de stories trabajadas en esta sesion (⬜→🟡, 🟡→✅, etc.)
- agrega nuevas stories si surgieron en la sesion con ID siguiente en secuencia
- si una story se completo, cambiarla a ✅ (no borrarla)

**next_steps.md** (solo contexto de sesion):
- actualiza fase actual si cambio
- actualiza lista de "completado en ultima sesion" (ultimos 5 items max)
- actualiza contexto tecnico critico si hay nuevas restricciones
- actualiza preguntas de arranque para la proxima sesion

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

### Paso 6 - Escaneo de markers obsoletos en outputs/

Si en esta sesion se completo al menos una STORY (cambio de estado a ✅):

1. Identificar el numero de cada story completada (XXX)
2. Para cada una, ejecutar:
   ```bash
   grep -rn "pending STORY_XXX" outputs/
   ```
3. Si hay matches, actualizarlos antes de continuar:
   - Cambiar `⚠️ Preliminar — pending STORY_XXX` por `✅ Validado (STORY_XXX — descripcion breve)`
4. Si los matches estan en archivos marcados `🔒 Historico`, ignorarlos (son intencionales)

Ver reglas completas en `.agents/rules/memory-hygiene.md`.

### Paso 7 - Limpiar checkpoint

Si existe `context/working_memory.md`, eliminarlo o vaciarlo porque un cierre exitoso invalida el checkpoint.

### Paso 8 - Confirmar cierre

Resume:
- fecha de cierre
- archivos de memoria actualizados
- numero de decisiones nuevas
- si `context/project_state.md` cambio o no

## Notas

- Si algo no pudo persistirse, dilo explicitamente en el cierre.
- Recuerda al usuario que la proxima sesion debe empezar con `context-start`.
