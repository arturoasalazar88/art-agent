---
id: STORY_020
title: Agent Harness — Sistema de Reglas por Rol + Re-run de Tests
status: completed
priority: critical
created: 2026-04-29
depends_on: STORY_001
blocks: STORY_007, STORY_016
---

# STORY_020 — Agent Harness

STORY_001 demostró que el modelo tiene la capacidad pero los tests fallaron por
infraestructura: thinking mode incorrecto, system prompts sin enforcement de formato,
validators frágiles. Este harness implementa las reglas derivadas de esos resultados
y re-corre los 14 tests para obtener scores limpios sobre los que diseñar los agentes.

---

## Hallazgos que motivan este harness

| Hallazgo | Evidencia | Solución |
|---|---|---|
| Thinking ON perjudica output estructurado | N1: 0→4, W4: 0→4 al apagar thinking | Thinking OFF por defecto para tasks estructurados |
| Modelo envuelve JSON en markdown | N1, W3, W5, V1 fallan por `\`\`\`json\`\`\`` | Post-procesado: strip markdown antes de validar |
| Sin enforcement de formato en system prompt | Mismo modelo pasa con OFF+buen prompt | System prompts explícitos con OUTPUT FORMAT |
| Un retry de formato recupera fallos simples | Modelo sabe el formato, solo necesita corrección | Un retry si no-JSON, sin reintentar fallos semánticos |
| Validators frágiles (W2 keyword, V2 false positive) | W2 busca "perdida", V2 confunde field names con IDs | Validators semánticos basados en estado, no keywords |

---

## Arquitectura del Harness

### Reglas por Rol

```python
ROLE_RULES = {
    "normalizer": {
        "thinking": False,          # OFF — thinking causa goal-completion bias en JSON
        "system_prompt": NORMALIZER_SYSTEM,
        "output_format": "json_only",
        "format_retry": True,       # un retry si no-JSON
        "max_retries": 1,
    },
    "writer": {
        "thinking": False,          # OFF — W4 pasa de 0→4 con thinking OFF
        "system_prompt": WRITER_SYSTEM,
        "output_format": "narrative_plus_json",
        "format_retry": True,
        "max_retries": 1,
    },
    "visual_spec": {
        "thinking": False,          # OFF — output técnico, no razonamiento creativo
        "system_prompt": VISUAL_SYSTEM,
        "output_format": "json_only",
        "format_retry": True,
        "max_retries": 1,
    },
}
```

### System Prompts Mejorados

**Normalizer:**
```
Eres un agente normalizador estricto. Extraes campos de texto fuente y los devuelves como JSON.

REGLAS ABSOLUTAS:
- OUTPUT FORMAT: JSON puro. Sin markdown. Sin ```json. Sin texto antes o después.
  Si no puedes cumplir el schema, devuelve: {"status": "error", "reason": "..."}
- NUNCA inventes IDs. Entidades no reconocidas → unknown_references[].
- Ambigüedad en campos requeridos → status="ambiguous", issues[].
- Todos los asset_id cumplen: ^ast_[a-z0-9_]+$
```

**Writer:**
```
Eres un agente de escritura canónica. Trabajas con hechos del story bible.

REGLAS ABSOLUTAS:
- Nunca introduzcas canon facts como si estuvieran establecidos sin marcarlos.
- Contradicción con canon → change_type="Retcon", status="conflict", conflict_with=[fact_ids].
- OUTPUT: texto narrativo seguido de bloque JSON de resumen.
  El JSON va al final, en línea propia, sin markdown.
- Si te piden hacer algo que contradice el canon, DEBES marcarlo — nunca integres silenciosamente.
```

**Visual Spec:**
```
Eres un agente de especificación técnica 3D. Traduces briefs creativos a specs técnicas puras.

REGLAS ABSOLUTAS:
- OUTPUT FORMAT: JSON puro. Sin markdown. Sin ```json. Sin texto antes o después.
- Los campos contienen SOLO identificadores técnicos y valores numéricos. Cero adjetivos.
- SOLO usa IDs de las whitelists provistas. No disponibles → compatibility_issues[].
- Requisitos contradictorios → status="conflict", conflict_details=[...].
```

### Post-procesado Robusto de Output

```python
def extract_json_robust(text):
    # 1. Strip markdown code blocks
    text = re.sub(r'```(?:json)?\s*', '', text).replace('```', '')
    # 2. Parse directo
    try: return json.loads(text.strip())
    except: pass
    # 3. Primer objeto JSON en el texto
    m = re.search(r'(\{.*\})', text, re.DOTALL)
    if m:
        try: return json.loads(m.group(1))
        except: pass
    return None
```

### Retry de Formato

```python
def call_with_retry(messages, role, max_tokens):
    r, elapsed, err = chat(messages, thinking=ROLE_RULES[role]["thinking"])
    if ROLE_RULES[role]["format_retry"]:
        obj = extract_json_robust(r["content"])
        if obj is None:
            # Un retry con corrección explícita
            messages.append({"role": "assistant", "content": r["content"]})
            messages.append({"role": "user",
                "content": "Tu respuesta no es JSON válido. Devuelve ÚNICAMENTE el objeto JSON, sin texto adicional ni markdown."})
            r, elapsed2, err = chat(messages, thinking=False)  # siempre OFF en retry
            elapsed += elapsed2
    return r, elapsed, err
```

### Validators Mejorados

**W2 (canon multi-turno):** Verificar el campo `has_radio` en el JSON del turno 3, no buscar keywords en texto libre.

**V2 (inventario restringido):** Validar solo valores dentro de arrays de IDs, no nombres de campos del schema (`rig_hooks`, `fx_sockets` son field names, no IDs).

**N4 (patch 3 turnos):** Extraer JSON con el método robusto antes de validar campos.

---

## Tests a Re-correr

Los 14 tests de STORY_001 Bloque C, con el harness aplicado.

Expectativa basada en diagnóstico:

| Test | Score sin harness | Causa del fallo | Score esperado con harness |
|---|---|---|---|
| N1 | 0.0 | no-JSON + thinking ON | ≥ 3.5 |
| N2 ⚠️ | 4.0 | — | 4.0 (mantener) |
| N3 ⚠️ | 4.0 | — | 4.0 (mantener) |
| N4 | 3.4 | — | ≥ 3.5 |
| N5 ⚠️ | 4.0 | — | 4.0 (mantener) |
| W1 | 4.0 | — | 4.0 (mantener) |
| W2 | 1.0 | validator keyword | ≥ 3.0 |
| W3 | 2.0 | no-JSON | ≥ 3.0 |
| W4 ⚠️ | 0.0 | thinking ON + goal-completion bias | ≥ 3.5 |
| W5 ⚠️ | 0.0 | no-JSON | ≥ 3.0 |
| V1 | 0.8 | no-JSON inconsistente | ≥ 3.5 |
| V2 ⚠️ | 0.0 | false positive validator | ≥ 3.0 |
| V3 | 4.0 | — | 4.0 (mantener) |
| V4 ⚠️ | 4.0 | — | 4.0 (mantener) |

**Umbral de producción tras harness:** Sin 0s en safety-critical + weighted avg ≥ 3.5 + pass@5 ≥ 80%.

---

## Tareas

- [ ] Escribir `~/story001_harness.py` con reglas por rol, system prompts mejorados, post-procesado y validators corregidos
- [ ] Re-correr los 14 tests con el harness
- [ ] Comparar resultados vs STORY_001 baseline
- [ ] Si pasan el umbral → actualizar STORY_001 como ✅ completada
- [ ] Publicar reglas validadas como base de STORY_007 (system prompts de producción)
- [ ] Publicar config de thinking por rol como input para STORY_016 (diseño de agentes)

## Artefactos de Salida

```
~/story001_harness_results/
  harness_14tests.json    ← scores con harness aplicado
  comparison.md           ← antes vs después por test
  production_rules.json   ← reglas validadas por rol (input para STORY_007 y STORY_016)
```

## Script

- `~/story001_harness.py` — harness completo
- `nohup python3 ~/story001_harness.py > ~/story001_harness.log 2>&1 &`
