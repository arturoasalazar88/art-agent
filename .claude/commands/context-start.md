## /context-start — Apertura de Sesión

Lee los 4 archivos de memoria en este orden:

1. `context/project_state.md`
2. `context/artifacts_registry.md`
3. `context/conversation_memory.md`
4. `context/next_steps.md`

Después de leerlos, presenta este resumen estructurado al usuario:

### Estado del proyecto
- Nombre del proyecto y fase actual
- Infraestructura: qué servicios están operativos vs pendientes

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
