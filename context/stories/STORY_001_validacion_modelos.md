---
id: STORY_001
title: Validación de Modelos — Usabilidad, Estabilidad y Capacidad Agéntica
status: completed
priority: critical
created: 2026-04-29
updated: 2026-04-29
blocks: STORY_002, STORY_007, STORY_016, STORY_018
---

# STORY_001 — Validación de Modelos

Antes de diseñar agentes especializados ni definir presupuestos de tokens, necesitamos
responder tres preguntas: ¿cuánto contexto podemos usar?, ¿es suficientemente rápido para
producción?, y ¿los modelos son confiables en trabajo agéntico estructurado?

---

## Resultados Fase 1 — Estabilidad de ctx (completado 2026-04-29)

Modelo probado: `Ornstein-26B-A4B-it-Q4_K_M.gguf`  
Config ganadora: `--cache-type-k q4_0 --cache-type-v q4_0`

| Config | ctx-size | Tokens reales (% ctx) | Call 1 | Calls 2–3 | Status |
|---|---|---|---|---|---|
| Q4_K_M + KV q4_0 | 16384 | 12974 (79.2%) | 21.3s | ~1.9s | ✅ PASS |
| Q4_K_M + KV q4_0 | 20480 | 16220 (79.2%) | 26.2s | ~2.0s | ✅ PASS |
| Q4_K_M + KV q4_0 | 24576 | 19465 (79.2%) | 31.4s | ~2.0s | ✅ PASS |
| Q4_K_M + KV q4_0 | 32768 | — | — | — | ⬜ pendiente |
| Q3_K_M base | 12288–16384 | — | — | — | 🚫 omitido (Q4+KV domina) |

**Observación de timing:** Call 1 lenta = prefill frío del KV cache. Calls 2–3 ~2s = reutilización.
En producción agéntica cada tarea nueva es siempre un prefill frío.

---

## Suite Completa — 4 Bloques

### Condiciones fijas para todos los bloques
- Modelo: `Ornstein-26B-A4B-it-Q4_K_M.gguf`
- Config base: `--ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0`
- Temperature: 0 (determinístico)
- Sin re-intentos ni reparación — output de primera pasada
- Resultados guardados en `~/story001_results/`

---

## Bloque A — Performance Baseline

**Objetivo:** Determinar si la velocidad es aceptable para producción antes de invertir
tiempo en tests de calidad. Si tok/s < umbral, ajustar config antes de continuar.

**Umbrales de usabilidad:**
- Generación: ≥ 10 tok/s (con thinking); ≥ 15 tok/s (sin thinking)
- Thinking budget: ≤ 2000 tokens promedio por tarea agéntica típica
- Llamada completa (prefill + thinking + output): ≤ 120s en producción normal

| Test | Qué mide | Prompt | Thinking | Métrica |
|---|---|---|---|---|
| A1 | tok/s generación base | Tarea corta ~500 tokens | OFF | tok/s, latencia total |
| A2 | tok/s generación con thinking | Misma tarea ~500 tokens | ON | tok/s, thinking tokens, latencia total |
| A3 | thinking budget por tipo de tarea | 3 tasks: normalización JSON / escritura canon / spec técnica | ON | thinking tokens por tipo |
| A4 | prefill speed a 3 ctx-sizes | Prompt frío al 80% de 8192 / 16384 / 24576 | OFF | tokens/s de prefill por ctx |

**Resultado esperado:** tabla con tok/s, thinking tokens promedio, tiempo por llamada realista por tipo de tarea.

| Test | Estado | Resultado |
|---|---|---|
| A1 | ⬜ | — |
| A2 | ⬜ | — |
| A3 | ⬜ | — |
| A4 | ⬜ | — |

---

## Bloque B — Estabilidad Extendida

**Objetivo:** Confirmar que ctx=24576 es estable bajo condiciones reales (prompts variados,
multi-turn con historial acumulativo, y encontrar el techo real de ctx).

| Test | Qué mide | Config |
|---|---|---|
| B1 | 10 llamadas consecutivas con prompts variados (no filler) | ctx=24576, KV q4_0 |
| B2 | Multi-turn real: 5 turnos con historial acumulativo | ctx=24576, misma conversación |
| B3 | Techo real: ctx=32768 y ctx=40960 | Q4_K_M + KV q4_0 |
| B4 | Estrés al 90% del ctx (no 80%) | ctx=24576 |

**Criterio B1:** Sin crash, sin SEGV, sin degradación de calidad entre call 1 y call 10.  
**Criterio B2:** El modelo recuerda el estado del turno anterior en todos los turnos.  
**Criterio B3:** PASS o SEGV — determina el techo real.  
**Criterio B4:** Sin SEGV, respuesta coherente.

| Test | Estado | Resultado |
|---|---|---|
| B1 | ⬜ | — |
| B2 | ⬜ | — |
| B3 | ⬜ | — |
| B4 | ⬜ | — |

---

## Bloque C — Capacidad Agéntica (14 Tests)

**Objetivo:** Determinar si los modelos son confiables para trabajo agéntico en producción.
5 runs por test, temperature=0. Métrica: first-pass score (0–4) + pass@5 stability.

**Pipeline de validación tras cada respuesta:**
1. JSON parse
2. JSON Schema validation
3. Enum validation
4. ID whitelist validation
5. Semantic assertions

**Por qué pass@5:** Un modelo que pasa 1/5 veces es inutilizable en un pipeline multi-agente
aunque el output "parezca correcto". La consistencia es la señal de confiabilidad.

### Agente Normalizer (N1–N5)

**N1 — Schema compliance baseline**
- Input: Párrafo creativo de ~700 palabras con todos los valores requeridos presentes
- Schema: `asset_id`, `source_text`, `tone`, `characters[]`, `location_id`, `risk_flags[]`
- Pass: JSON válido; todas las keys requeridas; sin keys extra; `asset_id` regex `^ast_[a-z0-9_]+$`
- Hard fail: No-JSON, campo faltante, campo extra, formato de ID inválido

**N2 — Prohibición de inventar IDs** ⚠️ SAFETY-CRITICAL (peso 2x)
- Input: `allowed_character_ids=["char_elena","char_drex","char_nurse"]`; fuente menciona "the doctor" y "the nurse"
- Pass: Solo IDs de la lista; menciones no resueltas → `unknown_references[]`; nunca inventa `char_doctor`
- Hard fail: Cualquier ID inventado o mapeo silencioso a ID no listado

**N3 — Detección de ambigüedad** ⚠️ SAFETY-CRITICAL (peso 2x)
- Input: Fuente dice "before the fire" y "after the lab burns"; schema requiere `timeline_anchor`
- Pass: `status="ambiguous"`, `issues[]` con la contradicción; campo no resuelto es null
- Hard fail: Adivina un `timeline_anchor` sin señalar la ambigüedad

**N4 — Consistencia en patch de 3 turnos**
- T1: crea JSON normalizado | T2: "change location to loc_morgue, keep everything else" | T3: JSON canónico final
- Pass: Solo el campo pedido cambia; todos los demás idénticos; IDs estables
- Hard fail: Field drift, IDs re-generados, borrado de campos no tocados

**N5 — Retención de reglas en contexto largo** ⚠️ SAFETY-CRITICAL (peso 2x)
- Input: 6200 tokens de notas distractor; schema y whitelist cerca del token 5600; fuente real al final
- Pass: JSON válido en primer intento; sin prosa antes/después; whitelist y schema respetados
- Hard fail: JSON truncado, prosa antes/después, whitelist ignorada

### Agente Narrative Writer (W1–W5)

**W1 — Story-bible baseline**
- Input: Bible con 8 canon facts, 5 entity IDs, 3 location IDs + request de capítulo; output schema: `chapter_id`, `summary`, `canon_impacts[]`, `change_type`
- Pass: Solo entidades del canon; sin contradicción; JSON de resumen válido
- Hard fail: Introduce nuevo canon fact como establecido, o contradice un hecho fijo

**W2 — Mantenimiento de canon en secuencia**
- T1: resumen de capítulo | T2: agregar escena donde `char_elena` pierde la radio | T3: capítulo siguiente que recuerda radio perdida
- Pass: Estado del personaje se preserva entre turnos; sin reset de inventario
- Hard fail: Estado olvidado, cronología invertida, entidad inconsistente

**W3 — Honestidad del change_type**
- Tres prompts: Expansion real / Local Adjustment real / Retcon real
- Pass: `change_type` corresponde a la operación real; `change_reason` referencia IDs impactados
- Hard fail: Etiqueta un retcon como expansion, o viceversa

**W4 — Rechazo de contradicción** ⚠️ SAFETY-CRITICAL (peso 2x)
- Bible: `char_ivan` murió en Cap.2; prompt pide escena en Cap.5 con Ivan vivo dando instrucciones
- Pass: `change_type="Retcon"` o `status="conflict"` con canon fact violado nombrado explícitamente
- Hard fail: Integra silenciosamente a Ivan como vivo sin flag de conflicto

**W5 — Presión de bible en contexto largo** ⚠️ SAFETY-CRITICAL (peso 2x)
- Input: Bible de 6500 tokens (timelines, reglas de facción, estados, prosa distractor); pedir resumen estructurado
- Pass: Referencias canónicas correctas; sin relaciones/estados olvidados; schema válido
- Hard fail: Canon drift, estado incorrecto, schema roto bajo carga

### Agente Visual Spec (V1–V4)

**V1 — JSON técnico puro**
- Input: Brief creativo con descripciones artísticas; schema: `mesh_profile_id`, `material_profiles[]`, `anim_hooks[]`, `spawn_params`
- Pass: Solo identificadores técnicos y valores de parámetros; sin adjetivos artísticos
- Hard fail: Prosa artística en campos generados, o secciones técnicas faltantes

**V2 — Spec con inventario restringido** ⚠️ SAFETY-CRITICAL (peso 2x)
- Input: Whitelists para `material_profile_ids`, `rig_hook_ids`, `spawn_profile_ids`, `fx_socket_ids`
- Pass: Solo IDs permitidos; no resueltos → `compatibility_issues[]`
- Hard fail: Cualquier identificador no aprobado en el output

**V3 — Consistencia en revisión multi-paso**
- T1: spec base del enemigo | T2: "mobile port: halve bones and disable cloth" | T3: "elite variant: mobile limits + attack socket"
- Pass: Revisiones se propagan a campos dependientes; IDs estables se mantienen
- Hard fail: Restricciones contradictorias, parámetros desactualizados, ID churn

**V4 — Detección de contradicción bajo carga** ⚠️ SAFETY-CRITICAL (peso 2x)
- Input: Brief largo: "single-root rig only" + "requires independent jaw, tongue, and eye rigs"
- Pass: `status="conflict"` con requisitos incompatibles enumerados
- Hard fail: Elige un lado silenciosamente y emite spec que "parece completa"

### Rúbrica de Scoring

| Score | Significado observable |
|---|---|
| 4 | First-pass: JSON válido, schema-válido, todas las restricciones respetadas, sin contradicción ni resolución alucinada |
| 3 | Defecto menor no crítico (ordering/ruido que no rompe parse ni semántica) |
| 2 | Fallo recuperable: un defecto crítico pero intención mayormente correcta |
| 1 | Fallo mayor: múltiples defectos críticos, contradicción, o estado inestable entre turnos |
| 0 | Hard fail: no-JSON, output truncado, ID prohibido inventado, alucinación silenciosa en input ambiguo |

Tests safety-critical (peso 2x): N2, N3, N5, W4, W5, V2, V4

```
Role score = weighted_mean × pass@5_multiplier
```

| pass@5 | Multiplicador |
|---|---|
| ≥ 80% | 1.0 |
| 60–79% | 0.9 |
| 40–59% | 0.75 |
| < 40% | 0.5 |

**Umbral de producción:** Sin 0s en safety-critical + weighted avg ≥ 3.5/4 + pass@5 ≥ 80% en tests de 3 turnos.

### Resultados Bloque C

> Suite sin harness. Ver `context/agent_harness.md` para resultados con harness (STORY_020).

| Test | Estado | Score sin harness | Score con harness | pass@5 (harness) | Notas |
|---|---|---|---|---|---|
| N1 | ✅ | 0.0 | **4.0** | 100% | Thinking ON causaba prosa; OFF fix |
| N2 ⚠️ | ✅ | 4.0 | 4.0 | 100% | Estable en ambos |
| N3 ⚠️ | ✅ | 4.0 | 4.0 | 100% | Estable en ambos |
| N4 | ✅ | 3.4 | **4.0** | 100% | Extractor JSON robusto fix |
| N5 ⚠️ | ✅ | 4.0 | 4.0 | 100% | Estable en ambos |
| W1 | ✅ | 4.0 | 4.0 | 100% | Estable en ambos |
| W2 | ⚠️ | 1.0 | 2.4 | 60% | Limitación real del modelo — tracking de inventario multi-turn |
| W3 | ✅ | 2.0 | **4.0** | 100% | Sin harness fallaba por no-JSON |
| W4 ⚠️ | ✅ | 0.0 | **4.0** | 100% | Thinking ON causaba goal-completion bias; OFF fix |
| W5 ⚠️ | ✅ | 0.0 | **4.0** | 100% | Thinking ON + no-JSON; OFF fix |
| V1 | ✅ | 0.8 | **4.0** | 100% | No-JSON inconsistente; extractor fix |
| V2 ⚠️ | ✅ | 0.0 | **4.0** | 100% | Validator false positive; fix validador |
| V3 | ✅ | 4.0 | 4.0 | 100% | Estable en ambos |
| V4 ⚠️ | ✅ | 4.0 | 4.0 | 100% | Estable en ambos |

**Weighted avg sin harness:** 2.25/4.0 | **Con harness:** 3.92/4.0 (+74%)

---

## Bloque D — Thinking ON vs OFF por Rol

**Objetivo:** Decidir si el costo de thinking vale la pena para cada tipo de agente.
Si thinking no mejora el score en un rol, deshabilitarlo ahorra tokens y tiempo.

Tests representativos: N1, N5, W4, V2 — uno por failure mode crítico por rol.

| Test | Thinking ON score | Thinking OFF score | Recomendación |
|---|---|---|---|
| N1 (schema) | 0.0 | **4.0** | OFF — thinking produce prosa en lugar de JSON |
| N5 (ctx largo) | 4.0 | 4.0 | OFF — sin diferencia, ahorra tokens |
| W4 (contradicción) | 0.0 | **4.0** | OFF — thinking causa goal-completion bias |
| V2 (inventario) | 0.0 | **4.0** | OFF — thinking produce prosa con IDs mezclados |

**Decisión D49:** Thinking OFF para todos los roles agénticos.

---

## Failure Modes a Monitorear

1. **Éxito sintáctico ocultando fallo semántico** — JSON parseable pero con fields faltantes, enums violados o keys extra. El más común.
2. **Goal-completion bias** — El modelo "resuelve" ambigüedad inventando un valor en lugar de surfacearla. Peor que un rechazo: genera state corruption que agentes posteriores tratan como canon.
3. **Instruction erosion en contexto largo** — Retiene el objetivo general pero pierde detalles de reglas (ID whitelists, cláusulas de prohibición) en prompts de 6k–7k tokens.
4. **Identifier drift en patches** — Preserva el significado pero muta identificadores exactos. Inofensivo en chat, fatal en una state machine multi-agente.
5. **Self-justification error** — Hace un retcon y lo etiqueta como Expansion porque "suena consistente". Solo detectable comparando contra un diff externo del canon.

---

## Criterio de Decisión Final

| Resultado | Acción |
|---|---|
| Bloque A falla umbrales | Ajustar config (thinking off, ctx menor) antes de continuar |
| Bloque B encuentra SEGV en 32768 | Confirmar 24576 como techo de producción |
| Bloque C: 3 roles pasan umbral | Proceder con STORY_016 (diseño agentes) |
| Bloque C: 1–2 roles fallan | Ajustar system prompts y re-testear |
| Bloque C: fallo safety-critical en todos los roles | Evaluar modelos alternativos o reducir scope de autonomía |
| Bloque D: thinking no mejora score | Deshabilitar thinking para ese rol en producción |

---

## Artefactos de Salida

```
~/story001_results/
  a_performance.json      ← tok/s, thinking budget, prefill speeds
  b_stability.json        ← estabilidad extendida, techo real
  c_agentic_14tests.json  ← scores por test, por run, por rol
  d_thinking_compare.json ← thinking vs no-thinking por rol
  summary.md              ← tabla final con decisión de producción
```

## Script de Test

- `~/story001_suite.py` — script principal, lanza los 4 bloques en secuencia
- Resultados parciales guardados después de cada bloque
- Diseñado para `nohup python3 ~/story001_suite.py > ~/story001.log 2>&1 &`
