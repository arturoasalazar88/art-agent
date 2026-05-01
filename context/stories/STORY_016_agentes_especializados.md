# STORY_016 — Diseño de Agentes Especializados + Memoria Atómica

> Estado: ✅ Completado
> Creada: 2026-04-30
> Depende de: STORY_001 ✅, STORY_020 ✅
> Desbloquea: STORY_017 (Blueprint Compiler), STORY_018 (Plataforma de orquestación)

---

## Objetivo

Producir la especificación completa de los agentes especializados del pipeline y su sistema de memoria atómica. Esta spec es el input principal para STORY_017 y STORY_018.

**No incluye:**
- Implementación del Memory Compiler (STORY_017)
- Arquitectura de orquestación / scheduler / queue (STORY_018)
- System prompts nuevos por workflow (STORY_007)

---

## Deliverable Principal

`outputs/agent_memory_spec.md` — Especificación completa de agentes y memoria atómica.

---

## Definition of Done

- [x] Anatomía del agente documentada (modelo + harness + compiler + canonical state)
- [x] Matriz de roles × bloques de memoria definida (per-rol, no per-agente)
- [x] Presupuesto de tokens por rol y por workflow justificado con ctx=24576
- [x] Spec del Memory Compiler (qué produce, no cómo lo implementa)
- [x] Reglas de invocación: qué bloques cargar para cada workflow
- [x] SuperGemma y TrevorJS marcados como `pending STORY_019`
- [x] Documento permite construir el harness para cualquier (modelo, rol) sin fuentes adicionales

---

## Contexto Técnico

- **ctx disponible:** 24576 tokens (Q4_K_M + `--cache-type-k q4_0 --cache-type-v q4_0`)
- **Harness validado:** `context/agent_harness.md` — reglas por rol, thinking OFF, canonical state
- **Scores de referencia:** `context/validation_results_complete.md` — timings y scores por test
- **Workflows:** `outputs/workflow_map.md` — 9 workflows, todos los actores
- **Decisiones base:** D41 (bloques fijos + compiler), D42 (El Ingeniero dos modos), D43 (Blueprint Compiler determinístico)

---

## Notas de Diseño

### Memoria es per-rol, no per-agente
Ornstein aparece en WF-02 (normalización), WF-04 (extracción lore), WF-05 (normalización criaturas), WF-07 (extracción interactividad), WF-08 (firewall semántico). Cada rol necesita bloques distintos — el bloque CANON para WF-07 incluye resúmenes de capítulos, el de WF-05 no los necesita.

### SuperGemma y TrevorJS en disco
Ambos modelos fueron eliminados del disco al cerrar las sesiones de validación. Sus specs son **preliminares, pending STORY_019**. La confianza en sus especificaciones es menor que la de Ornstein (harness validado empíricamente).

### Budget de tokens
- Budget objetivo ≤ 12k para roles multi-turno (writer en WF-02)
- 24k disponible solo para tareas one-shot pesadas (extracción de capítulo completo, normalización masiva)
- Prefill de 31s penaliza multi-turn a ctx alto — no diseñar para el techo

---

## Progreso

- [x] STORY_001 completada — ctx=24576 validado, 25 tok/s
- [x] STORY_020 completada — harness v2, weighted avg 4.0/4.0
- [x] Advisor consultado — scope y constraints definidos
- [ ] outputs/agent_memory_spec.md — en producción
