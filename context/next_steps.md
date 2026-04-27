# Próximos Pasos

> Última actualización: 2026-04-26
> Trigger de actualización: Cada cierre de sesión.

---

## Fase Actual

**Pre-producción** — Infraestructura validada, pipeline diseñado, agente context-engineering implementado y auditado. Listo para iniciar implementación del MCP server y desarrollo del juego.

---

## ✅ Completado en Última Sesión (2026-04-26)

- [x] Auditoría completa del agente art-agent — aprobado para producción (D27)
- [x] Decisiones de sesiones anteriores transferidas a conversation_memory.md (D23–D28)
- [x] Research hardware dual GPU completado — P40 + Z390-A viable, diferido por presupuesto (D24, D25)
- [x] Qwen-Image evaluado y descartado del pipeline (D23)
- [x] RTX 3060 + RTX 3090 analizada como mejor opción dual GPU (D26)
- [x] Estrategia de archivado para conversation_memory.md definida (D28)
- [x] Permisos de escritura del agente activados en el repo art-agent

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

- [ ] Descargar Q3_K_M de SuperGemma — dobla ctx-size a ~16384 sin costo (mejora inmediata disponible)
- [ ] Agregar session_log.md a context/ — una línea por sesión para audit trail
- [ ] System prompts por modelo adaptados al workflow de survival horror
- [ ] Autenticación `--api-key` para los servicios llama-server
- [ ] Pipeline automatizado LLM → imagen (Ornstein genera prompt → ComfyUI ejecuta)
- [ ] Workflow de storyboard con style lock en ComfyUI
- [ ] Instalar IPAdapter en ComfyUI para consistencia de personajes
- [ ] Script de batch generation para storyboard completo via API ComfyUI
- [ ] Estructura base del juego en Three.js
- [ ] Definir fichas de personaje con Ornstein
- [ ] **[FUTURO/PRESUPUESTO]** Hardware upgrade: P40 24GB + ASUS Z390-A LGA1151 (~$310-470 USD) — 36GB VRAM total, ctx 32768+, LLM + ComfyUI simultáneos. Alternativa superior: RTX 3090 (~$600-800 USD).

---

## Contexto Técnico Crítico para Próxima Sesión

- El MCP server debe correr en el servidor Debian (`asalazar@10.1.0.105`)
- Requiere Python 3.11+ y entorno virtual
- Transporte: SSE (para web clients) + stdio (para CLI tools)
- Debe ser compatible con: Claude Code, OpenCode (prioridad), Gemini CLI, Open WebUI
- ComfyUI tiene API REST en `:8188` — el MCP la envuelve
- El MCP NUNCA expone contenido de prompts en respuestas — solo rutas y status
- La implementación sigue exactamente las specs en `inputs/mcp-specs-survival-horror.md`
- Switch de modelos: `~/switch-model.sh [ornstein|supergemma|trevorjs|vision|image]`
- ctx-size máximo Q4_K_M: 8192 tokens — NO subir sin bajar a Q3_K_M primero

---

## Preguntas para el Usuario al Inicio de Sesión

- ¿Hubo cambios en el servidor desde la última sesión?
- ¿Tienes imágenes de referencia listas para definir la estética del juego?
- ¿Empezamos con el MCP server o con la descarga de Q3_K_M?
- ¿Has probado los modelos locales con prompts reales del juego?
