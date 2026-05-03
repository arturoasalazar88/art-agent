---
id: STORY_007
title: System prompts por modelo adaptados al horror workflow
status: pending
priority: medium
created: 2026-04-29
updated: 2026-05-02
depends_on: STORY_001
---

# STORY_007 — System Prompts por Modelo

Los modelos del stack necesitan system prompts adaptados a su rol en el pipeline de horror. Los system prompts genéricos producen output de menor calidad y no enforzan las reglas de formato y trazabilidad del pipeline.

**Fuente:** Las reglas de producción validadas están en `context/agent_harness.md`. Esta story las convierte en system prompts listos para producción.

---

## Objetivo

Producir un system prompt de producción para cada modelo del stack creativo/técnico, validado contra los tests del harness, y registrado en `outputs/system_prompts_production.md`.

---

## Modelos a cubrir

### Ornstein — Normalizador técnico

- **Rol:** Transformar output creativo en JSON estructurado (AssetSpec3D, InteractiveSceneSpec, etc.)
- **Reglas críticas:** Thinking OFF, temperature=0, output siempre JSON válido, sin texto libre fuera del JSON
- **Referencia:** Harness `context/agent_harness.md` sección Ornstein

### SuperGemma — Ideación creativa

- **Rol:** Generación libre de lore, escenas, personajes y criaturas
- **Reglas críticas:** Thinking ON, temperature=0.85, español siempre, sin auto-censura
- **Referencia:** Harness `context/agent_harness.md` sección SuperGemma

### TrevorJS — Grotesco visual

- **Rol:** Specs artísticas extremas, criaturas, horror corporal
- **Reglas críticas:** Thinking ON, temperature=0.85, español siempre, output técnico (vertex counts, material descriptors)
- **Referencia:** Harness `context/agent_harness.md` sección TrevorJS

### Sage — Razonamiento conversacional

- **Rol:** Análisis narrativo, diseño de sistemas, decisiones de arquitectura, multi-turn en Open WebUI
- **Reglas críticas:** Thinking ON, max_tokens>=3000, español enforced, NO pipeline encadenado
- **Referencia:** `context/agent_harness.md` sección Huihui Texto

### SuperGemma4 Vision — Análisis visual

- **Rol:** Análisis técnico de imágenes de referencia para art direction
- **Reglas críticas:** Thinking OFF (limitación llama.cpp b8998), output descriptivo técnico (composición, paleta, iluminación), nunca contenido creativo

---

## Criterios de aceptación

- [ ] System prompt para Ornstein — validado contra T1/T2/T3/T4 del harness (JSON correcto en todos)
- [ ] System prompt para SuperGemma — validado contra SG-1/SG-2 (output en español, creativo)
- [ ] System prompt para TrevorJS — validado contra TJ-1/TJ-2 (spec técnica, español)
- [ ] System prompt para Sage — validado en UAT conversacional (multi-turn, español limpio)
- [ ] System prompt para Vision — validado con imagen de referencia real
- [ ] Todos registrados en `outputs/system_prompts_production.md`
- [ ] Configs de arranque actualizadas en servidor con los system prompts (via `--system-prompt` o archivo)

---

## Notas

- Revisar `context/agent_harness.md` completamente antes de escribir — contiene las reglas, ejemplos y casos de fallo documentados
- Los system prompts de Ornstein son los más críticos — un system prompt incorrecto puede romper el JSON output y detener el pipeline
- El Canonical State Pattern (D51) aplica al system prompt de Ornstein cuando opera en modo multi-turn
