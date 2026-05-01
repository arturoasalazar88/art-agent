# Registro de Artefactos

> Última actualización: 2026-04-30 (sesión 14)
> Trigger de actualización: Cada vez que se crea, modifica o depreca un archivo.

---

## Archivos del Agente

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `context/session_log.md` | ✅ Activo | 2026-04-26 | Log de sesiones — una línea por sesión, append only |
| `CLAUDE.md` | ✅ Activo | 2026-04-29 | Identidad del agente — rol, protocolos, memory.load, docs.policy |
| `context/project_state.md` | ✅ Activo | 2026-04-24 | Estado estable del proyecto — equipo, infra, modelos, riesgos, glosario |
| `context/artifacts_registry.md` | ✅ Activo | 2026-04-24 | Este archivo — registro de todos los artefactos |
| `context/conversation_memory.md` | ✅ Activo | 2026-04-29 | Log comprimido de 50 decisiones (D01–D50) |
| `context/next_steps.md` | ✅ Activo | 2026-04-29 | Foco de sesión y contexto técnico crítico (listas de tareas → INDEX.md) |
| `context/stories/INDEX.md` | ✅ Activo | 2026-04-29 | Índice maestro de trabajo pendiente — 18 stories organizadas en 5 áreas |
| `context/stories/STORY_001_validacion_modelos.md` | ✅ Completado | 2026-04-29 | Validación de modelos: ctx=24576 estable, 14 tests agénticos, harness weighted avg 3.92/4.0 |
| `context/stories/STORY_020_agent_harness.md` | ✅ Completado | 2026-04-29 | Agent harness: reglas por rol, thinking OFF, system prompts, validators corregidos |
| `context/agent_harness.md` | ✅ Activo | 2026-04-29 | Reglas de producción del harness — fuente de verdad para STORY_007 y STORY_016 |
| `context/validation_results_complete.md` | ✅ Activo | 2026-04-30 | Resultados milimétricos completos — todos los bloques A/B/C/D + harness v1/v2, run por run, diagnóstico de cada failure mode. Referencia técnica para proyectos futuros. |
| `SPEC_context_engineering_agent.md` | ✅ Activo | 2026-04-24 | Spec del patrón context engineering — referencia, no modificar |
| `.agents/rules/no-assumptions.md` | ✅ Activo | 2026-05-01 | Regla operativa inviolable — evidencia requerida antes de cualquier acción. Cargada en autoload de manifest.yaml y referenciada en core.md. |
| `.agents/rules/token-efficiency.md` | ✅ Activo | 2026-05-01 | Reglas de eficiencia de tokens — grep antes de leer, SSH compound, plan antes de editar, límite 2 intentos por approach. Cargada en autoload. Fuente: estudio empírico SMU/Heidelberg 2026. |

---

## Skills

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `.claude/commands/context-checkpoint.md` | ✅ Activo | 2026-04-26 | Skill de checkpoint — memoria a corto plazo para compactación o ruptura de sesión |
| `.claude/commands/context-start.md` | ✅ Activo | 2026-04-29 | Skill de apertura de sesión — carga memoria + INDEX.md y presenta resumen |
| `.claude/commands/context-close.md` | ✅ Activo | 2026-04-24 | Skill de cierre de sesión — actualiza memoria y confirma |
| `.claude/commands/context-save.md` | ✅ Activo | 2026-04-24 | Skill de guardado on-demand — persiste decisiones o chat a memoria |

---

## Outputs (Generados por el Agente)

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `outputs/` | ✅ Activo | 2026-04-24 | Directorio para artefactos producidos — código, scripts, configs, docs |
| `outputs/workflow_map.md` | ✅ Activo | 2026-04-28 | Mapa completo de workflows creativos y de generación de assets. 9 workflows, todos los actores, matriz actor×workflow, catálogo de 16 contratos de handoff, gaps identificados. Fuente de verdad para diseño de plataforma. |
| `outputs/agent_memory_spec.md` | ✅ Activo | 2026-04-30 | Especificación completa de agentes especializados y memoria atómica. 6 roles (modelo×rol), 10 bloques atómicos, presupuestos de tokens por rol, spec del Memory Compiler, Canonical State Manager, configuración de invocación, reglas por workflow. Input para STORY_017 y STORY_018. |
| `outputs/void_engine_layout_guide.md` | ✅ Activo | 2026-05-01 | Guía de layout de VOID_ENGINE. Define shell desktop 3 columnas, dimensiones, reglas de scroll, breakpoints, pantalla base Main Workspace y política de mocks on-demand. Fuente de verdad para layout de plataforma. |
| `outputs/void_engine_ui_ux_guide.md` | ✅ Activo | 2026-05-01 | Guía UI/UX de VOID_ENGINE. Define principios visuales, paleta dark-only, tipografía, componentes, reglas de copy, UX por tarea y política de Gemini/Stitch como herramienta exploratoria de baja confianza. |
| `context/stories/STORY_016_agentes_especializados.md` | ✅ Completado | 2026-04-30 | Story de diseño de agentes especializados + memoria atómica. Completada en sesión 11. |
| `outputs/story019_validation_results.md` | ✅ Activo | 2026-04-30 | Resultados completos STORY_019 — métricas por test (SG-1/SG-2/TJ-1/TJ-2), highlights de output, hallazgos técnicos sobre max_tokens y thinking budget. |
| `outputs/creative_models_production_config.md` | ✅ Activo | 2026-04-30 | Config de producción validada para SuperGemma y TrevorJS — comandos de arranque, parámetros de inferencia, system prompts, restricciones de hardware, tiempos esperados. |
| `outputs/ornstein_validation_results.md` | ✅ Activo | 2026-04-30 | Resultados completos validación Ornstein — T1/T2/T3/T4, JSON outputs reales, diagnóstico de last_updated_turn, hallazgos técnicos. |
| `outputs/ornstein_production_config.md` | ✅ Activo | 2026-04-30 | Config de producción Ornstein — comando arranque, parámetros, 4 system prompts por contrato, harness completo con Canonical State Pattern (código Python). |

---

## Inputs — Plataforma de Orquestación

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `inputs/adonisjs_assessment.md` | ✅ Activo | 2026-04-30 | Assessment completo AdonisJS 7.x — 15 secciones, estructura, controllers, services, validators, SSE/streaming LLM, filesystem, HTMX+Edge.js, Alpine.js, env, error handling, testing, routing, middleware, anti-patterns. Fuente de verdad para el harness del agente de código de la plataforma. |
| `inputs/mocks/stitch-prompts/screen_01_main_workspace/prompt_v1_layout.md` | 🚫 Eliminado | 2026-05-01 | Prompt Stitch layout-only para Screen 01. Eliminado por decisión de abandonar mocks generales en Stitch y pasar a guías de layout/UI on-demand. |
| `inputs/mocks/stitch-prompts/screen_01_main_workspace/prompt_v2_layout_fix.md` | 🚫 Eliminado | 2026-05-01 | Prompt Stitch v2 para Screen 01. Eliminado junto con la serie de prompts por baja confiabilidad de Gemini/Stitch para copy/layout exactos. |
| `inputs/mocks/stitch-prompts/screen_01_main_workspace/prompt_v3_text_lock.md` | 🚫 Eliminado | 2026-05-01 | Prompt Stitch v3 para Screen 01. Eliminado junto con la serie de prompts; la estrategia text-lock no impidió alucinaciones estructurales. |
| `inputs/mocks/stitch-prompts/screen_01_main_workspace/prompt_v4_low_trust_renderer.md` | 🚫 Eliminado | 2026-05-01 | Prompt Stitch v4 para Screen 01. Eliminado junto con la serie de prompts; la estrategia low-trust confirmó que Stitch no es fuente confiable para pantallas exactas. |

---

## Inputs (Read-Only — Documentos Fuente)

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `inputs/chat.txt` | 🔒 Histórico | 2026-04-24 | Chat completo de Claude Desktop — 3738 líneas, fuente original |
| `inputs/session-handoff-llm-survival-horror.md` | 🔒 Histórico | 2026-04-23 | Handoff original — superseded por `context/project_state.md` |
| `inputs/mcp-specs-survival-horror.md` | ✅ Activo | 2026-04-23 | Specs técnicas del MCP server — **referencia activa para implementación**, NO ingestado en context/ |
| `inputs/pipeline-context.md` | 🔒 Histórico | 2026-04-24 | Pipeline context original — superseded por CLAUDE.md + context/ |
| `inputs/spec-workflow-creativo-orquestador-memoria.md` | ✅ Activo | 2026-04-28 | Spec de workflow creativo, orquestación Unity MCP y sistema de memoria — **referencia activa**, NO ingestada en context/ |
| `inputs/handoff-workflows-detallados-llms-orquestador.md` | ✅ Activo | 2026-04-28 | 11 workflows granulares por modelo, contratos de handoff, trazabilidad, estructura de directorios, política de contexto — **referencia activa** para operación diaria |
| `inputs/formatos_de_handoff.md` | 🔒 Histórico | 2026-04-28 | Script Python que generó `handoff-workflows-detallados-llms-orquestador.md` — contenido idéntico, ya ingestado |

---

## Artefactos en Servidor Debian (No Versionados Aquí)

| Ruta (servidor) | Estado | Descripción |
|---|---|---|
| `/etc/systemd/system/llama-ornstein.service` | ✅ Activo | Servicio systemd para Ornstein |
| `/etc/systemd/system/llama-supergemma.service` | ✅ Activo | Servicio systemd para SuperGemma |
| `/etc/systemd/system/llama-trevorjs.service` | ✅ Activo | Servicio systemd para TrevorJS |
| `/etc/systemd/system/llama-vision.service` | ✅ Activo | Servicio systemd para Vision |
| `/etc/systemd/system/comfyui.service` | ✅ Activo | Servicio systemd para ComfyUI (no auto-start) |
| `~/switch-model.sh` | ✅ Activo | Script switch de 5 modos |
| `~/story001_harness.py` | ✅ Activo | Harness completo — 14 tests, 5 runs, comparación vs baseline |
| `~/story001_harness_results/harness_14tests.json` | ✅ Activo | Scores finales con harness aplicado |
| `~/story001_harness_results/comparison.md` | ✅ Activo | Tabla antes vs después por test |
| `~/story001_harness_results/production_rules.json` | ✅ Activo | Reglas validadas por rol — input para STORY_007 y STORY_016 |
| `~/story019_suite.py` | 🔒 Histórico | Suite original — descartada, max_tokens=512 consumido por thinking, scorers regex frágiles |
| `~/sg19_runner.py` | ✅ Activo | Runner individual por test SuperGemma/TrevorJS — 4 tests cualitativos (sg1/sg2/tj1/tj2) |
| `~/orn_runner.py` | ✅ Activo | Runner individual por test Ornstein — 4 tests JSON (t1/t2/t3/t4), incluye extractor JSON y validación automática de criterios |
| `~/story019_results/supergemma_results.json` | 🔒 Histórico | Resultados v1 sin raw output — no interpretar |
| `~/story019_results/trevorjs_results.json` | 🔒 Histórico | Resultados v1 sin raw output — no interpretar |
| `~/weaver_spec.txt` | ✅ Activo | Spec visual "The Weaver" generado por TrevorJS — input para TJ-2 y referencia de calidad |
| `~/ComfyUI/workflows/pony_horror.json` | ✅ Activo | Workflow base — Pony + VAE, sin LoRAs |
| `~/ComfyUI/workflows/pony_horror_lora.json` | ✅ Activo | Workflow completo — Pony + VAE + 3 LoRAs |

---

## Outputs Generados en Sesión 5 (2026-04-26)

| Ruta | Estado | Fecha | Descripción |
|---|---|---|
| `outputs/` | ✅ Activo | 2026-04-26 | Directorio listo para artefactos — vacío, primer output será MCP server |

---

## Convenciones

- Archivos en `inputs/` son **read-only** — nunca se modifican después de ser colocados ahí
- Los archivos `🔒 Histórico` se mantienen como referencia pero su contenido ya fue ingestado en `context/`
- Los archivos `✅ Activo` son la fuente de verdad actual
- Todo archivo nuevo producido por el agente debe registrarse aquí con estado `🔧 En progreso` y pasar a `✅ Activo` al validarse
