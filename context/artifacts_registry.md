# Registro de Artefactos

> Última actualización: 2026-05-02 (sesión 26)
> Trigger de actualización: Cada vez que se crea, modifica o depreca un archivo.

---

## Archivos del Agente

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `context/session_log.md` | ✅ Activo | 2026-05-02 | Log de sesiones — una línea por sesión, append only |
| `CLAUDE.md` | ✅ Activo | 2026-04-29 | Identidad del agente — rol, protocolos, memory.load, docs.policy |
| `context/project_state.md` | ✅ Activo | 2026-04-24 | Estado estable del proyecto — equipo, infra, modelos, riesgos, glosario |
| `context/artifacts_registry.md` | ✅ Activo | 2026-05-02 | Este archivo — registro de todos los artefactos |
| `context/conversation_memory.md` | ✅ Activo | 2026-05-02 | Log comprimido de decisiones activas (D01–D85) |
| `context/next_steps.md` | ✅ Activo | 2026-05-02 | Foco de sesión y contexto técnico crítico (listas de tareas → INDEX.md) |
| `context/stories/INDEX.md` | ✅ Activo | 2026-05-02 | Índice maestro de trabajo pendiente — stories organizadas por área |
| `context/stories/STORY_001_validacion_modelos.md` | ✅ Completado | 2026-04-29 | Validación de modelos: ctx=24576 estable, 14 tests agénticos, harness weighted avg 3.92/4.0 |
| `context/stories/STORY_020_agent_harness.md` | ✅ Completado | 2026-04-29 | Agent harness: reglas por rol, thinking OFF, system prompts, validators corregidos |
| `context/agent_harness.md` | ✅ Activo | 2026-04-29 | Reglas de producción del harness — fuente de verdad para STORY_007 y STORY_016 |
| `context/validation_results_complete.md` | ✅ Activo | 2026-04-30 | Resultados milimétricos completos — todos los bloques A/B/C/D + harness v1/v2, run por run, diagnóstico de cada failure mode. Referencia técnica para proyectos futuros. |
| `SPEC_context_engineering_agent.md` | ✅ Activo | 2026-04-24 | Spec del patrón context engineering — referencia, no modificar |
| `.agents/rules/no-assumptions.md` | ✅ Activo | 2026-05-01 | Regla operativa inviolable — evidencia requerida antes de cualquier acción. Cargada en autoload de manifest.yaml y referenciada en core.md. |
| `.agents/rules/token-efficiency.md` | ✅ Activo | 2026-05-01 | Reglas de eficiencia de tokens — grep antes de leer, SSH compound, plan antes de editar, límite 2 intentos por approach. Cargada en autoload. Fuente: estudio empírico SMU/Heidelberg 2026. |
| `inputs/handoff-qwen3-upgrade.md` | ✅ Activo | 2026-05-01 | Handoff de research del usuario para integrar Qwen3.6-35B-A3B. Evidencia de benchmarks, plan de 6 fases, URLs de descarga, template de servicio systemd. |

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
| `context/stories/STORY_002_mcp_server.md` | ⬜ Pendiente | 2026-05-02 | MCP server FastMCP — 7 herramientas (save_prompt, generate_image, list_prompts, get_prompt_metadata, get_job_status, list_workflows, list_models), puerto 8189. |
| `context/stories/STORY_003_horror_game_structure.md` | ⬜ Pendiente | 2026-05-02 | Estructura ~/horror-game/ en servidor Debian — canon, chapters, entities, scene_specs, assets, jobs, validation, refs. |
| `context/stories/STORY_004_unity_mcp_research.md` | 🔬 Research | 2026-05-02 | Investigar Unity MCP — herramientas disponibles, gap analysis vs pipeline, instrucciones de instalación. Desbloquea STORY_012. |
| `context/stories/STORY_005_estetica_base.md` | 🟡 En progreso | 2026-05-02 | Estética base del juego — análisis de refs con Vision, ArtDirectionBrief canónico, paleta, iluminación, mood. |
| `context/stories/STORY_006_lora_strengths.md` | 🟡 En progreso | 2026-05-02 | Calibración LoRA strengths por tipo de asset (criatura, environment, personaje, ítem). |
| `context/stories/STORY_007_system_prompts.md` | ⬜ Pendiente | 2026-05-02 | System prompts de producción por modelo — Ornstein, SuperGemma, TrevorJS, Sage, Vision. Fuente: agent_harness.md. |
| `context/stories/STORY_008_pipeline_llm_comfyui.md` | ⬜ Pendiente | 2026-05-02 | Pipeline automatizado LLM → ComfyUI — script pipeline_run.py, AssetSpec3D → generate_image → polling → imagen. |
| `context/stories/STORY_009_storyboard_style_lock.md` | ⬜ Pendiente | 2026-05-02 | Workflow storyboard con style lock — seed/sampler/LoRA fijos, solo prompt variable. |
| `context/stories/STORY_010_ipadapter_consistencia.md` | ⬜ Pendiente | 2026-05-02 | IPAdapter en ComfyUI para consistencia visual de personajes en múltiples imágenes. |
| `context/stories/STORY_011_batch_generation.md` | ⬜ Pendiente | 2026-05-02 | Script batch generation storyboard — lote de frames via API ComfyUI, manifest JSON al final. |
| `context/stories/STORY_012_unity_escena_base.md` | ⬜ Pendiente | 2026-05-02 | Estructura base Unity — escena inicial, player controller, configuración Unity MCP. |
| `context/stories/STORY_013_fichas_personaje.md` | ⬜ Pendiente | 2026-05-02 | Fichas de personaje con Ornstein — StoryBibleEntry JSON en entities/characters/, registradas en canon_index.json. |
| `context/stories/STORY_014_llama_server_auth.md` | ⬜ Pendiente | 2026-05-02 | Autenticación --api-key en todos los servicios llama-server. Prioridad baja (red local privada). |
| `context/stories/STORY_015_hardware_upgrade.md` | ⬜ Pendiente | 2026-05-02 | Hardware upgrade — RAM 64GB (prioritario, ~$40-60 USD) y/o GPU P40/3090 (diferido por presupuesto). |
| `context/stories/STORY_016_agentes_especializados.md` | ✅ Completado | 2026-04-30 | Story de diseño de agentes especializados + memoria atómica. Completada en sesión 11. |
| `context/stories/STORY_017_blueprint_compiler.md` | ⬜ Pendiente | 2026-05-02 | Blueprint Compiler — script Python determinístico que transforma InteractiveSceneSpec → SceneBlueprint sin campos narrativos. |
| `context/stories/STORY_018_plataforma_orquestacion.md` | ⬜ Pendiente | 2026-05-02 | VOID_ENGINE plataforma de orquestación — AdonisJS 7.x + HTMX + Alpine.js + Tailwind + DaisyUI. 4 fases: shell, estado modelos, chat LLM, ComfyUI. |
| `context/stories/STORY_021_qwen3_validacion.md` | ✅ Completado | 2026-05-01 | Story de validación Qwen3.6-35B-A3B. PASS perfecto 4 tests × 5 ctx-sizes hasta 32k. Pendiente: systemd + switch-model.sh. |
| `context/stories/STORY_022_systemd_servicios_switcher.md` | ✅ Completado | 2026-05-01 | Story de infraestructura ejecutada: Ornstein thinking=false corregido con wrapper, llama-qwen3.service creado, switch-model.sh actualizado a 6 modos. Vision queda bloqueado por falta de GGUF/mmproj. |
| `context/stories/STORY_023_huihui_validacion.md` | ✅ Completado | 2026-05-01 | Validación Huihui-Qwen3.5-35B-A3B. Resultado: no reemplaza Qwen3.6 en ingeniería por latencia/thinking OFF no confiable; sí adoptado como backend de Vision con mmproj. |
| `context/stories/STORY_024_huihui_vision_openwebui.md` | ✅ Completado | 2026-05-02 | Superada por STORY_027: Huihui Vision reemplazado por SuperGemma4 Vision. UAT PASS. Story cerrada en sesión 25. |
| `context/stories/STORY_025_huihui_sin_mmproj_ctx_validacion.md` | ✅ Completada | 2026-05-01 | Huihui sin mmproj ctx=32768 production-ready. T1/T2 PASS hasta 32k. UAT-3 conversacional PASS (lógica, arquitectura, multi-turn). Rol: razonamiento conversacional uncensored en Open WebUI. |
| `outputs/story019_validation_results.md` | ✅ Activo | 2026-04-30 | Resultados completos STORY_019 — métricas por test (SG-1/SG-2/TJ-1/TJ-2), highlights de output, hallazgos técnicos sobre max_tokens y thinking budget. |
| `outputs/creative_models_production_config.md` | ✅ Activo | 2026-04-30 | Config de producción validada para SuperGemma y TrevorJS — comandos de arranque, parámetros de inferencia, system prompts, restricciones de hardware, tiempos esperados. |
| `outputs/ornstein_validation_results.md` | ✅ Activo | 2026-04-30 | Resultados completos validación Ornstein — T1/T2/T3/T4, JSON outputs reales, diagnóstico de last_updated_turn, hallazgos técnicos. |
| `outputs/ornstein_production_config.md` | ✅ Activo | 2026-04-30 | Config de producción Ornstein — comando arranque, parámetros, 4 system prompts por contrato, harness completo con Canonical State Pattern (código Python). |
| `outputs/qwen3_validation_results.md` | ✅ Activo | 2026-05-01 | Resultados completos STORY_021 — T1/T2/T3/T4 × 4k/8k/16k/24k/32k, PASS perfecto en todos. Hallazgos: thinking ON vs OFF, max_tokens por tarea, latencias, diagnóstico de 4 fallos intermedios. |
| `outputs/qwen3_production_config.md` | ✅ Activo | 2026-05-01 | Config de producción Qwen3.6-35B-A3B — comando arranque (puerto 8013, ctx=40960), 3 perfiles de inferencia (extracción, codegen, agentic), tabla de ventana validada, posición en el stack. |
| `outputs/qwen3_runner.py` | ✅ Activo | 2026-05-01 | Runner de validación Qwen3 — 4 tests (T1 JSON, T2 MCP, T3 codegen, T4 multi-turn) × 5 ctx-sizes. Needle-in-haystack methodology. Uso: `python3 qwen3_runner.py <T1|T2|T3|T4> <4k|8k|16k|24k|32k>`. |
| `outputs/story024_huihui_vision_openwebui_results.md` | ✅ Activo | 2026-05-02 | Resultados de STORY_024: Huihui Vision API PASS, Open WebUI bloqueado por auth, hallazgo de codegen fallido por context exceeded y recomendación de usar Qwen3 para ingeniería. |
| `outputs/story025_huihui_text_ctx_validation_results.md` | ✅ Activo | 2026-05-02 | Resultados de STORY_025: Huihui sin mmproj arranca a ctx=32768 y pasa T1/T2 hasta 32k, pero falla objetivo de velocidad frente a Qwen3.6. |
| `context/stories/STORY_026_openwebui_web_search.md` | ✅ Completada | 2026-05-01 | SearXNG instalado en Docker (puerto 8080), Web Search activado en Open WebUI y validado en UAT. RAG de URL pendiente de verificar. |
| `context/stories/STORY_027_qwen25vl_vision_upgrade.md` | ✅ Completado | 2026-05-02 | Vision Upgrade completado. SuperGemma4-26B-abliterated-multimodal adoptado como modelo de visión. UAT PASS (D83). Thinking OFF obligatorio por limitación llama.cpp b8998 (D84). Huihui Vision/Texto y Qwen2.5-VL eliminados del servidor (D85). |
| `outputs/story027_qwen25vl_vision_upgrade_results.md` | ✅ Activo | 2026-05-02 | Resultados STORY_027: comparación Qwen2.5-VL-32B (lento), Huihui Vision (alucinaciones), Qwen2.5-VL-7B (baja calidad), SuperGemma4 Vision (UAT PASS). Documenta canal thinking OFF limitación llama.cpp b8998. |
| `context/stories/STORY_028_huihui_claude47_upgrade.md` | ✅ Completado | 2026-05-02 | Sage (Huihui 4.7): UAT 5/5 PASS. T1/T2/T3 conversacional + T4/T5 ingeniería ctx baseline+32k. Adoptado como `sage` en switch-model.sh. (D89) |
| `context/stories/STORY_029_moe_large_ram_upgrade.md` | 🔴 Bloqueada | 2026-05-01 | MoE Large 57B–122B: validar candidatos huihui 67B-A3B merge, 122B-A10B y Qwen3-57B-A14B con 64GB RAM. Bloqueada hasta upgrade de RAM. |
| `context/agent_harness.md` | ✅ Activo | 2026-05-01 | Actualizado con sección Huihui Texto — reglas de producción, tabla UAT-3, enforcement de español, ctx=32768 obligatorio. |

---

## Artefactos en Servidor 10.1.0.104 (Clawdbot — No Versionados Aquí)

| Ruta (servidor) | Estado | Descripción |
|---|---|---|
| `/home/rdpuser/clawdbot/config/clawdbot.json` | ⚠️ Degradado | Config openclaw — Huihui eliminado, DeepSeek R1 actúa como primary (caída directa), Gemini Flash como fallback final. Pendiente STORY_028 para restaurar primary local. |
| `/home/rdpuser/clawdbot/config/clawdbot.json.bak` | ✅ Backup | Backup pre-sesión 20 del config original con Gemini 2.5 Pro como primary. |
| `outputs/huihui_text_runner.py` | ✅ Activo | 2026-05-02 | Runner de validación STORY_025 — suite T1/T2/T3/T4 por ctx-size contra Huihui texto puro en puerto 8014. |
| `outputs/story025_suite.log` | ✅ Activo | 2026-05-02 | Log parcial de suite STORY_025: T1 4k-32k PASS, T2 4k-32k PASS, T3 4k PASS; suite detenida por cierre. |
| `outputs/huihui_text_launch.log` | ✅ Activo | 2026-05-02 | Log de arranque Huihui texto puro sin mmproj: ctx=32768, KV q8_0, thinking=1, puerto 8014. |

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
| `/home/asalazar/start-ornstein.sh` | ✅ Activo | Wrapper Ornstein con `--chat-template-kwargs '{"enable_thinking":false}'` — evita bug de parsing systemd |
| `/etc/systemd/system/llama-ornstein.service` | ✅ Activo | Servicio systemd para Ornstein — apunta a `/home/asalazar/start-ornstein.sh`, health OK en 8012 |
| `/etc/systemd/system/llama-supergemma.service` | ✅ Activo | Servicio systemd para SuperGemma |
| `/etc/systemd/system/llama-trevorjs.service` | ✅ Activo | Servicio systemd para TrevorJS |
| `/home/asalazar/start-qwen3.sh` | ✅ Activo | Wrapper Qwen3 con ctx=40960, KV q8_0, MoE CPU y puerto 8013 |
| `/etc/systemd/system/llama-qwen3.service` | ✅ Activo | Servicio systemd para Qwen3 ingeniería/codegen — health OK en 8013 |
| `/home/asalazar/models/huihui47/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated.Q4_K_M.gguf` | ✅ Activo | Sage — Huihui Claude 4.7 Q4_K_M 21.3GB. UAT 5/5 PASS sesión 24. ctx=32768, KV q8_0 |
| `/home/asalazar/start-huihui47-text.sh` | ✅ Activo | Wrapper Sage — ctx=32768, KV q8_0, MoE CPU, puerto 8012 |
| `/etc/systemd/system/llama-huihui47.service` | ✅ Activo | Servicio systemd Sage — alias `sage` en switch-model.sh, puerto 8012 |
| `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf` | 🚫 Eliminado | Modelo Huihui Qwen3.5 MoE 35B — eliminado del servidor en sesión 22 (D85) |
| `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf` | 🚫 Eliminado | mmproj Huihui Vision — eliminado del servidor en sesión 22 (D85) |
| `/home/asalazar/start-huihui-vision.sh` | 🚫 Eliminado | Wrapper Huihui Vision — reemplazado por start-supergemma4-vision.sh |
| `/home/asalazar/models/supergemma4-vision/supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf` | ✅ Activo | Modelo SuperGemma4 26B Multimodal Q4_K_M — 17GB, MoE Gemma 4 architecture, abliterated, vision UAT PASS (D83) |
| `/home/asalazar/models/supergemma4-vision/mmproj-supergemma4-26b-abliterated-multimodal-f16.gguf` | ✅ Activo | mmproj SuperGemma4 Vision F16 — cargado en CPU via `--override-tensor ".*=CPU"` |
| `/home/asalazar/models/supergemma4-vision/chat_template.jinja` | ✅ Activo | Chat template Gemma 4 con strip_thinking() macro y enable_thinking support — descargado de Jiunsong/supergemma4-26b-abliterated-multimodal |
| `/home/asalazar/start-supergemma4-vision.sh` | ✅ Activo | Wrapper SuperGemma4 Vision — ctx=8192, thinking OFF (`enable_thinking:false`), n-cpu-moe 12, puerto 8012 |
| `/etc/systemd/system/llama-vision.service` | ✅ Activo | Servicio systemd para SuperGemma4 Vision — actualizado sesión 22, apunta a start-supergemma4-vision.sh, health OK en 8012 |
| `/etc/systemd/system/comfyui.service` | ✅ Activo | Servicio systemd para ComfyUI (no auto-start) |
| `/etc/sudoers.d/asalazar` | ✅ Activo | NOPASSWD para asalazar — creado sesión 23 (D87), elimina workaround de heredoc en SSH |
| `~/switch-model.sh` | ✅ Activo | Script switch de 6 modos: ornstein, supergemma, trevorjs, vision, qwen3, image |
| `~/switch-model.sh.bak` | ✅ Activo | Backup del switcher anterior creado antes de STORY_022 |
| `~/apply-story022-root.sh` | ✅ Activo | Script idempotente usado para aplicar cambios root de STORY_022 |
| `~/download-huihui.sh` | ✅ Activo | Script de descarga reanudable usado en STORY_023 |
| `~/apply-story023-vision-root.sh` | ✅ Activo | Script idempotente usado para crear `llama-vision.service` con Huihui |
| `~/story001_harness.py` | ✅ Activo | Harness completo — 14 tests, 5 runs, comparación vs baseline |
| `~/story001_harness_results/harness_14tests.json` | ✅ Activo | Scores finales con harness aplicado |
| `~/story001_harness_results/comparison.md` | ✅ Activo | Tabla antes vs después por test |
| `~/story001_harness_results/production_rules.json` | ✅ Activo | Reglas validadas por rol — input para STORY_007 y STORY_016 |
| `~/story019_suite.py` | 🔒 Histórico | Suite original — descartada, max_tokens=512 consumido por thinking, scorers regex frágiles |
| `~/sg19_runner.py` | ✅ Activo | Runner individual por test SuperGemma/TrevorJS — 4 tests cualitativos (sg1/sg2/tj1/tj2) |
| `~/orn_runner.py` | ✅ Activo | Runner individual por test Ornstein — 4 tests JSON (t1/t2/t3/t4), incluye extractor JSON y validación automática de criterios |
| `~/qwen3_runner.py` | ✅ Activo | Runner validación Qwen3 — espejo de `outputs/qwen3_runner.py` |
| `~/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf` | ✅ Activo | Modelo GGUF 21.3 GB — bartowski Q4_K_M |
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

## Assets del Estudio

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `assets/fonts/DArkkercornner.otf` | ✅ Activo | 2026-05-02 | Fuente OTF generada desde darkercornner_font.png — 45/52 glifos (A–X mayúsculas, a–u minúsculas). Script: `scripts/build_font.py`. Instalable en Mac y Windows. |
| `scripts/build_font.py` | ✅ Activo | 2026-05-02 | Script Python — extrae glifos de PNG via proyección, vectoriza con potrace, ensambla OTF con fonttools. |
| `assets/logo/darkkercornner_studios_logo.png` | ✅ Activo | 2026-05-02 | Logo oficial DArkkercornner Studios — generado con Nano Banana Pro. Concepto: tipografía de niño que maduró demasiado pronto. |
| `assets/logo/darkkercornner_studios_logo_variant.png` | ✅ Activo | 2026-05-02 | Variante del logo oficial — fondo negro. |

---

## Convenciones

- Archivos en `inputs/` son **read-only** — nunca se modifican después de ser colocados ahí
- Los archivos `🔒 Histórico` se mantienen como referencia pero su contenido ya fue ingestado en `context/`
- Los archivos `✅ Activo` son la fuente de verdad actual
- Todo archivo nuevo producido por el agente debe registrarse aquí con estado `🔧 En progreso` y pasar a `✅ Activo` al validarse
