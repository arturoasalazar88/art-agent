# Próximos Pasos

> Última actualización: 2026-04-24
> Trigger de actualización: Cada cierre de sesión.

---

## Fase Actual

**Pre-producción** — Infraestructura validada, pipeline diseñado, agente context-engineering implementado.

---

## ✅ Completado en Última Sesión (2026-04-24)

- [x] Implementación del agente context-engineering siguiendo SPEC
- [x] Creación de `CLAUDE.md` con las 4 secciones requeridas
- [x] Creación de los 4 archivos de contexto (`context/`)
- [x] Ingestión completa de `chat.txt` (3738 líneas) en `conversation_memory.md`
- [x] Ingestión completa de `session-handoff-llm-survival-horror.md` en `project_state.md`
- [x] Ingestión completa de `pipeline-context.md` en `project_state.md`
- [x] Referencia activa de `mcp-specs-survival-horror.md` en `artifacts_registry.md`
- [x] Creación de skills: `/context-start`, `/context-close`, `/context-save`
- [x] Reorganización de archivos fuente a `inputs/`

---

## 🔴 Urgente

- [ ] **Implementar MCP server** — specs completas en `inputs/mcp-specs-survival-horror.md`. Python + FastMCP, puerto 8189. Las 7 herramientas: save_prompt, list_prompts, get_prompt_metadata, generate_image, get_job_status, list_workflows, list_models.
- [ ] **Crear estructura `~/horror-game/assets/`** en el servidor Debian — storyboard/, characters/, environments/, workflows/

---

## 🟡 En Progreso

- [ ] Definir estética base del juego — necesita sesión con supergemma-vision analizando imágenes de referencia
- [ ] Afinar strengths de LoRAs según tipo de asset (personaje vs ambiente vs storyboard)

---

## ⬜ Cola (Próximas Acciones)

- [ ] System prompts por modelo adaptados al workflow de survival horror
- [ ] Autenticación `--api-key` para los servicios llama-server
- [ ] Pipeline automatizado LLM → imagen (Ornstein genera prompt → ComfyUI ejecuta)
- [ ] Workflow de storyboard con style lock en ComfyUI
- [ ] Instalar IPAdapter en ComfyUI para consistencia de personajes
- [ ] Script de batch generation para storyboard completo via API ComfyUI
- [ ] Evaluar Q3_K_M de SuperGemma para duplicar ventana de contexto (~16384)
- [ ] Estructura base del juego en Three.js
- [ ] Definir fichas de personaje con Ornstein

---

## Contexto Técnico Crítico para Próxima Sesión

- El MCP server debe correr en el servidor Debian (`asalazar@10.1.0.105`)
- Requiere Python 3.11+ y entorno virtual
- Transporte: SSE (para web clients) + stdio (para CLI tools)
- Debe ser compatible con: Claude Code, OpenCode (prioridad), Gemini CLI, Open WebUI
- ComfyUI tiene API REST en `:8188` — el MCP la envuelve
- El MCP NUNCA expone contenido de prompts en respuestas — solo rutas y status
- La implementación sigue exactamente las specs en `inputs/mcp-specs-survival-horror.md`

---

## Preguntas para el Usuario al Inicio de Sesión

- ¿Tienes imágenes de referencia listas para definir la estética del juego?
- ¿Quieres empezar con el MCP server o con el desarrollo del juego en Three.js?
- ¿Has probado los modelos locales con prompts reales del juego desde la última sesión?
