## /context-close — Cierre de Sesión

Ejecuta estos pasos en orden:

### 1. Resumen de la sesión
Lista todo lo que se logró en esta sesión:
- Archivos creados o modificados
- Decisiones tomadas
- Problemas resueltos
- Descubrimientos técnicos

### 2. Actualizar `context/next_steps.md`
- Mueve items completados de 🔴/🟡/⬜ a ✅ Completado
- Agrega nuevos items pendientes que surgieron en la sesión
- Actualiza la fase actual si cambió
- Agrega contexto técnico relevante para la próxima sesión
- Agrega preguntas para el usuario al inicio de la siguiente sesión

### 3. Actualizar `context/conversation_memory.md`
Para cada decisión significativa tomada en la sesión, añade una entrada con:
- **ID:** DXX (siguiente número secuencial)
- **Contexto/trigger:** ¿Por qué surgió esta decisión?
- **Opciones:** ¿Qué alternativas se consideraron?
- **Decisión:** ¿Qué se decidió?
- **Por qué:** Razonamiento detrás de la decisión
- **Descartado:** (si aplica) ¿Qué se descartó y por qué?

### 4. Actualizar `context/artifacts_registry.md`
Para cada archivo nuevo o modificado:
- Agregar entrada con ruta, estado, fecha y descripción
- Cambiar estado de artefactos superseded a 🔒 Histórico
- Marcar artefactos en progreso como 🔧 En progreso

### 5. Actualizar `context/project_state.md` (si aplica)
Solo si hubo cambios en:
- Equipo o roles
- Infraestructura (nuevo servicio, nuevo modelo, cambio de config)
- Metodología o framework
- Riesgos activos
- Glosario (nuevos términos)

### 6. Limpiar working_memory.md (si existe)
Si existe `context/working_memory.md`, eliminarlo o vaciarlo — el cierre de sesión exitoso invalida el checkpoint. La próxima sesión parte desde los archivos permanentes de memoria.

### 7. Confirmar
Imprime resumen de cierre:
```
✅ Sesión cerrada — [fecha]
Archivos actualizados:
- context/next_steps.md
- context/conversation_memory.md (X decisiones nuevas)
- context/artifacts_registry.md (X artefactos nuevos/modificados)
- context/project_state.md (si cambió)
```
