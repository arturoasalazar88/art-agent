# Próximos Pasos

> Última actualización: 2026-04-26
> Trigger de actualización: Cada cierre de sesión.

---

## Fase Actual

**Pre-producción** — Infraestructura validada, pipeline diseñado, agente context-engineering implementado y auditado. Listo para iniciar implementación del MCP server y desarrollo del juego.

---

## ✅ Completado en Última Sesión (2026-04-28)

- [x] Motor del juego cambiado de Three.js a Unity + Unity MCP — project_state.md actualizado (D29)
- [x] Arquitectura de 5 capas aprobada e ingestada en contexto (D30)
- [x] Novelización mutable como base estratégica definida (D31)
- [x] Sistema de memoria por capas + presupuesto de tokens documentado (D32)
- [x] Clasificación de cambios narrativos (Expansión / Ajuste local / Retcon) (D33)
- [x] 15 formatos de handoff canónicos documentados en project_state.md (D34, D36)
- [x] 11 workflows operativos granulares ingestados (D35)
- [x] Trazabilidad obligatoria de artefactos definida — 5 campos mínimos (D37)
- [x] Estructura de directorios `~/horror-game/` aprobada (D38)
- [x] Política de contexto 7 niveles + artefactos de compresión obligatorios (D39)
- [x] 3 inputs ingestados: spec-workflow, handoff-workflows-detallados, formatos_de_handoff (generador)

---

## 🔴 Urgente

- [ ] **Implementar MCP server** — specs completas en `inputs/mcp-specs-survival-horror.md`. Python + FastMCP, puerto 8189. Las 7 herramientas: save_prompt, list_prompts, get_prompt_metadata, generate_image, get_job_status, list_workflows, list_models.
- [ ] **Crear estructura de directorios en servidor Debian** — `~/horror-game/` con: `canon/`, `chapters/`, `chapter_summaries/`, `entities/` (characters, locations, factions, creatures), `scene_specs/`, `branch_graphs/`, `assets/`, `jobs/unity/`, `validation/`, `refs/images/`
- [ ] **Investigar Unity MCP** — evaluar servidor MCP para Unity Editor, compatibilidad con el pipeline local, tipos de herramientas disponibles (import_prefab, place_object, assign_material, add_trigger, etc.)

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
- [ ] Estructura base del juego en Unity — escena inicial, player controller, primer nivel
- [ ] Definir fichas de personaje con Ornstein
- [ ] **[FUTURO/PRESUPUESTO]** Hardware upgrade: P40 24GB + ASUS Z390-A LGA1151 (~$310-470 USD) — 36GB VRAM total, ctx 32768+, LLM + ComfyUI simultáneos. Alternativa superior: RTX 3090 (~$600-800 USD).

---

## Contexto del Workflow Creativo (2026-04-28)

El proyecto adoptó un nuevo workflow maestro de 5 fases documentado en `inputs/spec-workflow-creativo-orquestador-memoria.md`:
1. Novelización mutable (SuperGemma → Ornstein)
2. Consolidación canon (story_bible + derivados)
3. Extracción de interactividad (Ornstein → InteractiveSceneSpec)
4. Generación de assets (TrevorJS/Vision → Ornstein → AssetSpec3D)
5. Orquestación Unity (contratos → Unity MCP)

**Motor cambiado:** Three.js → **Unity + Unity MCP**
**Ornstein** es el normalizador entre horror local y orquestador técnico.
**Regla central:** el orquestador nunca ve horror explícito — solo contratos normalizados.

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
