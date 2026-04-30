# Memoria de Conversación — Log de Decisiones

> Última actualización: 2026-04-28 (sesión 7 — D40)
> Formato: Cronológico, comprimido. Decisiones y su WHY, no transcripción.
> Trigger de actualización: Después de cada sesión donde se toma una decisión significativa.

---

## 2026-04-21 — Sesión 1: Setup Inicial del Servidor

### D01: Runtime = llama.cpp server
- **Contexto:** Necesidad de servir modelos GGUF locales en Debian con RTX 3060.
- **Opciones:** Ollama, vLLM, llama.cpp server.
- **Decisión:** llama.cpp server.
- **Por qué:** Soporte nativo de GGUF, modo híbrido GPU+RAM con `--n-cpu-moe`, control granular de parámetros, compatibilidad con OpenAI API.

### D02: Tres modelos especializados, no uno general
- **Contexto:** ¿Un modelo para todo o especialización por rol?
- **Decisión:** Tres modelos con roles definidos.
- **Por qué:** Cada modelo tiene fortalezas distintas — Ornstein para estructura, SuperGemma para crudeza creativa, TrevorJS para grotesco visual. Un solo modelo no cubre todo.

### D03: Preset base = `--n-cpu-moe 12 --n-gpu-layers 999 --ctx-size 8192`
- **Contexto:** Encontrar el balance entre rendimiento y estabilidad en RTX 3060 12GB.
- **Opciones probadas:** n-cpu-moe 10 (falló), 12 (estable), 14 (funciona pero innecesario). ctx-size 2048 (muy pequeño), 8192 (estable), 16384 (SEGV).
- **Decisión:** n-cpu-moe=12, ctx-size=8192.
- **Por qué:** 12 es el mínimo seguro. 8192 maximiza contexto sin SEGV. 16384 revienta KV cache.
- **Descartado:** ctx-size 16384 causa SEGV en Q4_K_M.

### D04: Puerto fijo 8012, un modelo a la vez
- **Contexto:** ¿Cómo manejar múltiples modelos con VRAM limitada?
- **Decisión:** Puerto único 8012, script switch-model.sh para cambiar.
- **Por qué:** La RTX 3060 no puede cargar dos modelos simultáneamente. Puerto fijo = Open WebUI nunca necesita reconfiguración.

### D05: Thinking activado en todos los modelos
- **Contexto:** ¿Activar o desactivar el modo thinking (chain-of-thought)?
- **Decisión:** Activado en los tres. Sin `--chat-template-kwargs '{"enable_thinking":false}'`.
- **Por qué:** Mejora la calidad de razonamiento. Open WebUI maneja `reasoning_content` correctamente.

---

## 2026-04-22 — Sesión 2: ComfyUI + VAE + LoRAs

### D06: ComfyUI como generador de imágenes
- **Contexto:** Necesidad de generar assets visuales de horror (gore, environments, criaturas).
- **Decisión:** ComfyUI con Pony Diffusion V6 XL.
- **Por qué:** API REST nativa, workflows JSON programables, soporte SDXL, ecosistema de LoRAs.

### D07: ComfyUI y llama-server no corren simultáneamente
- **Contexto:** ¿Pueden compartir la GPU?
- **Decisión:** No. Modos exclusivos: LLM o imagen, nunca ambos.
- **Por qué:** La RTX 3060 12GB no tiene VRAM para ambos. Switch obligatorio via switch-model.sh.

### D08: ComfyUI como servicio systemd pero sin auto-start
- **Contexto:** ¿Cómo gestionar ComfyUI?
- **Decisión:** Servicio systemd creado pero `systemctl disable comfyui` — solo arranca manualmente.
- **Por qué:** Evitar conflicto de VRAM en el boot si un LLM también arranca.

### D09: VAE externo sdxl_vae.safetensors
- **Contexto:** El VAE integrado del checkpoint producía colores pobres.
- **Decisión:** Descargar y usar sdxl_vae.safetensors de Stability AI (319 MB).
- **Por qué:** Mejora notable en colores, sombras y detalle vs VAE integrado. Validado visualmente.

### D10: Tres LoRAs seleccionados para horror
- **Contexto:** Mejorar la calidad específica de horror en las generaciones.
- **Decisión:** horror_style (0.7), gore_details (0.5), dark_fantasy_arch (0.4).
- **Por qué:** Cada uno mejora un aspecto: atmósfera, anatomía gore, arquitectura decadente. Strengths calibrados para no sobre-estilizar.
- **Nota:** dark_fantasy_arch descargado del mirror (ID original 404 en CivitAI).

### D11: switch-model.sh ampliado a 4 modos (+ image)
- **Contexto:** Necesidad de cambiar entre LLM y ComfyUI.
- **Decisión:** Agregar modo `image` al script que detiene LLMs y arranca ComfyUI.
- **Por qué:** Un solo comando para todo: `~/switch-model.sh image`.

---

## 2026-04-23 — Sesión 3: Pipeline Artista/Ingeniero + Visión + MCP

### D12: Pipeline Artista / Ingeniero
- **Contexto:** ¿Cómo manejar la censura de Claude mientras se generan assets gore?
- **Decisión:** Separación estricta. El Artista (humano + LLMs uncensored) genera contenido. El Ingeniero (agente censored) ejecuta técnicamente sin ver el contenido.
- **Por qué:** Claude puede ayudar con todo lo técnico sin violar sus restricciones. Los prompts viajan como archivos JSON donde el ingeniero solo lee metadata y parámetros, nunca el prompt en sí.

### D13: MCP server agnóstico con FastMCP
- **Contexto:** ¿Cómo conectar el pipeline Artista → Ingeniero?
- **Opciones:** Script directo, MCP propietario, MCP estándar.
- **Decisión:** Servidor MCP en Python con FastMCP, transporte SSE + stdio, puerto 8189.
- **Por qué:** Estándar MCP = compatible con Claude Code, Gemini CLI, OpenCode, Open WebUI sin modificaciones. Un servidor, todos los clientes.

### D14: Dos herramientas MCP principales
- **Contexto:** ¿Qué herramientas necesita el MCP?
- **Decisión:** `save_prompt` (Artista) y `generate_image` (Ingeniero) como core. Plus: `list_prompts`, `get_prompt_metadata`, `get_job_status`, `list_workflows`, `list_models`.
- **Por qué:** Cubre el flujo completo: el artista guarda, el ingeniero ejecuta. Las demás son auxiliares.

### D15: SuperGemma Vision multimodal
- **Contexto:** Necesidad de analizar imágenes de referencia para extraer estética.
- **Decisión:** Descargar supergemma4-26b-abliterated-multimodal GGUF + mmproj del mirror kof1467.
- **Por qué:** El repo original de Jiunsong requería auth. El mirror tiene los mismos archivos sin restricción.

### D16: mmproj forzado a CPU con --override-tensor
- **Contexto:** mmproj necesita ~1145 MB pero solo quedan ~27 MB en VRAM.
- **Opciones:** `--mmproj-use-cpu` (no existe en este build), `--override-tensor ".*=CPU"`.
- **Decisión:** `--override-tensor ".*=CPU"` + ctx-size reducido a 4096.
- **Por qué:** Es la única forma de forzar el mmproj a RAM en este build de llama.cpp.

### D17: Visión NO necesita ser uncensored
- **Contexto:** ¿Necesitamos un modelo de visión uncensored para analizar gore?
- **Opciones evaluadas:** Gemma 3 12B abliterated (mmproj defectuoso), Gemma 4 26B MAX Q8_0 (no cabe), E4B HauhauCS (viable pero innecesario).
- **Decisión:** No. SuperGemma Vision describe técnicamente. SuperGemma/TrevorJS generan el prompt gore.
- **Por qué:** La censura importa en la generación, no en el análisis. Vision solo produce descripciones técnicas (composición, paleta, mood).

### D18: Qwen3-Coder y Qwen3-30B descartados
- **Contexto:** Buscar el modelo de código más potente para el hardware.
- **Descartados:**
  - Qwen3.6-35B-A3B: Arquitectura Gated DeltaNet no soportada en llama.cpp.
  - Qwen3-Coder-30B-A3B: No tiene thinking mode.
  - Qwen3-30B-A3B: Evaluado con Perplexity, resultado insatisfactorio para coding agentic.
- **Decisión:** Mantener Gemma 4 variantes como stack principal.

### D19: switch-model.sh ampliado a 5 modos (+ vision)
- **Contexto:** Integrar el modelo multimodal en el flujo operativo.
- **Decisión:** Agregar modo `vision` con servicio systemd `llama-vision`.
- **Por qué:** Un solo script, 5 modos: ornstein, supergemma, trevorjs, vision, image.

### D20: Estructura de archivos de prompt (JSON schema)
- **Contexto:** ¿Cómo guardar los prompts del Artista para que el Ingeniero los ejecute?
- **Decisión:** JSON con campos separados: `prompt`/`negative_prompt` (solo escritura para ingeniero), `metadata` (lectura segura), `generation` (parámetros técnicos), `output` (resultado).
- **Por qué:** Separación limpia. El ingeniero puede operar sin ver contenido creativo.

### D21: Pipeline context como archivo para agentes
- **Contexto:** Necesidad de un documento legible por agentes con el flujo completo.
- **Decisión:** Crear `pipeline-context.md` como texto plano, sin UI, para cargar como contexto.
- **Por qué:** Cualquier agente lo puede leer al inicio de sesión y entender el proyecto completo.

---

## 2026-04-24 — Sesión 4: Context Engineering Agent

### D22: Adopción del patrón Context Engineering
- **Contexto:** Necesidad de que el agente recuerde todo entre sesiones sin re-briefing.
- **Decisión:** Implementar el patrón de SPEC_context_engineering_agent.md — CLAUDE.md + 4 archivos de contexto + skills de sesión.
- **Por qué:** Memoria persistente basada en archivos. Separación estable/volátil. El agente puede retomar cualquier sesión con `/context-start`.
- **Descartado:** agent.md monolítico (anti-patrón "one giant context file").

---

## 2026-04-26 — Sesión 5: Auditoría del Agente + Research Hardware + Modelos

### D23: Qwen-Image descartado del pipeline
- **Contexto:** Se evaluó Qwen/Qwen-Image como posible herramienta para el pipeline visual.
- **Opciones:** Integrar como generador alternativo a ComfyUI.
- **Decisión:** Descartado — no es relevante para el pipeline actual.
- **Por qué:** Es un modelo text-to-image (compite con ComfyUI/Pony Diffusion), no análisis visual. Fortalezas en text rendering dentro de imágenes — útil solo en fase futura de UI del juego. Sin GGUF disponible, corre en BF16, exigente en VRAM.
- **Descartado:** Sin cuantización Q4, resoluciones nativas 1664×928 exceden capacidad cómoda.

### D24: B365M-A confirmada como bloqueante para dual GPU
- **Contexto:** Research de upgrade hardware RTX 3060 + Tesla P40 24GB.
- **Hallazgo:** ASUS Prime B365M-A es mATX con chipset B365. Solo tiene 1 slot PCIe x16 eléctrico. El segundo slot es x1 eléctrico — P40 ni entraría físicamente.
- **Decisión:** La B365M-A bloquea cualquier configuración dual GPU. Requiere cambio de motherboard obligatorio.
- **Por qué:** Sin dos slots x16 eléctricos no hay dual GPU posible en este hardware.

### D25: Plan upgrade P40 + Z390-A viable pero diferido por presupuesto
- **Contexto:** Evaluar si el upgrade dual GPU es viable con presupuesto limitado.
- **Opciones:** P40 + Z390-A ($310-470 USD total), RTX 3090 sola ($600-800 USD), RTX 3060 + RTX 3090 (más caro aún).
- **Decisión:** Diferido. Viable técnicamente pero presupuesto no lo permite ahora.
- **Detalles del plan cuando haya presupuesto:**
  - Motherboard: ASUS Prime Z390-A LGA1151 (~$150-200 USD segunda mano)
  - GPU: Tesla P40 24GB (~$80-150 USD segunda mano)
  - Cooler activo para P40 (~$20-40 USD)
  - Fuente 750W+ si es necesario (~$60-80 USD)
  - Resultado: 36GB VRAM total, ctx-size 32768+, LLM + ComfyUI simultáneos
- **Riesgo P40:** Pascal (2016), sin flash attention eficiente, requiere enfriamiento activo, 250W TDP.
- **Alternativa superior:** RTX 3090 24GB (~$600-800) — misma arquitectura Ampere, más simple.
- **Mejora inmediata de bajo costo:** RAM 32→64GB (~$40-60 USD) o descargar Q3_K_M (gratis, dobla ctx a ~16384).

### D26: RTX 3060 + RTX 3090 analizada como mejor opción dual GPU
- **Contexto:** ¿Es mejor P40 + 3060 o 3090 + 3060?
- **Decisión:** 3090 + 3060 es superior técnicamente pero más cara.
- **Por qué:** Ambas Ampere — mismo driver, misma arquitectura, flash attention funciona en las dos. llama.cpp maneja Ampere+Ampere mejor que Pascal+Ampere. Con 36GB combinados, `--tensor-split 12,24` distribuye capas eficientemente. Velocidad estimada 100-140 tok/s vs ~40 tok/s actual.
- **Descartado por ahora:** Precio inaccesible con presupuesto actual.

### D27: art-agent auditado y aprobado para producción
- **Contexto:** Auditoría completa del agente context-engineering antes de usarlo con Claude Code.
- **Resultado:** Agente listo para producción. Sigue SPEC al 100%. CLAUDE.md bien estructurado, 22 decisiones en memoria, skills funcionales.
- **Issues identificados (resueltos en este cierre):**
  - Decisiones de sesión 5 no capturadas → resuelto ahora
  - Sin estrategia de archivado → documentada en D28
  - Sin session_log.md → agregado como mejora pendiente
  - next_steps.md sin hardware upgrade como item en cola → resuelto ahora
- **Por qué aprobado:** Estructura correcta, separación Artista/Ingeniero codificada, memoria completa, skills funcionales.

---

## 2026-04-28 — Sesión 6: Workflow Creativo + Sistema de Memoria + Unity

### D29: Motor del juego cambiado de Three.js a Unity + Unity MCP
- **Contexto:** Review del spec `inputs/spec-workflow-creativo-orquestador-memoria.md` reveló que la decisión de motor había evolucionado.
- **Decisión:** Unity como motor principal. Unity MCP como capa de ensamblaje interactivo (gestión de assets, escenas, scripts, GameObjects desde agente).
- **Por qué:** Unity MCP provee herramientas estructuradas para que un agente opere el editor programáticamente. Mejor fit para el pipeline de orquestación que Three.js manual.
- **Impacto:** Actualizado en `project_state.md` y `next_steps.md`.

### D30: Arquitectura de 5 capas aprobada
- **Contexto:** Necesidad de separar creación sensible de montaje técnico.
- **Decisión:** 5 capas — ideación, canon, normalización, orquestación, implementación Unity.
- **Por qué:** La capa de normalización (Ornstein) es el firewall entre horror explícito local y el orquestador técnico. El orquestador nunca consume descripción grotesca, solo contratos normalizados.

### D31: Novelización mutable como base del proyecto (antes que interactividad)
- **Contexto:** ¿Construir juego y narrativa en paralelo o secuencialmente?
- **Decisión:** Primero story bible + novela base; después extracción de interactividad.
- **Por qué:** La interactividad sin canon sólido genera incoherencia estructural. Canon primero = trazabilidad lore → escena → asset.

### D32: Sistema de memoria por capas con presupuesto de tokens definido
- **Contexto:** Ventana de 8,192 tokens — no cabe la novela completa.
- **Decisión:** 5 capas de memoria (global, semántica, episódica, trabajo, cambios) + estrategia de contexto mínimo suficiente.
- **Presupuesto:** instrucciones 400–700 / canon global 500–900 / entidades 1,000–1,800 / capítulo activo 800–1,500 / continuidad vecina 400–800 / resto para generación.
- **Por qué:** Retrieval selectivo por tarea activa, no dump completo. Regla: si un bloque no cambia la decisión del modelo para esta tarea, no entra al prompt.

### D33: Clasificación de cambios narrativos (Expansión / Ajuste local / Retcon)
- **Contexto:** ¿Cómo mantener coherencia cuando la novela muta?
- **Decisión:** Todo cambio narrativo clasificado en una de tres categorías que determinan qué actualizar y qué mandar a reconciliación.
- **Por qué:** Sin clasificación, un cambio menor puede pasar desapercibido y romper continuidad en capítulos futuros.

### D34: Formatos de handoff canónicos definidos
- **Contexto:** Necesidad de contratos estructurados entre capas del pipeline.
- **Decisión:** 4 formatos JSON: `StoryBibleEntry`, `InteractiveSceneSpec`, `AssetSpec3D`, `ChapterMemoryRecord`.
- **Por qué:** Contratos explícitos permiten que el orquestador técnico opere sin ambigüedad y sin ver contenido sensible.

### D35: 11 workflows granulares definidos por modelo
- **Contexto:** El spec anterior definía 5 fases de alto nivel. El handoff detalla la operación concreta.
- **Decisión:** 11 workflows operativos: (1) ideación libre, (2) escritura capítulo, (3) reescritura capítulo, (4) extracción de lore canonizable, (5) diseño criaturas/horror visual, (6) análisis referencias visuales, (7) extracción interactividad, (8) normalización para orquestador, (9) orquestador, (10) Unity MCP, (11) validación y reconciliación.
- **Por qué:** Cada workflow define modelo, entradas, output contract y reglas de postproceso. Operación sin ambigüedad.
- **Fuente:** `inputs/handoff-workflows-detallados-llms-orquestador.md`

### D36: Dos nuevos tipos de job Unity definidos
- **Contexto:** Necesidad de contratos ejecutables para Unity Editor.
- **Decisión:** `UnityPlacementJob` (lista de acciones MCP: import_prefab, place_object, assign_material, add_trigger) y `UnitySceneAssemblyJob` (ensamblaje completo de escena).
- **Por qué:** El orquestador recibe un job con acciones atómicas y validaciones — nunca texto libre. Permite auditoría y reintento por acción.

### D37: Trazabilidad obligatoria en todos los artefactos
- **Contexto:** ¿Cómo mantener trazabilidad lore → asset → implementación?
- **Decisión:** Todo artefacto lleva 5 campos: `source_model`, `normalized_by`, `source_refs` (capítulos/entidades), `change_log_refs`, `unity_job_refs`.
- **Por qué:** Permite responder: ¿de qué capítulo salió? ¿qué modelo lo produjo? ¿qué job Unity lo implementó?

### D38: Estructura de directorios aprobada para servidor Debian
- **Contexto:** ¿Dónde vive el canon, los assets y los jobs?
- **Decisión:** `~/horror-game/` con subdirectorios: `canon/`, `chapters/`, `chapter_summaries/`, `entities/` (characters, locations, factions, creatures), `scene_specs/`, `branch_graphs/`, `assets/`, `jobs/unity/`, `validation/`, `refs/images/`.
- **Por qué:** Separación clara por tipo de artefacto. Jobs y validación como carpetas propias para trazabilidad.

### D39: Política de contexto con 7 niveles de prioridad
- **Contexto:** ¿Qué entra al prompt cuando hay que elegir qué cortar?
- **Decisión:** Prioridad: (1) tarea activa, (2) restricciones de canon, (3) entidades necesarias, (4) escena/capítulo relevante, (5) cambios pendientes, (6) estilo, (7) contexto opcional.
- **Reglas duras:** Nunca enviar novela completa, nunca historial bruto de chat. Un prompt = una tarea.
- **Artefactos de compresión obligatorios:** resumen corto por capítulo, resumen medio por capítulo, ficha por entidad, timeline comprimido, world rules comprimidas, diff por cambio.

---

## 2026-04-28 — Sesión 7: Mapa de Workflows

### D40: Creación de workflow_map.md como fuente de verdad para la plataforma
- **Contexto:** Los inputs existentes (`handoff-workflows-detallados-llms-orquestador.md`, `spec-workflow-creativo-orquestador-memoria.md`) cubren los workflows desde la perspectiva LLM pero no mapean todos los actores del sistema (Arturo, El Ingeniero, ComfyUI, switch-model.sh, filesystem). Este gap bloquea el diseño de una plataforma de orquestación.
- **Decisión:** Crear `outputs/workflow_map.md` — documento de referencia activa con 9 workflows detallados, todos los actores, matriz actor×workflow, catálogo de 16 contratos de handoff, sistema de memoria, y tabla de gaps identificados.
- **Por qué:** Este documento es el insumo principal para diseñar la plataforma que orquestará todos los procesos. No se auto-carga en `/memory.load` para no inflar cada apertura de sesión — se consulta on-demand cuando se trabaje en diseño de plataforma.
- **Clasificado en CLAUDE.md como:** Referencia activa on-demand en `/docs.policy`.

### D28: Estrategia de archivado para conversation_memory.md
- **Contexto:** El archivo crecerá indefinidamente degradando rendimiento de carga.
- **Decisión:** Cuando supere 50 decisiones, archivar las más antiguas a `context/conversation_memory_archive_YYYY.md` y mantener solo las últimas 30 en el archivo activo.
- **Por qué:** Mantiene el archivo de carga pequeño y rápido. El archivo de decisiones activas debe ser manejable para el contexto de Claude Code.
