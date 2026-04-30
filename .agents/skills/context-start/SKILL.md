---
name: context-start
description: Carga el sistema de memoria y las reglas operativas del proyecto al inicio de la sesion. Usalo al empezar cada sesion en OpenCode. Si existe context/working_memory.md, detecta el checkpoint y guia la recuperacion sin invocar skills externos ni hacer busquedas web.
compatibility: opencode
---

# Context Start

Inicializa la sesion en OpenCode con la misma logica de memoria que usa Claude Code en este repo.

## Cuando usarlo

Usalo al inicio de cada sesion. Si el runtime no precargo `CLAUDE.md`, este skill debe cargarlo explicitamente junto con los archivos de `context/`.

## Instrucciones

### Paso 1 - Cargar reglas base

Lee `CLAUDE.md` completo para recuperar:
- rol del agente
- separacion Artista/Ingeniero
- restricciones de hardware
- politica documental
- protocolo de memoria y cierre de sesion

### Paso 2 - Cargar memoria persistente

Lee estos archivos en este orden:
1. `context/project_state.md`
2. `context/artifacts_registry.md`
3. `context/conversation_memory.md`
4. `context/next_steps.md`
5. `context/stories/INDEX.md`
6. `context/working_memory.md` solo si existe

### Paso 3 - Presentar resumen de apertura

#### Si existe context/working_memory.md — mostrar PRIMERO antes del resumen normal:

```
CHECKPOINT ACTIVO - sesion interrumpida detectada
  Tarea: [extraer de seccion "Que estabamos haciendo"]
  Timestamp: [extraer del encabezado del archivo]
  Proximo paso: [extraer de seccion "REANUDAR AQUI -> Proximo paso"]
  Decisiones sin formalizar: [N - contar las DXX pendientes]

Retomamos desde el checkpoint?
```

#### Luego el resumen normal:

**Estado del proyecto:**
- nombre del proyecto y fase actual
- infraestructura operativa vs pendiente
- riesgos o restricciones tecnicas que afecten el trabajo de hoy

**Decisiones activas:**
- las 3-5 decisiones mas recientes de `context/conversation_memory.md`
- incluir cualquier decision con impacto directo en la tarea actual

**Trabajo pendiente:**
- mostrar `context/stories/INDEX.md` completo agrupado por area
- priorizar al mostrar: 🟡 en progreso → 🔬 research → 🔴 bloqueadas → ⬜ pendientes de mayor prioridad
- `context/next_steps.md` solo para contexto tecnico critico de sesion, no para lista de tareas

**Ultimo artefacto:**
- reporta el archivo mas reciente o relevante en `context/artifacts_registry.md`

**Cierre de sesion obligatorio:**
- recordar que la sesion debe terminar con `context-close`

### Paso 4 - Responder a la decision del usuario

#### Si el usuario dice "si, retomemos" o equivalente:

**NO invocar skills externos. NO hacer busquedas web. NO llamar herramientas intermedias.**

Ejecutar exactamente en orden:
1. Confirmar: "Retomando desde el checkpoint de [timestamp]"
2. Leer seccion "REANUDAR AQUI" de `context/working_memory.md`
3. Anunciar: "Estabamos [tarea activa]. El proximo paso es: [proximo paso exacto]"
4. Ejecutar ese proximo paso directamente
5. Durante la sesion recuperada, formalizar decisiones pendientes con `context-save` cuando corresponda

**Regla anti-bucle:** Si el proximo paso requiere informacion externa, verificar primero
la seccion "Contexto tecnico inmediato" del checkpoint. Solo buscar externamente si la
informacion no esta ahi.

#### Si el usuario dice "no, tarea nueva":

1. Preguntar: "En que trabajamos hoy?"
2. No borrar el checkpoint todavía
3. Al terminar la sesion, `context-close` lo limpiara

### Paso 5 - Pregunta de arranque (solo si no hay checkpoint o el usuario rechaza retomar)

Preguntar al usuario en que trabajamos hoy.

## Notas

- No inventes estado si algun archivo falta; reportalo claramente.
- Si `context/working_memory.md` existe, no lo borres en este skill.
- Este skill debe comportarse como la contraparte OpenCode de `.claude/commands/context-start.md`.
- El agente NUNCA debe invocar `recovery-from-checkpoint` como herramienta de shell.
  La recuperacion es inline en este mismo skill.
