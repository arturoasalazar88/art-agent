---
name: recovery-from-checkpoint
description: Instrucciones para retomar una sesion desde context/working_memory.md. IMPORTANTE - este skill NO debe ser invocado como herramienta de shell. Sus instrucciones deben ejecutarse inline por el agente despues de que el usuario confirme retomar el checkpoint en context-start.
compatibility: opencode
---

# Recovery From Checkpoint

Guia para retomar una sesion interrumpida desde el checkpoint.

## ADVERTENCIA CRITICA

Este skill NO es una herramienta de shell. NO lo invoques con subprocess, exec, ni como comando.
Sus instrucciones son pasos que el agente ejecuta directamente en su propio contexto.

Si el agente se encuentra invocando este skill como herramienta externa, debe detenerse
inmediatamente y seguir las instrucciones de abajo de forma directa.

## Cuando aplica

Cuando el usuario confirma retomar desde un checkpoint detectado en `context-start`.

## Instrucciones de recuperacion (ejecutar inline, no como herramienta)

### Paso 1 - Confirmar retoma

Decir: "Retomando desde el checkpoint de [timestamp del working_memory.md]"

### Paso 2 - Leer la seccion REANUDAR AQUI

Leer `context/working_memory.md`, seccion "REANUDAR AQUI". Extraer:
- Tarea activa
- Proximo paso exacto
- N decisiones pendientes

### Paso 3 - Anunciar el estado recuperado

Decir exactamente:
```
Retomando sesion.
Estabamos: [tarea activa]
Proximo paso: [proximo paso exacto]
Decisiones sin formalizar: [N]
```

### Paso 4 - Ejecutar el proximo paso directamente

Ejecutar el "Proximo paso exacto" del checkpoint.

**NO hacer nada de esto antes de ejecutar:**
- busquedas web
- fetch de URLs externas
- invocacion de otros skills
- preguntas adicionales al usuario

La seccion "Contexto tecnico inmediato" del checkpoint debe tener toda la informacion
necesaria. Si algo falta, notarlo al usuario pero continuar con lo disponible.

### Paso 5 - Durante la sesion recuperada

- Continuar el trabajo normal desde el proximo paso
- Formalizar decisiones pendientes con `context-save` cuando sea natural hacerlo
  (no interrumpir el trabajo para formalizarlas todas de golpe)
- Tratar las decisiones DXX pendientes del checkpoint como si fueran de la sesion actual

### Paso 6 - Cierre

Terminar con `context-close` como cualquier sesion normal.
`context-close` limpiara `context/working_memory.md` al cerrar.

## Que hacer si el contexto tecnico inmediato es insuficiente

Si al ejecutar el proximo paso falta informacion critica que no esta en el checkpoint:

1. Notificar al usuario: "El checkpoint no incluye [informacion faltante]. Necesito [X] para continuar."
2. Pedir al usuario que provea la informacion
3. Continuar desde ahi
4. En el proximo checkpoint, asegurarse de que esa informacion quede registrada en
   "Contexto tecnico inmediato"
