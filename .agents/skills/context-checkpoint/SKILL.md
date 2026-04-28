---
name: context-checkpoint
description: Crea o actualiza context/working_memory.md con un snapshot operativo completo de la sesion. Usalo antes de operaciones largas, cada ~30 mensajes, o cuando haya riesgo de compactacion. El checkpoint debe ser suficientemente detallado para que el agente retome sin buscar informacion externa.
compatibility: opencode
---

# Context Checkpoint

Crea memoria volatil de corto plazo para poder retomar la sesion si OpenCode o el runtime pierde hilo.

## Cuando usarlo

Usalo cuando:
- la conversacion se esta alargando
- hay riesgo de compactacion
- el agente detecta perdida de hilo
- el usuario pide un checkpoint
- antes de operaciones largas (descargas, compilaciones, esperar procesos)
- como higiene preventiva cada ~30 mensajes

## Instrucciones

### Paso 1 - Capturar estado vivo de la sesion

Escribe o sobreescribe `context/working_memory.md` con esta estructura.
Cada seccion debe estar completamente poblada - no dejar campos vacios ni placeholders.

```markdown
# Working Memory - Checkpoint
> Generado: [YYYY-MM-DD HH:MM]
> Sesion: [numero o fecha]
> Contexto aproximado consumido: [estimacion si es posible]

## REANUDAR AQUI
<!-- Primera seccion que leera el agente al recuperar la sesion -->
**Tarea activa:** [una linea exacta de que se estaba haciendo]
**Proximo paso:** [accion concreta e inmediata - especifica, no vaga]
**Decisiones pendientes:** [N decisiones - listar con DXX]

---

## Que estabamos haciendo
[Descripcion detallada de la tarea activa - 3-5 oraciones. Suficiente para que
alguien sin contexto entienda que se estaba construyendo y por que]

## Hilo de conversacion reciente
[Resumen numerado y comprimido del hilo - no transcripcion, solo contexto
necesario para retomar. Incluir que se investigo, descubrio, descarto y por que]

1. [primer evento relevante]
2. [segundo evento relevante]
...

## Decisiones tomadas en esta sesion (NO formalizadas en conversation_memory.md)
[Cada decision con contexto completo para formalizarla despues sin ambiguedad]

- D[XX] pendiente: [nombre descriptivo]
  - Contexto: [por que surgio]
  - Decision: [que se decidio]
  - Por que: [razonamiento]

## Trabajo en vuelo
[Archivos en edicion activa, comandos esperando respuesta, procesos corriendo]
- Si no hay nada: "Ningun proceso activo al momento del checkpoint"

## Contexto tecnico inmediato
[Rutas, URLs, flags, comandos, valores especificos relevantes al trabajo actual.
Copiar textualmente para evitar errores al retomar. Este campo DEBE ser tan
completo que el agente no necesite buscar informacion externa para continuar]

## Preguntas abiertas
[Decisiones pendientes o informacion que el usuario debe proveer para continuar]
```

### Paso 2 - Confirmar

Reporta exactamente:
```
Checkpoint guardado - context/working_memory.md
  Tarea activa: [resumen en una linea]
  Proximo paso: [siguiente accion]
  Decisiones pendientes de formalizar: [N]
```

## Regla de calidad del checkpoint

Si al crear el checkpoint el agente no puede llenar completamente la seccion
"Contexto tecnico inmediato", debe agregar ahi mismo una nota de que informacion
falta y donde buscarla. El objetivo es que la recuperacion no requiera busquedas
externas.

## Notas

- Este skill no reemplaza `context-save`.
- Este skill no reemplaza `context-close`.
- Despues de retomar una sesion rota, las decisiones pendientes deben formalizarse con `context-save`.
- El archivo `context/working_memory.md` es volatil - se sobreescribe en cada checkpoint y se borra en `context-close`.
