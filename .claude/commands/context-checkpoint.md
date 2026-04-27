## /context-checkpoint — Snapshot de Memoria a Corto Plazo

Úsalo cuando:
- La conversación se está alargando y hay riesgo de compactación de contexto
- El agente detecta que está perdiendo hilo de conversaciones anteriores
- El usuario pide explícitamente un checkpoint
- Antes de operaciones largas (compilar, descargar, esperar procesos del servidor)
- Cada ~30 mensajes como higiene preventiva

Este skill crea o sobreescribe `context/working_memory.md` — un archivo volátil de corto plazo que captura el estado vivo de la sesión. No reemplaza `context-close` ni los archivos permanentes de memoria.

---

### Comportamiento

#### Paso 1 — Capturar estado de la conversación activa

Escribe en `context/working_memory.md` con esta estructura:

```markdown
# Working Memory — Checkpoint
> Generado: [timestamp]
> Sesión: [fecha]
> Contexto aproximado consumido: [estimación en porcentaje si es posible]

## Qué estábamos haciendo
[Descripción concisa de la tarea activa — máximo 3 oraciones]

## Hilo de conversación reciente (últimos 10-15 intercambios)
[Resumen comprimido del hilo — no transcripción, solo contexto necesario para retomar]

## Decisiones tomadas en esta sesión (no formalizadas aún)
[Lista de decisiones del hilo actual que NO están aún en conversation_memory.md]
- DXX pendiente: [contexto → decisión → por qué]

## Trabajo en vuelo
[Archivos en edición, comandos esperando respuesta, procesos corriendo]
- Archivo: [ruta] — estado: [qué se está haciendo]
- Servidor: [qué proceso está corriendo]

## Contexto técnico inmediato
[Variables, valores, rutas, flags o configuraciones relevantes al trabajo actual]

## Próximo paso exacto
[La siguiente acción concreta a tomar para continuar]

## Preguntas abiertas
[Cualquier decisión pendiente o información que el usuario deba proveer]
```

#### Paso 2 — Confirmar

Imprime:
```
🔖 Checkpoint guardado — context/working_memory.md
   Tarea activa: [resumen en una línea]
   Próximo paso: [siguiente acción]
   Decisiones pendientes de formalizar: [N]
```

---

### Cuándo NO usarlo

- No reemplaza `/context-close` — al cerrar sesión, las decisiones deben pasar a `conversation_memory.md`
- No reemplaza `/context-save` — ese skill es para persistir decisiones individuales en los archivos permanentes
- No es para registrar artefactos — eso va en `artifacts_registry.md`

---

### Recuperación tras compactación o ruptura de sesión

Si Claude Code pierde contexto o la sesión se rompe, al retomar:

1. Ejecutar `/context-start` normalmente
2. Si el resumen parece incompleto o desactualizado, leer también `context/working_memory.md`
3. El agente debe anunciar: *"Encontré un checkpoint de [timestamp]. Estábamos trabajando en [X]. ¿Continúo desde ahí?"*
4. Después de retomar, formalizar las decisiones pendientes del working_memory a `conversation_memory.md` con `/context-save`
5. Una vez retomado y formalizado, el working_memory puede borrarse o archivarse

---

### Re-arquitectura de memoria (sesión rota)

Si la sesión se rompe completamente y hay que re-arquitecturar:

1. `/context-start` — carga memoria base
2. Leer `context/working_memory.md` — recupera el hilo
3. Leer `context/next_steps.md` — recupera el estado operativo
4. El agente presenta: qué se estaba haciendo, qué decisiones quedan pendientes, cuál es el próximo paso
5. Usuario confirma o corrige
6. Continuar desde el checkpoint

---

### Integración con context-start

El skill `/context-start` debe verificar si existe `context/working_memory.md`. Si existe y su timestamp es reciente (misma sesión), lo incluye en el resumen de apertura como sección adicional:

```
### ⚡ Checkpoint activo encontrado
- Tarea interrumpida: [descripción]
- Timestamp: [hora]
- ¿Retomar desde el checkpoint?
```
