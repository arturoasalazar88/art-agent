# Memory Hygiene Rules

## Propósito

Prevenir que documentos en `outputs/` queden con información desactualizada cuando se completan stories o se validan modelos. El problema histórico: `agent_memory_spec.md` y `workflow_map.md` tenían `⚠️ Preliminar — pending STORY_019` durante semanas después de que STORY_019 fue completada.

---

## Regla 1 — Convención de markers de validación

Usar siempre estos markers exactos en documentos de `outputs/`:

| Estado | Marker |
|---|---|
| No validado aún | `⚠️ Preliminar — pending STORY_XXX` |
| Validado | `✅ Validado (STORY_XXX — descripción breve)` |
| Obsoleto | `🔒 Superseded — ver STORY_XXX` |

**Nunca** dejar un marker `⚠️ pending STORY_XXX` en `outputs/` después de que esa story cierre con ✅.

---

## Regla 2 — Scan obligatorio al completar una story

Cuando se completa cualquier STORY en `context/stories/INDEX.md`, ejecutar antes del commit:

```bash
grep -rn "pending STORY_XXX\|PRELIMINAR.*STORY_XXX" outputs/
```

Donde `XXX` es el número de la story completada. Si hay matches, actualizarlos antes de hacer commit.

---

## Regla 3 — Documentos con validación dependiente

Los siguientes documentos de `outputs/` contienen markers que deben actualizarse cuando las stories correspondientes cierran:

| Documento | Story que lo invalida |
|---|---|
| `outputs/agent_memory_spec.md` | Cualquier STORY de validación de modelos |
| `outputs/workflow_map.md` | Cualquier STORY de validación o de nuevo modelo |
| `outputs/agent_memory_spec.md` sección 3.x | STORY de validación del modelo correspondiente |

---

## Regla 4 — ctx-size nunca hardcodeado en reglas de restricción

Las restricciones de hardware en `core.md` y `project_state.md` deben referenciar los presets validados, no un valor fijo. Un valor fijo se vuelve mentira tan pronto como se valida un ctx mayor.

Formato correcto en documentos de restricción:
- ❌ `ctx-size <= 8192 con Q4_K_M`
- ✅ `ctx-size: ver presets validados en project_state.md — actualmente 24576 (Gemma4) y 40960 (Qwen3)`

---

## Regla 5 — Ciclo de vida de documentos en outputs/

Los documentos en `outputs/` tienen ciclo de vida activo — no son archivos históricos. A diferencia de `inputs/` (read-only histórico), `outputs/` debe mantenerse actualizado.

Triggers de actualización para documentos de outputs/:
- Se completa una STORY de validación → actualizar markers y status en agent_memory_spec.md y workflow_map.md
- Se agrega un nuevo modelo al stack → actualizar workflow_map.md sección 1.3 y topología
- Cambia un preset de hardware → actualizar workflow_map.md sección 4 y project_state.md

---

## Regla 6 — Staleness check en context-close

En cada ejecución de `context-close`, si se completó al menos una STORY en la sesión:
1. Listar las stories completadas
2. Para cada una, hacer el grep de la Regla 2
3. Si hay matches, corregir antes de hacer commit
4. Si los matches son en archivos `🔒 Histórico`, ignorar (son intencionales)
