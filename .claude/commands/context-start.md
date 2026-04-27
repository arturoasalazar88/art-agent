## /context-start — Apertura de Sesión

Lee los archivos de memoria en este orden:

1. `context/project_state.md`
2. `context/artifacts_registry.md`
3. `context/conversation_memory.md`
4. `context/next_steps.md`
5. `context/working_memory.md` — **solo si existe**. Si existe, incluirlo en el resumen como sección especial ⚡.

Después de leerlos, presenta este resumen estructurado al usuario:

### Estado del proyecto
- Nombre del proyecto y fase actual
- Infraestructura: qué servicios están operativos vs pendientes
- ¿Hubo cambios en el servidor desde la última sesión? (preguntar al usuario)

### ⚡ Checkpoint activo (solo si existe working_memory.md)
- Tarea interrumpida: [descripción]
- Timestamp del checkpoint
- Decisiones pendientes de formalizar
- Próximo paso registrado
- Pregunta: ¿Retomar desde el checkpoint o empezar tarea nueva?

### Decisiones activas
- Las 3–5 decisiones más recientes de `conversation_memory.md`
- Cualquier decisión que tenga impacto en el trabajo de hoy

### Pendientes (🔴 🟡 ⬜)
- 🔴 Urgentes de `next_steps.md`
- 🟡 En progreso
- ⬜ Siguientes en cola

### Último artefacto
- Archivo más reciente de `artifacts_registry.md` con su estado

### ¿En qué trabajamos hoy?
Pregunta al usuario qué quiere abordar en esta sesión.
