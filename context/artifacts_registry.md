# Registro de Artefactos

> Última actualización: 2026-04-24 (auditoría)
> Trigger de actualización: Cada vez que se crea, modifica o depreca un archivo.

---

## Archivos del Agente

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `context/session_log.md` | ✅ Activo | 2026-04-26 | Log de sesiones — una línea por sesión, append only |
| `CLAUDE.md` | ✅ Activo | 2026-04-24 | Identidad del agente — rol, protocolos, memory.load, docs.policy |
| `context/project_state.md` | ✅ Activo | 2026-04-24 | Estado estable del proyecto — equipo, infra, modelos, riesgos, glosario |
| `context/artifacts_registry.md` | ✅ Activo | 2026-04-24 | Este archivo — registro de todos los artefactos |
| `context/conversation_memory.md` | ✅ Activo | 2026-04-26 | Log comprimido de 28 decisiones (D01–D28) |
| `context/next_steps.md` | ✅ Activo | 2026-04-24 | Estado operativo — completado, pendiente, siguiente |
| `SPEC_context_engineering_agent.md` | ✅ Activo | 2026-04-24 | Spec del patrón context engineering — referencia, no modificar |

---

## Skills

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `.claude/commands/context-checkpoint.md` | ✅ Activo | 2026-04-26 | Skill de checkpoint — memoria a corto plazo para compactación o ruptura de sesión |
| `.claude/commands/context-start.md` | ✅ Activo | 2026-04-24 | Skill de apertura de sesión — carga memoria y presenta resumen |
| `.claude/commands/context-close.md` | ✅ Activo | 2026-04-24 | Skill de cierre de sesión — actualiza memoria y confirma |
| `.claude/commands/context-save.md` | ✅ Activo | 2026-04-24 | Skill de guardado on-demand — persiste decisiones o chat a memoria |

---

## Outputs (Generados por el Agente)

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `outputs/` | ✅ Activo | 2026-04-24 | Directorio para artefactos producidos — código, scripts, configs, docs |

---

## Inputs (Read-Only — Documentos Fuente)

| Ruta | Estado | Fecha | Descripción |
|---|---|---|---|
| `inputs/chat.txt` | 🔒 Histórico | 2026-04-24 | Chat completo de Claude Desktop — 3738 líneas, fuente original |
| `inputs/session-handoff-llm-survival-horror.md` | 🔒 Histórico | 2026-04-23 | Handoff original — superseded por `context/project_state.md` |
| `inputs/mcp-specs-survival-horror.md` | ✅ Activo | 2026-04-23 | Specs técnicas del MCP server — **referencia activa para implementación**, NO ingestado en context/ |
| `inputs/pipeline-context.md` | 🔒 Histórico | 2026-04-24 | Pipeline context original — superseded por CLAUDE.md + context/ |

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
