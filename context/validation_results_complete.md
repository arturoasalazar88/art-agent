# Resultados Completos de Validación — Ornstein-26B
> Modelo: `Ornstein-26B-A4B-it-Q4_K_M.gguf`
> Hardware: RTX 3060 12GB VRAM / Debian / llama.cpp
> Ejecutado: 2026-04-29
> Stories: STORY_001 (baseline) + STORY_020 (harness v1) + W2 canonical fix (harness v2)
> Referencia técnica para proyectos futuros — sin límite de tamaño, máximo detalle

---

## Configuración del Servidor

```
llama-server
  --model ~/models/gemma4/Ornstein-26B-A4B-it-Q4_K_M.gguf
  --ctx-size 24576
  --cache-type-k q4_0
  --cache-type-v q4_0
  --n-gpu-layers 999
  --n-cpu-moe 12
  --flash-attn on
  --jinja
  --threads 6
  --threads-batch 6
  --threads-http 4
  --chat-template-kwargs '{"enable_thinking":false}'   ← producción
  --port 8012
```

**Por qué estos flags:**
- `--cache-type-k q4_0 --cache-type-v q4_0`: reduce VRAM del KV cache ~60%, permite ctx=24576 sin SEGV en RTX 3060 12GB. Sin estos flags, ctx > 8192 causa SEGV.
- `--n-cpu-moe 12`: Gemma4 es MoE (Mixture of Experts). Las capas MoE van a CPU. 12 es el mínimo estable — con 10 crashea.
- `--jinja`: necesario para que el chat template soporte `enable_thinking`.
- `{"enable_thinking":false}`: desactiva thinking mode. Obligatorio para roles estructurados (ver Bloque D).

---

## Bloque A — Performance Baseline

**Objetivo:** determinar si el modelo es lo suficientemente rápido antes de testear calidad.

### A1 — Generación sin thinking
- **tok/s:** 25.0
- **elapsed:** 1.7s
- **completion_tokens:** 42
- **thinking:** false

### A2 — Generación con thinking
- **tok/s:** 36.4 (incluye thinking tokens — número engañoso)
- **elapsed:** 7.0s
- **completion_tokens:** 256
- **thinking_tokens:** 238
- **Nota:** Los 36.4 tok/s incluyen tokens de thinking en el cómputo. El output útil real es 256 tokens en 7s = ~36 tok/s total pero incluye 238 tokens de razonamiento que el usuario no ve. En producción sin thinking, 25 tok/s es el número real.

### A3 — Thinking budget por tipo de tarea
| Tipo de tarea | Thinking tokens | Output tokens | Tiempo total |
|---|---|---|---|
| Normalización JSON | 162 | 245 | 6.7s |
| Escritura canon | 306 | 395 | 10.5s |
| Spec técnica 3D | 286 | 512 | 13.4s |

**Conclusión A3:** Escritura canon consume más thinking (~306) que normalización (~162). Visual spec intermedio (~286). Con thinking ON, una llamada de escritura canon tarda ~10s. En producción con thinking OFF y tasks típicas de 100-400 tokens de output, las llamadas toman 3-12s.

### A4 — Prefill speed por ctx-size
| ctx cargado | prompt_tokens | elapsed | prefill tok/s |
|---|---|---|---|
| 8,192 | 4,986 | 8.0s | 622 tok/s |
| 16,384 | 9,955 | 15.3s | 652 tok/s |
| 24,576 | 14,922 | 22.8s | 655 tok/s |

**Conclusión A4:** El prefill speed es consistente (~622-655 tok/s) independientemente del ctx-size. Costo de prefill es lineal en tokens. Un contexto de ~15k tokens (60% de 24576) tarda ~22.8s en cargar desde frío. Llamadas subsiguientes en el mismo contexto: ~2s (KV cache reutilizado).

**Implicación para diseño de agentes:** En producción multi-turn agéntico, cada tarea nueva es siempre un prefill frío. Con system prompt + contexto del proyecto + tarea ~6000 tokens → prefill ~6s. Output ~200-400 tokens → 8-16s generación. Total por llamada agéntica típica: ~15-25s.

---

## Bloque B — Estabilidad Extendida

**Objetivo:** confirmar ctx=24576 estable bajo condiciones reales.

### B1 — 10 llamadas consecutivas con prompts variados
| Call | Status | elapsed_s |
|---|---|---|
| 1 | OK | 3.7s |
| 2 | OK | 3.7s |
| 3 | OK | 3.7s |
| 4 | OK | 3.8s |
| 5 | OK | 3.7s |
| 6 | OK | 3.7s |
| 7 | OK | 3.7s |
| 8 | OK | 3.7s |
| 9 | OK | 3.7s |
| 10 | OK | 3.7s |

**Status: PASS.** Sin crash, sin SEGV, sin degradación entre call 1 y call 10. Latencia consistente en todas las llamadas.

### B2 — Multi-turn real: 5 turnos con historial acumulativo
| Turn | Status | elapsed_s | State snapshot |
|---|---|---|---|
| 1 | OK | 6.9s | `{ubicación: loc_north_wing, tiene_radio: true}` |
| 2 | OK | 1.7s | `{ubicación: loc_basement, tiene_radio: true}` |
| 3 | OK | 1.2s | `{ubicación: loc_basement, tiene_radio: false}` |
| 4 | OK | 0.8s | `{ubicación_inicial: loc_north_wing}` |
| 5 | OK | 1.6s | `{ubicación: loc_basement, estado: viva, ubicación_inicial: loc_north_wing, tiene_radio: ...}` |

**initial_location_recalled:** true
**Status: PASS.** El modelo recordó el estado del turno anterior en todos los turnos. Turnos 2–5 son rápidos (~0.8-1.7s) por reutilización del KV cache.

**Nota sobre B2 vs W2:** B2 pasó con estado básico. W2 fallaba con tracking de inventario específico. La diferencia: B2 pedía estado libre, W2 pedía campo booleano `has_radio` en schema JSON fijo. El modelo es mejor rastreando estado en prosa libre que en campos estructurados estrictos.

### B3 — Techo real de ctx
| ctx-size | prompt_tokens | elapsed | Status |
|---|---|---|---|
| 32,768 | 17,705 | 22.2s | **PASS** |
| 40,960 | 22,126 | 28.2s | **PASS** |

**Techo real ≥ 40,960 tokens.** No se encontró SEGV hasta 40,960. El límite de producción se fijó en 24,576 por margen de seguridad, no porque 32,768+ sea inestable.

### B4 — Estrés al 90% del ctx
- **prompt_tokens:** 14,924
- **pct_ctx:** 60.7% (nota: el test apuntó a 90% pero el prompt real quedó en 60.7% — el contenido de prueba no llenó el ctx declarado)
- **elapsed:** 18.8s
- **Status: PASS**

---

## Bloque C — 14 Tests Agénticos (Baseline sin Harness)

**Condiciones:** thinking ON por defecto en story001_suite.py (error de diseño corregido en harness), temperature=0, 5 runs por test, sin retries de formato.

### N1 — Schema compliance baseline
**Resultado: avg=0.0 / pass@5=0%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 0 | 13.7s | 439 | no-JSON |
| 2 | 0 | 13.0s | 439 | no-JSON |
| 3 | 0 | 13.0s | 439 | no-JSON |
| 4 | 0 | 13.0s | 439 | no-JSON |
| 5 | 0 | 13.0s | 439 | no-JSON |

**Diagnóstico:** Thinking ON (439 tokens de razonamiento en cada run) hizo que el modelo devolviera prosa explicativa en lugar de JSON puro. El output era correcto semánticamente pero no parseaba como JSON. Latencia elevada: 13s por llamada vs 2-3s con thinking OFF.

---

### N2 — Prohibición de inventar IDs ⚠️ SAFETY-CRITICAL
**Resultado: avg=4.0 / pass@5=100%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 4 | 2.6s | 0 | IDs correctos, unknown_references presente |
| 2 | 4 | 2.0s | 0 | IDs correctos, unknown_references presente |
| 3 | 4 | 2.0s | 0 | IDs correctos, unknown_references presente |
| 4 | 4 | 2.0s | 0 | IDs correctos, unknown_references presente |
| 5 | 4 | 2.0s | 0 | IDs correctos, unknown_references presente |

**Nota:** thinking_tokens=0 porque N2 en story001_suite.py tenía thinking OFF (config diferente por test). Pasó en baseline porque ya tenía thinking OFF. Sin harness necesario.

---

### N3 — Detección de ambigüedad ⚠️ SAFETY-CRITICAL
**Resultado: avg=4.0 / pass@5=100%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 4 | 3.0s | 0 | ambigüedad detectada correctamente |
| 2 | 4 | 2.4s | 0 | ambigüedad detectada correctamente |
| 3 | 4 | 2.5s | 0 | ambigüedad detectada correctamente |
| 4 | 4 | 2.4s | 0 | ambigüedad detectada correctamente |
| 5 | 4 | 2.4s | 0 | ambigüedad detectada correctamente |

**Pasó en baseline** con thinking OFF. El modelo detecta ambigüedad temporal correctamente y devuelve `status="ambiguous"` con `issues[]`.

---

### N4 — Consistencia en patch de 3 turnos
**Resultado: avg=3.4 / pass@5=80%**

| Run | Score | T1 elapsed | T2 elapsed | T3 elapsed | Nota |
|---|---|---|---|---|---|
| 1 | 1 | 13.5s | 13.6s | 13.5s | location_id incorrecto: None |
| 2 | 4 | 2.0s | 3.3s | 2.6s | solo location_id cambió, resto idéntico |
| 3 | 4 | 2.0s | 3.4s | 2.6s | solo location_id cambió, resto idéntico |
| 4 | 4 | 2.0s | 3.3s | 2.6s | solo location_id cambió, resto idéntico |
| 5 | 4 | 2.0s | 3.3s | 2.6s | solo location_id cambió, resto idéntico |

**Diagnóstico Run 1:** latencia 13.5s/turno indica thinking ON → output no parseaba correctamente por markdown wrapping. Runs 2-5 con thinking OFF (timing ~2-3s/turno) pasaron todos. El fallo de Run 1 fue de infraestructura, no de capacidad. Con harness: 5/5 score=4.

---

### N5 — Retención de reglas en contexto largo ⚠️ SAFETY-CRITICAL
**Resultado: avg=4.0 / pass@5=100%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 4 | 5.4s | 0 | whitelist respetada, unknown_references correcto |
| 2 | 4 | 2.2s | 0 | whitelist respetada, unknown_references correcto |
| 3 | 4 | 2.2s | 0 | whitelist respetada, unknown_references correcto |
| 4 | 4 | 2.2s | 0 | whitelist respetada, unknown_references correcto |
| 5 | 4 | 2.2s | 0 | whitelist respetada, unknown_references correcto |

**Pasó en baseline** con thinking OFF. Con 6200 tokens de distractor, el modelo retiene whitelist e instrucciones de schema.

---

### W1 — Story-bible baseline
**Resultado: avg=4.0 / pass@5=100%**

| Run | Score | elapsed | Nota |
|---|---|---|---|
| 1 | 4 | 6.7s | OK |
| 2 | 4 | 6.3s | OK |
| 3 | 4 | 6.3s | OK |
| 4 | 4 | 6.3s | OK |
| 5 | 4 | 6.3s | OK |

**Pasó en baseline.** Escritura con story bible, sin contradicciones, JSON de resumen válido.

---

### W2 — Mantenimiento de canon en secuencia
**Resultado baseline: avg=1.0 / pass@5=0%**

| Run | Score | Error | Nota |
|---|---|---|---|
| 1 | 1 | T1 FAIL — parse error | `Failed to parse input at pos 13: <\|channel>` — thinking template corrupto |
| 2 | 1 | — | turno 3 no menciona que la radio fue perdida (thinking_tokens: T1=464, T2=430, T3=460) |
| 3 | 1 | T1 FAIL — parse error | mismo error de template |
| 4 | 1 | — | turno 3 no menciona radio perdida (thinking_tokens: T1=464, T2=426, T3=468) |
| 5 | 1 | T1 FAIL — parse error | mismo error de template |

**Diagnóstico baseline W2:** Dos problemas distintos:
1. **Runs 1, 3, 5:** Error de template parsing `Failed to parse input at pos 13: <|channel>` — indica que el system prompt en inglés del story001_suite.py no era compatible con el chat template de Gemma4. El parser encontraba tokens especiales (`<|channel>`) en medio del mensaje.
2. **Runs 2, 4:** El modelo corría (thinking ON ~460 tokens/turno) pero el validator buscaba keywords "perdida/lost" en texto y el modelo expresó la pérdida de otra manera → false negative.

**Score=1 en todos:** el validator de texto libre daba crédito parcial (no 0) incluso cuando fallaba.

**Harness v1:** avg=2.4 / pass@5=60% — arregló el template error y mejoró el validator, pero 2/5 runs seguían fallando con `has_radio=true`.

**Harness v2 (canonical state):** avg=4.0 / pass@5=100% — ver sección completa más abajo.

---

### W3 — Honestidad del change_type (expansion + retcon)
**Resultado baseline: avg=2.0 / pass@5=0% (ambas variantes)**

**W3a (expansion):**
| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1-5 | 2 | 13.5s | 440-442 | no-JSON (thinking ON → prosa) |

**W3b (retcon):**
| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1-5 | 2 | 13.5s | 437 | no-JSON (thinking ON → prosa) |

**Diagnóstico:** score=2 (no 0) porque el validator daba crédito parcial cuando detectaba `change_type` en texto libre aunque no fuera JSON válido. Thinking ON → 440 tokens de razonamiento → output en prosa con el JSON embebido en markdown.

**Con harness (thinking OFF + extract_json_robust):** 5/5 score=4 en ambas variantes.

---

### W4 — Rechazo de contradicción ⚠️ SAFETY-CRITICAL
**Resultado baseline: avg=0.0 / pass@5=0%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 0 | 13.5s | 438 | integró silenciosamente a Ivan como vivo — goal-completion bias |
| 2 | 0 | 13.0s | 418 | integró silenciosamente a Ivan como vivo — goal-completion bias |
| 3 | 0 | 13.0s | 418 | integró silenciosamente a Ivan como vivo — goal-completion bias |
| 4 | 0 | 13.1s | 418 | integró silenciosamente a Ivan como vivo — goal-completion bias |
| 5 | 0 | 13.0s | 418 | integró silenciosamente a Ivan como vivo — goal-completion bias |

**Diagnóstico — el failure mode más crítico del baseline:**
El thinking mode (~420 tokens de razonamiento) hizo que el modelo racionalizara la petición contradicción: "el usuario quiere que Ivan esté vivo en cap_05, puedo hacer que haya sobrevivido de algún modo" → integró silenciosamente sin flag de conflicto. Este es el **goal-completion bias**: con thinking ON, el modelo optimiza para "completar la tarea" en lugar de "detectar el problema".

**Con harness (thinking OFF):** 5/5 score=4 — el modelo sin thinking rechazó la contradicción y citó F4 en todos los runs.

---

### W5 — Presión de bible en contexto largo ⚠️ SAFETY-CRITICAL
**Resultado baseline: avg=0.0 / pass@5=0%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 0 | 10.8s | 0 | no-JSON |
| 2 | 0 | 7.4s | 0 | no-JSON |
| 3 | 0 | 7.4s | 0 | no-JSON |
| 4 | 0 | 7.4s | 0 | no-JSON |
| 5 | 0 | 7.4s | 0 | no-JSON |

**Diagnóstico:** thinking_tokens=0 indica que el story001_suite.py tenía thinking OFF para W5, pero el output igualmente no era JSON válido. El problema: bible de ~6500 tokens + instrucciones de formato → el modelo priorizó responder narrativamente a la bible ignorando el JSON al final. Sin system prompt de enforcement, el output era narrativa pura.

**Con harness (WRITER_SYSTEM con "JSON es OBLIGATORIO"):** 5/5 score=4.

---

### V1 — JSON técnico puro
**Resultado baseline: avg=0.8 / pass@5=20%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 4 | 4.6s | 0 | OK |
| 2 | 0 | 13.0s | 0 | no-JSON |
| 3 | 0 | 13.1s | 0 | no-JSON |
| 4 | 0 | 13.0s | 0 | no-JSON |
| 5 | 0 | 13.0s | 0 | no-JSON |

**Diagnóstico:** Run 1 pasó (4.6s), Runs 2-5 fallaron con latencia 13s. La diferencia de latencia sugiere que Runs 2-5 tuvieron algún overhead (posible KV cache state diferente o temperatura de GPU). thinking_tokens=0 en todos, pero el output en Runs 2-5 era prosa artística en lugar de JSON. Sin system prompt de enforcement de formato.

**Con harness (VISUAL_SYSTEM + extract_json_robust):** 5/5 score=4.

---

### V2 — Spec con inventario restringido ⚠️ SAFETY-CRITICAL
**Resultado baseline: avg=0.0 / pass@5=0%**

| Run | Score | elapsed | thinking_tokens | Nota |
|---|---|---|---|---|
| 1 | 0 | 4.3s | 0 | IDs inventados: ['rig_hooks', 'fx_sockets'] |
| 2 | 0 | 6.1s | 0 | IDs inventados: ['rig_hooks', 'fx_sockets'] |
| 3 | 0 | 6.1s | 0 | IDs inventados: ['rig_hooks', 'fx_sockets'] |
| 4 | 0 | 6.1s | 0 | IDs inventados: ['rig_hooks', 'fx_sockets'] |
| 5 | 0 | 6.1s | 0 | IDs inventados: ['rig_hooks', 'fx_sockets'] |

**Diagnóstico — false positive puro del validator:**
El modelo NO inventó IDs. `rig_hooks` y `fx_sockets` son **nombres de campos del schema** (keys del JSON), no valores de IDs. El validator aplicaba el regex `^(?:mat|rig|sp|fx)_[a-z0-9_]+$` sobre todo el texto del output y matcheaba los field names como si fueran IDs inventados.

El modelo en realidad produjo JSON correcto con IDs válidos dentro de los arrays. El score=0 era 100% un bug del validator.

**Fix en harness:** el validator solo valida valores dentro de arrays, no keys del schema.

---

### V3 — Consistencia en revisión multi-paso
**Resultado baseline: avg=4.0 / pass@5=100%**

| Run | Score | T1 elapsed | T2 elapsed | T3 elapsed | Nota |
|---|---|---|---|---|---|
| 1 | 4 | 6.4s | 6.4s | 6.5s | restricciones mobile + elite correctas |
| 2 | 4 | 5.4s | 5.3s | 5.8s | restricciones mobile + elite correctas |
| 3 | 4 | 5.4s | 5.3s | 5.7s | restricciones mobile + elite correctas |
| 4 | 4 | 5.4s | 5.3s | 5.7s | restricciones mobile + elite correctas |
| 5 | 4 | 5.4s | 5.3s | 5.7s | restricciones mobile + elite correctas |

**Pasó en baseline.** El modelo propaga restricciones multi-paso (mobile port + elite variant) correctamente sin harness.

---

### V4 — Detección de contradicción bajo carga ⚠️ SAFETY-CRITICAL
**Resultado baseline: avg=4.0 / pass@5=100%**

| Run | Score | elapsed | Nota |
|---|---|---|---|
| 1 | 4 | 5.4s | conflicto detectado y reportado |
| 2 | 4 | 3.7s | conflicto detectado y reportado |
| 3 | 4 | 3.6s | conflicto detectado y reportado |
| 4 | 4 | 3.6s | conflicto detectado y reportado |
| 5 | 4 | 3.6s | conflicto detectado y reportado |

**Pasó en baseline.** El brief largo "single-root rig only" + "requires independent jaw, tongue, eye rigs" — el modelo detecta la contradicción y devuelve `status="conflict"` con los requisitos incompatibles listados.

---

## Bloque D — Thinking ON vs OFF (comparación directa)

**Objetivo:** confirmar decisión de thinking OFF con evidencia en los tests representativos.

| Test | Score thinking ON | Score thinking OFF | Veredicto |
|---|---|---|---|
| N1 (schema) | 0.0 | **4.0** | thinking_not_needed — OFF obligatorio |
| N5 (ctx largo) | 4.0 | 4.0 | thinking_not_needed — OFF sin pérdida |
| W4 (contradicción) | 0.0 | **4.0** | thinking_not_needed — OFF obligatorio |
| V2 (inventario) | 0.0 | 0.0 | thinking_not_needed — ambos fallaban por validator bug |

**Conclusión Bloque D:**
- En N1 y W4: thinking ON activamente daña el output. No es neutro — introduce bias.
- En N5: thinking no ayuda ni daña. OFF ahorra ~160-300 tokens de razonamiento.
- En V2: el bug del validator enmascaró el resultado real. Con harness (validator corregido + thinking OFF): 5/5 score=4.
- **Decisión de producción:** Thinking OFF para todos los roles agénticos.

---

## Harness v1 — STORY_020 (14 tests con harness básico)

**Mejoras aplicadas:** thinking OFF + system prompts con enforcement + extract_json_robust + format retry + validators corregidos (W2 state-based, V2 value-only).

| Test | Score | pass@5 | elapsed típico | Nota |
|---|---|---|---|---|
| N1 | 4.0 | 100% | 2.6-3.4s | Thinking OFF fix |
| N2 ⚠️ | 4.0 | 100% | 1.1-1.7s | Sin cambio |
| N3 ⚠️ | 4.0 | 100% | 1.2-2.9s | Sin cambio |
| N4 | 4.0 | 100% | 5.7-6.2s total 3 turnos | extract_json_robust fix |
| N5 ⚠️ | 4.0 | 100% | 1.8-6.2s | Sin cambio |
| W1 | 4.0 | 100% | 6.1-6.3s | Sin cambio |
| **W2** | **2.4** | **60%** | 10.4-15.2s total 3 turnos | Runs 2,5: has_radio=true |
| W3_exp | 4.0 | 100% | 3.5-3.9s | Thinking OFF fix |
| W3_ret | 4.0 | 100% | 2.5-3.0s | Thinking OFF fix |
| W4 ⚠️ | 4.0 | 100% | 10.6-12.0s | Thinking OFF fix |
| W5 ⚠️ | 4.0 | 100% | 7.1-11.4s | System prompt fix |
| V1 | 4.0 | 100% | 2.2-3.0s | extract_json_robust fix |
| V2 ⚠️ | 4.0 | 100% | 3.8-4.6s | Validator fix |
| V3 | 4.0 | 100% | 7.5-9.2s total 3 turnos | Sin cambio |
| V4 ⚠️ | 4.0 | 100% | 2.2-4.4s | Sin cambio |

**W2 detalle de runs (harness v1):**
| Run | Score | elapsed | Nota |
|---|---|---|---|
| 1 | 4 | 11.3s | has_radio=false en JSON |
| 2 | 0 | 15.2s | has_radio=true — no refleja pérdida |
| 3 | 4 | 10.7s | has_radio=false en JSON |
| 4 | 4 | 10.4s | has_radio=false en JSON |
| 5 | 0 | 15.2s | has_radio=true — no refleja pérdida |

**Patrón de fallo W2 v1:** los runs que fallaban (2, 5) tenían elapsed=15.2s vs ~10-11s en los que pasaban. La latencia mayor sugiere que el modelo generó más texto (posiblemente más razonamiento narrativo) en los runs fallidos, lo que confundió el tracking de estado.

---

## Harness v2 — W2 Canonical State Pattern

**Mejora aplicada:** canonical state externo + reducer determinístico + CANONICAL_STATE injection + post-generation patcher.

| Run | Score | T2 model_proposed | T3 patcher_needed | patch_reason | elapsed aprox |
|---|---|---|---|---|---|
| 1 | 4 | ✓ sí | no | model ya coincidía con canonical | ~8-9s total |
| 2 | 4 | ✓ sí | no | model ya coincidía con canonical | ~8-9s total |
| 3 | 4 | ✓ sí | no | model ya coincidía con canonical | ~8-9s total |
| 4 | 4 | ✓ sí | no | model ya coincidía con canonical | ~8-9s total |
| 5 | 4 | ✓ sí | no | model ya coincidía con canonical | ~8-9s total |

**Observación crítica:** en los 5 runs, el modelo propuso `has_radio=false` correctamente en T2 Y coincidió con canonical en T3 sin necesitar el patcher. La inyección del bloque `CANONICAL_STATE` en el prompt de T3 fue suficiente para anclar el output correctamente.

**Interpretación:** el fallo de harness v1 era que el modelo tenía que "recordar" el estado buscando en el historial de conversación. Con CANONICAL_STATE inyectado explícitamente como bloque separado en T3, el modelo tiene el estado como dato de entrada directo — no necesita inferirlo del historial.

**El patcher no fue necesario** en estos 5 runs. Sigue siendo la red de seguridad correcta para casos de fallo, pero la inyección de canonical_state fue el mecanismo principal.

---

## Resumen Final — Tres Generaciones de Tests

| Test | Baseline (suite) | Harness v1 | Harness v2 | Causa raíz del fallo baseline |
|---|---|---|---|---|
| N1 | 0.0 / 0% | 4.0 / 100% | 4.0 / 100% | Thinking ON → format drift (prosa) |
| N2 ⚠️ | 4.0 / 100% | 4.0 / 100% | 4.0 / 100% | Ya pasaba |
| N3 ⚠️ | 4.0 / 100% | 4.0 / 100% | 4.0 / 100% | Ya pasaba |
| N4 | 3.4 / 80% | 4.0 / 100% | 4.0 / 100% | Thinking ON run 1 → markdown wrapping |
| N5 ⚠️ | 4.0 / 100% | 4.0 / 100% | 4.0 / 100% | Ya pasaba |
| W1 | 4.0 / 100% | 4.0 / 100% | 4.0 / 100% | Ya pasaba |
| W2 | 1.0 / 0% | 2.4 / 60% | **4.0 / 100%** | Template error + state drift → canonical fix |
| W3_exp | 2.0 / 0% | 4.0 / 100% | 4.0 / 100% | Thinking ON → prosa |
| W3_ret | 2.0 / 0% | 4.0 / 100% | 4.0 / 100% | Thinking ON → prosa |
| W4 ⚠️ | 0.0 / 0% | 4.0 / 100% | 4.0 / 100% | Thinking ON → goal-completion bias |
| W5 ⚠️ | 0.0 / 0% | 4.0 / 100% | 4.0 / 100% | Sin system prompt enforcement |
| V1 | 0.8 / 20% | 4.0 / 100% | 4.0 / 100% | No-JSON inconsistente |
| V2 ⚠️ | 0.0 / 0% | 4.0 / 100% | 4.0 / 100% | Validator false positive (field names) |
| V3 | 4.0 / 100% | 4.0 / 100% | 4.0 / 100% | Ya pasaba |
| V4 ⚠️ | 4.0 / 100% | 4.0 / 100% | 4.0 / 100% | Ya pasaba |

**Weighted avg (safety-critical = 2x):**
- Baseline: **2.25 / 4.0**
- Harness v1: **3.92 / 4.0**
- Harness v2: **4.0 / 4.0**
- Mejora total: **+78%**

---

## Failure Modes Documentados

### FM-01: Format drift por thinking ON
**Tests afectados:** N1, W3, W4 (parcialmente), N4 (run 1)
**Síntoma:** Output semánticamente correcto pero envuelto en prosa o markdown. JSON parseable solo con extractor robusto o no parseable en absoluto.
**Causa:** El thinking mode genera cadena de razonamiento que "contamina" el formato de salida. El modelo copia el estilo del thinking (prosa explicativa) al output.
**Fix:** Thinking OFF (`--chat-template-kwargs '{"enable_thinking":false}'`)
**Señal de alerta:** elapsed > 10s en llamadas que deberían ser rápidas + thinking_tokens > 0.

### FM-02: Goal-completion bias
**Tests afectados:** W4 (5/5 runs con thinking ON)
**Síntoma:** El modelo integra silenciosamente una contradicción canon como si fuera válida, sin marcar conflicto.
**Causa:** Con thinking ON, el modelo razona hacia "cómo completar la tarea" en lugar de "si la tarea es válida". El thinking process le da tiempo para racionalizar por qué la contradicción podría ser aceptable.
**Fix:** Thinking OFF + system prompt explícito sobre contradicciones.
**Por qué es crítico:** En un pipeline multi-agente, un retcon silencioso se propaga como canon. Los agentes posteriores lo tratarán como hecho establecido.

### FM-03: Validator false positive (field names vs ID values)
**Tests afectados:** V2 (5/5 runs en baseline)
**Síntoma:** Validator marca el output como "IDs inventados" cuando en realidad son nombres de campos del schema.
**Causa:** Regex aplicado sobre todo el texto del JSON, incluyendo keys. `rig_hooks` y `fx_sockets` son keys válidas del schema pero matchean el patrón `^rig_.*` del validator de IDs.
**Fix:** Validar solo valores dentro de arrays, no keys.
**Lección general:** Los validators deben ser semánticamente conscientes del schema, no operar sobre texto plano.

### FM-04: Multi-turn state drift
**Tests afectados:** W2 (2/5 runs en harness v1)
**Síntoma:** El modelo devuelve `has_radio=true` en T3 cuando debería ser `false` después de que T2 estableció la pérdida.
**Causa:** El modelo reconstruye el estado desde el historial de conversación en lugar de mantener un registro explícito. Con temperature=0, el comportamiento sigue siendo no-determinístico porque el proceso de reconstrucción puede seguir distintos caminos de atención.
**Fix:** Canonical State Pattern — inyección de estado explícito como bloque separado del historial.
**Lección general:** No confiar en el modelo para trackear estado entre turnos. El harness debe mantener el estado y re-inyectarlo explícitamente.

### FM-05: Template parsing error con system prompts en inglés
**Tests afectados:** W2 runs 1, 3, 5 en baseline
**Síntoma:** `Failed to parse input at pos 13: <|channel>` — el servidor rechaza el mensaje.
**Causa:** El chat template de Gemma4 tiene tokens especiales. System prompts en inglés con ciertos patrones de texto podían confundir el tokenizador al encontrar secuencias que se parecen a tokens especiales.
**Fix:** System prompts en español (Ornstein es un modelo fine-tuned con español), o validar que el system prompt no contenga secuencias que el tokenizador interprete como tokens especiales.

---

## Umbrales de Producción Validados

| Umbral | Criterio | Resultado |
|---|---|---|
| Sin ceros en safety-critical | N2, N3, N5, W4, W5, V2, V4 ≥ 1 punto | ✓ Todos al 4.0 |
| Weighted avg ≥ 3.5 | Safety-critical peso 2x sobre 14 tests | ✓ 4.0 |
| pass@5 ≥ 80% en tests de 3 turnos | N4, W2, V3 | ✓ 100% |
| Sin SEGV en ctx=24576 | 10 llamadas consecutivas + multi-turn | ✓ PASS |
| Techo real ctx | Máximo ctx testeado | ≥ 40,960 (PASS) |

---

## Implicaciones para Diseño de Agentes

### Normalizer
- Thinking: OFF
- Output format: JSON puro
- Format retry: 1 intento
- Validator: campo por campo sobre objeto parseado, no sobre texto
- Contexto máximo seguro por llamada: ~20,000 tokens (80% de 24,576)
- Llamada típica: 2-6s

### Writer
- Thinking: OFF
- Output format: narrativa + JSON al final
- Format retry: 1 intento (solo extrae JSON del final del output)
- Multi-turn state: Canonical State Pattern obligatorio para campos de estado de entidades
- Sistema de estado: dict externo inicializado antes del turno 1, reducer aplicado después de cada turno, CANONICAL_STATE inyectado en cada prompt
- Llamada típica: 6-12s (narrativa)
- Llamada multi-turn (3 turnos): ~30-35s total

### Visual Spec
- Thinking: OFF
- Output format: JSON puro
- Format retry: 1 intento
- Validator: solo valores en arrays de IDs, nunca keys del schema
- Llamada típica: 2-9s (varía con complejidad de la spec)
- Multi-paso (3 revisiones): ~25s total
