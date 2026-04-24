## /context-save — Guardar a Memoria (On-Demand)

Usa este skill en cualquier momento de la sesión para persistir decisiones, descubrimientos o contexto a la memoria sin esperar al cierre de sesión.

### Uso

El usuario puede invocar esto con:
- "guarda esta decisión en memoria"
- "registra este descubrimiento"
- "actualiza la memoria con lo que acabamos de hacer"

### Comportamiento

#### Si se trata de una decisión:
Añade a `context/conversation_memory.md`:
- **ID:** DXX (siguiente número secuencial — revisa el último ID existente)
- **Contexto/trigger**
- **Opciones consideradas**
- **Decisión tomada**
- **Por qué**
- **Descartado** (si aplica)

#### Si se trata de un artefacto nuevo o modificado:
Actualiza `context/artifacts_registry.md`:
- Ruta exacta del archivo
- Estado: ✅ Activo / 🔧 En progreso
- Fecha
- Descripción

#### Si se trata de un cambio de infraestructura o proyecto:
Actualiza `context/project_state.md`:
- Nuevo servicio, modelo, configuración, riesgo, o entrada de glosario

#### Si se trata de un cambio de estado operativo:
Actualiza `context/next_steps.md`:
- Mover items entre estados (⬜ → 🟡 → ✅)
- Agregar nuevos items pendientes

### Confirmación

Después de guardar, imprime:
```
💾 Memoria actualizada:
- [archivo(s) modificado(s)]
- [resumen de lo que se guardó]
```

### Cuándo usarlo
- Después de una decisión importante que no quieres que se pierda si la sesión se interrumpe
- Después de instalar o configurar algo nuevo en el servidor
- Después de descubrir una restricción técnica o gotcha
- Cuando el usuario explícitamente pide guardar algo
- Cuando un chat largo con el usuario contiene información que debe persistir
