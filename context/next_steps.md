# Foco de Sesión

> Última actualización: 2026-05-01 (sesión 13)
> Nota: Las listas de tareas y trabajo pendiente están en `context/stories/INDEX.md`.
> Este archivo contiene solo el contexto de sesión: qué acaba de pasar y restricciones técnicas críticas.

---

## Fase Actual

**Pre-producción** — Infraestructura validada, pipeline diseñado, agentes especializados diseñados. Iniciando diseño y construcción de plataforma de orquestación VOID_ENGINE.

---

## Completado en Última Sesión (2026-04-30)

- [x] STORY_016 completada — `outputs/agent_memory_spec.md` producido (6 roles, 10 bloques atómicos, presupuestos de tokens, Memory Compiler spec)
- [x] VOID_ENGINE: concepto de plataforma de orquestación iniciado — UI tipo workspace 3 paneles
- [x] Tech stack frontend VOID_ENGINE decidido — Tailwind CSS + DaisyUI, dark theme only
- [x] Paleta de color VOID_ENGINE definida — charcoal sólido + acento único #5b7cff
- [x] Múltiples iteraciones de mockup Stitch — Image #13 mejor resultado previo, Image #16 cercano con DaisyUI prompt
- [x] Auditoría del prompt Stitch v3 — 7 problemas identificados y documentados
- [x] Enfoque layout-first con Stitch probado y superseded — la serie de prompts fue eliminada tras confirmar baja confiabilidad
- [x] AdonisJS 7.x assessment completado — `inputs/adonisjs_assessment.md` disponible como referencia técnica
- [x] Stitch/Gemini deprecado como fuente de verdad para pantallas exactas — 4 iteraciones confirmaron baja confiabilidad en copy/layout
- [x] Guías base de VOID_ENGINE creadas — `outputs/void_engine_layout_guide.md` y `outputs/void_engine_ui_ux_guide.md`
- [x] Prompts Stitch de Screen 01 eliminados por permiso explícito del usuario

---

## Contexto Técnico Crítico

- **ctx-size producción:** 24,576 tokens con Q4_K_M + `--cache-type-k q4_0 --cache-type-v q4_0`
- **Servidor:** `asalazar@10.1.0.105` — verificar estado al inicio de cada sesión
- **MCP server (8189):** pendiente de implementación — specs en `inputs/mcp-specs-survival-horror.md`
- **ComfyUI y llama-server:** nunca simultáneos — usar `~/switch-model.sh`
- **VOID_ENGINE stack:** AdonisJS 7.x + HTMX + Alpine.js + Tailwind CSS + DaisyUI
- **DaisyUI theme custom:** base-100=#0b0d14, base-200=#111522, base-300=#141824, primary=#5b7cff, success=#56d38a, warning=#d9a441
- **VOID_ENGINE diseño:** guías propias son fuente de verdad — `outputs/void_engine_layout_guide.md` y `outputs/void_engine_ui_ux_guide.md`
- **Gemini/Stitch:** herramienta exploratoria visual de baja confianza; no usar para copy exacto, workflows, layout final ni mocks generales

---

## Próximos Pasos (por prioridad)

1. **VOID_ENGINE implementación base** — construir shell desktop 3 columnas desde las guías propias, no desde Stitch
2. **STORY_019** — validar SuperGemma y TrevorJS (re-descargar modelos primero)
3. **STORY_018** — arquitectura de orquestación VOID_ENGINE (depende de STORY_016 ✅)
4. **STORY_017** — Blueprint Compiler (~150 líneas Python, depende de STORY_016 ✅)
5. **STORY_002** — MCP server FastMCP, 7 herramientas, puerto 8189

---

## Preguntas para el Usuario al Inicio de Sesión

- ¿Hubo cambios en el servidor desde la última sesión?
- ¿Empezamos con el shell base de VOID_ENGINE en AdonisJS/Tailwind o con arquitectura STORY_018?
