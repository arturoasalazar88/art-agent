---
name: opencode-usage
description: Explica como usar este repo en OpenCode con el mismo sistema de memoria que en Claude Code, incluyendo prompts exactos de inicio, guardado, checkpoint, recuperacion y cierre. Usalo cuando necesites cambiar de agente sin perder el flujo operativo.
compatibility: opencode
---

# OpenCode Usage

Guia operativa para usar este repo en OpenCode con la misma disciplina de memoria que en Claude Code.

## Objetivo

Dar al usuario y al agente una receta exacta para cambiar entre runtimes sin perder:
- carga de memoria
- checkpoints
- guardado de decisiones
- cierre correcto de sesion

## Mapeo de equivalencias

### Claude Code

- `/context-start`
- `/context-save`
- `/context-checkpoint`
- `/context-close`

### OpenCode

Como no estamos tocando `.opencode/commands/`, en OpenCode el equivalente operativo es pedir el uso explicito de skills:

- `Usa el skill context-start`
- `Usa el skill context-save`
- `Usa el skill context-checkpoint`
- `Usa el skill context-close`

## Prompts exactos recomendados

### Inicio de sesion

Usa este prompt:

```text
Usa el skill context-start para inicializar la sesion en este repo. Despues dame un resumen corto del estado del proyecto, indica si hay checkpoint activo y preguntame en que trabajamos hoy.
```

### Guardar una decision o descubrimiento

```text
Usa el skill context-save para guardar en la memoria del proyecto la decision o descubrimiento que acabamos de tomar. Si afecta mas de un archivo de context, actualiza todos los necesarios y resume que guardaste.
```

### Crear checkpoint antes de una operacion larga

```text
Usa el skill context-checkpoint y crea un snapshot operativo de la sesion antes de continuar. Incluye tarea activa, trabajo en vuelo, decisiones pendientes y proximo paso exacto.
```

### Retomar una sesion interrumpida

```text
Usa el skill recovery-from-checkpoint. Si existe context/working_memory.md, resumeme que estabamos haciendo, que decisiones faltan por formalizar y preguntame si retomamos desde ahi.
```

### Cierre de sesion

```text
Usa el skill context-close para cerrar la sesion correctamente. Actualiza la memoria del proyecto, limpia working_memory si existe y luego dame un resumen breve del cierre.
```

## Workflow minimo recomendado

### Flujo normal

1. Inicio:

```text
Usa el skill context-start para inicializar la sesion en este repo.
```

2. Durante la sesion, cuando haya una decision importante:

```text
Usa el skill context-save para persistir la decision importante que acabamos de tomar.
```

3. Antes de compilaciones largas, tareas densas o riesgo de compactacion:

```text
Usa el skill context-checkpoint antes de seguir.
```

4. Al terminar:

```text
Usa el skill context-close para cerrar la sesion.
```

### Flujo de recuperacion

1. Arranque:

```text
Usa el skill context-start para inicializar la sesion.
```

2. Si hay checkpoint activo o quieres retomar:

```text
Usa el skill recovery-from-checkpoint.
```

3. Si retomas y formalizas decisiones pendientes:

```text
Usa el skill context-save para formalizar las decisiones pendientes del checkpoint.
```

4. Cierre final:

```text
Usa el skill context-close para cerrar la sesion.
```

## Reglas practicas para no perder paridad

1. Siempre empezar con `context-start`.
2. No asumir que OpenCode ya leyo `CLAUDE.md`; `context-start` lo carga explicitamente.
3. No dejar la sesion sin `context-close`.
4. Si hubo muchas decisiones en una misma sesion, usar `context-save` antes del cierre para no acumular riesgo.
5. Si existe `context/working_memory.md`, tratarlo como fuente de continuidad hasta formalizarlo.

## Respuesta esperada del agente

Cuando uses esta guia, el agente debe:
- preferir los prompts exactos anteriores
- mantener el lenguaje en espanol
- respetar las reglas de `CLAUDE.md`
- operar sobre el mismo sistema de memoria de `context/`

## Nota

Esta skill no reemplaza `context-start`, `context-save`, `context-checkpoint`, `recovery-from-checkpoint` ni `context-close`. Solo explica como invocarlos en OpenCode para mantener el mismo funcionamiento que en Claude Code.
