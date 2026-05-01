# Memoria de Conversación — Log de Decisiones

> Última actualización: 2026-04-30 (sesión 14 — D62)
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

---

## 2026-04-29 — Sesión 8: Arquitectura de Agentes + Sistema de Stories

### D41: Arquitectura de memoria de agentes especializados — bloques fijos + compiler
- **Contexto:** Research de Perplexity (inputs/obsidian-context-engineering-research.md) evaluó sistemas de memoria para agentes locales con ventana de 8192 tokens.
- **Opciones:** Markdown libre, Obsidian directo al modelo, bloques fijos compilados, RAG (descartado por complejidad).
- **Decisión:** Arquitectura de dos capas — fuente humana editable (Obsidian o Markdown con frontmatter) + runtime artifact compilado con bloques fijos: IDENTITY, OPERATING_RULES, CANON, ACTIVE_GOALS, OPEN_LOOPS, RECENT_DECISIONS, EXAMPLES. Cada bloque con presupuesto propio de tokens.
- **Por qué:** Separa mantenibilidad (vault rico) de economía de tokens (artifact acotado). Letta confirma el patrón con sus "memory blocks". El compiler es el paso crítico — sin él el vault es demasiado verboso para cargarse directo.
- **Descartado:** RAG — añade complejidad innecesaria para el scope actual; Obsidian directo al modelo — demasiado verboso.

### D42: El Ingeniero como Unity assembler — dos modos de memoria
- **Contexto:** Arturo quiere que El Ingeniero ejecute también el rol de Unity assembler para evitar un agente extra, pero sin riesgo de censura por contenido narrativo.
- **Opciones:** Agente Unity separado, El Ingeniero en modo dual, agente Unity que solo ve blueprints.
- **Decisión:** El Ingeniero opera en dos modos: (1) modo sesión — memoria completa del proyecto; (2) modo ejecución Unity — solo memoria técnica mínima + job contract normalizado. Nunca se carga historia, lore ni assets/ en modo ejecución.
- **Por qué:** Ornstein ya es el firewall semántico. El Ingeniero recibe contratos normalizados (IDs, posiciones, flags), no contenido narrativo. La plataforma enforcea esto pasando solo el job file + memoria técnica al invocarlo en modo ejecución.

### D43: Blueprint Compiler como script determinístico, no LLM
- **Contexto:** Necesidad de transformar InteractiveSceneSpec (Ornstein) en SceneBlueprint puramente técnico para El Ingeniero.
- **Opciones:** Ornstein en modo blueprint (mismo modelo, segunda pasada), agente LLM dedicado, script Python determinístico.
- **Decisión:** Script Python determinístico (~100 líneas). Si InteractiveSceneSpec es JSON estructurado, la transformación es mecánica: conservar IDs/posiciones/valores, eliminar todos los campos de descripción.
- **Por qué:** Cero tokens consumidos, cero riesgo de censura, transformación predecible y auditable. Un LLM adicional solo añade latencia y punto de falla para trabajo que no requiere razonamiento.

### D44: Sistema de stories para tracking de trabajo pendiente
- **Contexto:** next_steps.md mezclaba contexto de sesión con listas de tareas, crecía sin estructura y no era navegable entre agentes.
- **Opciones:** Mantener next_steps.md expandido, Jira/Linear externo, sistema de archivos Markdown con índice.
- **Decisión:** context/stories/INDEX.md como índice maestro + archivos STORY_XXX_nombre.md individuales. INDEX.md cargado en /memory.load. next_steps.md reducido a foco de sesión y contexto técnico crítico.
- **Por qué:** File-based, portable entre Claude Code / OpenCode / Codex. El índice es compacto (~400 tokens). Los archivos individuales se cargan on-demand. Paridad garantizada via .agents/.

### D45: Opciones de ctx-size expandido — validación pendiente (STORY_001 Fase 1)
- **Contexto:** Discusión sobre si RAM libre podía expandir el contexto. Conclusión: RAM no ayuda — el KV cache vive en VRAM.
- **Opciones identificadas:** Q3_K_M (~16384 estimado), Q4_K_M + KV cache cuantizado (--cache-type-k q4_0 --cache-type-v q4_0, ~16384–24000).
- **Decisión:** Validar ambas opciones en servidor antes de definir presupuestos de tokens para agentes especializados. Documentado en STORY_001 Fase 1.
- **Por qué:** Los presupuestos de tokens de los agentes especializados dependen del ctx-size real disponible. No diseñar para 8192 si podemos tener 16384+.

---

## 2026-04-29 — Sesión 9: STORY_001 Fase 1 — Validación ctx expandido

### D46: Q4_K_M + KV q4_0 estable hasta ctx=24576 — techo de producción confirmado
- **Contexto:** STORY_001 Fase 1 — determinar el ctx-size máximo estable en RTX 3060 12GB con Ornstein Q4_K_M.
- **Test ejecutado:** Script automatizado, 3 llamadas consecutivas con prompt al 79.2% del ctx declarado, sin reparación ni re-intentos. Temperature=0.
- **Resultados:**
  - Q4_K_M + KV q4_0, ctx=16384 → **PASS** (12974 tokens reales, calls: 21.3s / 1.9s / 1.9s)
  - Q4_K_M + KV q4_0, ctx=20480 → **PASS** (16220 tokens reales, calls: 26.2s / 2.0s / 2.0s)
  - Q4_K_M + KV q4_0, ctx=24576 → **PASS** (19465 tokens reales, calls: 31.4s / 2.0s / 2.0s)
- **Decisión:** Límite de producción provisional = **ctx=24576** con `--cache-type-k q4_0 --cache-type-v q4_0`. El techo real puede ser mayor (32768 sin probar).
- **Observación de timing:** Primera llamada lenta (prefill), calls 2–3 casi instantáneas (~2s) por reutilización del KV cache. Crítico para diseño de multi-turn agéntico.
- **Por qué importa:** Los presupuestos de tokens de agentes especializados pasan de 8192 → 24576. El diseño de STORY_016 puede asumir ventanas 3× más grandes. Q3_K_M se puede omitir (Q4_K_M+KV domina en calidad y ya alcanza ctx mayor).
- **Pendiente:** Decidir si probar ctx=32768 para encontrar techo real, o proceder con 24576 como límite conservador.

### D47: Q3_K_M omitido del plan de validación
- **Contexto:** STORY_001 evaluó si valía descargar Q3_K_M para ganar ctx-size.
- **Decisión:** Omitido permanentemente.
- **Por qué:** Q4_K_M + KV q4_0 supera los ctx-sizes estimados de Q3_K_M con mejor calidad. No hay tradeoff favorable.

### D48: Suite de validación expandida a 4 bloques
- **Contexto:** El test de estabilidad original (Fase 1) validaba solo si el modelo crasheaba. No medía usabilidad (tok/s), ni calidad agéntica real.
- **Decisión:** Suite expandida a Bloque A (performance), B (estabilidad extendida), C (14 tests agénticos), D (thinking ON vs OFF por rol).
- **Por qué:** Los presupuestos de tokens y el diseño de agentes dependen de conocer tok/s, thinking budget y confiabilidad por tipo de tarea. Medir primero.

### D49: Thinking OFF para todos los roles agénticos — validado en producción
- **Contexto:** STORY_001 Bloque C corrió los 14 tests con thinking ON. Varios tests críticos fallaron (N1=0, W4=0, W5=0, V2=0) por output en prosa/markdown en lugar de JSON. STORY_020 aplicó el harness con thinking OFF.
- **Evidencia:** N1: 0→4, W4: 0→4 al apagar thinking. Thinking causa goal-completion bias en tareas estructuradas.
- **Decisión:** Thinking OFF por defecto para todos los roles agénticos (normalizer, writer, visual_spec). Regla registrada en `context/agent_harness.md`.
- **Por qué:** El thinking mode mejora razonamiento libre pero introduce sesgos en tareas con output estructurado. Para agentes que producen JSON, OFF es siempre mejor.

### D50: Harness de producción validado — weighted avg 2.25→3.92 (+74%)
- **Contexto:** STORY_001 Bloque C sin harness tenía weighted avg=2.25, 3 ceros en safety-critical. STORY_020 implementó harness (thinking OFF, system prompts explícitos, extractor de JSON robusto, retry de formato, validators corregidos).
- **Resultados:** 14/15 tests pasan umbral ≥3.5. Todos los safety-critical (7/7) al 100% pass@5. Weighted avg=3.92. Único fallo: W2 (canon multi-turno, avg=2.4, pass@5=60%) — limitación real del modelo, no de infraestructura.
- **Decisión:** Harness aprobado para producción. Reglas publicadas en `context/agent_harness.md` como input para STORY_007 (system prompts) y STORY_016 (diseño de agentes). W2 documentado como limitación conocida — mitigación: incluir estado explícito de inventario en cada turno del prompt en producción.
- **Por qué:** Los umbrales de producción se cumplen: sin ceros en safety-critical, weighted avg ≥3.5, pass@5 ≥80% excepto W2 (no safety-critical).

### D51: Canonical State Pattern — solución a multi-turn entity state tracking
- **Contexto:** W2 fallaba 2/5 runs con `has_radio=true` a pesar de que el turno 2 decía explícitamente que Elena perdía la radio. El harness v1 (thinking OFF + system prompt) mejoró de 1.0 a 2.4 pero no resolvió el fallo.
- **Diagnóstico:** El modelo usa el historial de conversación como contexto narrativo, no como fuente de verdad de estado. Con temperature=0 el resultado es no-determinístico porque el modelo "reconstruye" el estado en lugar de propagarlo.
- **Solución:** Canonical State Pattern — 4 componentes en el harness (no en el modelo):
  1. **Estado canónico externo** — dict en el harness, inicializado con estado inicial de la conversación.
  2. **Reducer determinístico** — después de cada turno, el harness aplica los eventos al estado. Si el prompt especifica un evento explícitamente, el reducer lo aplica independientemente de si el modelo lo reflejó.
  3. **CANONICAL_STATE injection** — al construir el prompt del turno siguiente, se inyecta un bloque `CANONICAL_STATE` separado del historial. El system prompt dice que ese bloque tiene prioridad sobre el historial.
  4. **Post-generation patcher** — antes de aceptar el output, el harness sobreescribe `entity_states[]` con el estado canónico. El modelo nunca tiene autoridad final.
- **Resultado:** W2: avg 2.4→4.0, pass@5 60%→100% en 5/5 runs. Weighted avg total: 3.92→4.0.
- **Observación del run:** en los 5 runs el modelo propuso correctamente en T2 Y coincidió con canonical en T3. La inyección del bloque ancló el output sin necesitar el patcher. El patcher es red de seguridad, no el mecanismo principal.
- **Regla derivada:** Historial de conversación = contexto narrativo. Estado de entidades = canonical externo inyectado. Para cualquier campo cuyo valor correcto es determinístico (inventario, posición, flags de canon), el harness es la fuente de verdad.
- **Fuente:** `context/agent_harness.md` — sección "Canonical State Pattern".

### D28: Estrategia de archivado para conversation_memory.md
- **Contexto:** El archivo crecerá indefinidamente degradando rendimiento de carga.
- **Decisión:** Cuando supere 50 decisiones, archivar las más antiguas a `context/conversation_memory_archive_YYYY.md` y mantener solo las últimas 30 en el archivo activo.
- **Por qué:** Mantiene el archivo de carga pequeño y rápido. El archivo de decisiones activas debe ser manejable para el contexto de Claude Code.

---

## 2026-04-30 — Sesión 12: VOID_ENGINE Platform UI Design

### D52: Tech stack frontend VOID_ENGINE — Tailwind CSS + DaisyUI
- **Contexto:** Se necesitaba un framework CSS para la plataforma de orquestación VOID_ENGINE construida sobre AdonisJS 7.x + HTMX + Alpine.js. La pregunta era si usar una librería de componentes o CSS puro.
- **Opciones:** Tailwind solo (máximo control, más trabajo), Tailwind + DaisyUI (componentes HTML puros + sistema de temas), Tailwind + Flowbite (más orientado a dashboards), shadcn/ui (requiere React — incompatible).
- **Decisión:** Tailwind CSS + DaisyUI.
- **Por qué:** DaisyUI usa CSS custom properties para el sistema de temas — se define la paleta una vez y todos los componentes la heredan. Los componentes son HTML puro, compatibles con HTMX y Alpine.js sin JS framework. Los prompts de diseño pueden usar nombres de componentes DaisyUI explícitos (`chat chat-start`, `badge badge-outline`, `menu menu-compact`) reduciendo ambigüedad tanto en mockups como en generación de código.

### D53: Paleta de color VOID_ENGINE definitiva — dark theme only
- **Contexto:** Múltiples iteraciones de mockup Stitch revelaron que descripciones de color ambiguas ("dark navy", glassmorphism) causaban resultados inconsistentes. Se necesitaba una paleta fija en hex sólidos.
- **Opciones:** Glassmorphism con rgba y dos acentos (azul + cyan) — descartado por Image #15 (cyberpunk neon); charcoal sólido con acento único — validado en Image #13 y #16.
- **Decisión:** DaisyUI theme custom: base-100=#0b0d14, base-200=#111522, base-300=#141824, border=#1f2535, primary=#5b7cff, success=#56d38a, warning=#d9a441, text-primary=#f4f7ff, text-muted=#8b9ec0.
- **Por qué:** Hex sólidos eliminan el problema de compositing (rgba requiere que Stitch "invente" qué hay detrás del vidrio). Acento único evita que la herramienta use colores secundarios en lugares arbitrarios. El charcoal neutro (#0b0d14) no tiene tinte azul — eso fue el problema de Image #15.
- **Descartado:** cyan #6fd3ff como acento secundario — causa resultado neon con herramientas de generación de UI.

### D54: Estrategia de mockup Stitch — layout-first, luego diseño
- **Contexto:** Después de 4+ iteraciones de prompt (v1–v4), los problemas de Stitch eran de dos tipos independientes: (1) layout incorrecto o contenido inventado, (2) colores/estilos incorrectos. Mezclarlos en un solo prompt produce fallos en ambas dimensiones simultáneamente.
- **Opciones:** Seguir iterando prompt completo (estilo + layout), separar en dos fases (layout primero, luego estilos).
- **Decisión:** Approach en dos fases: (1) `prompt_v1_layout.md` — sin estilos, solo estructura y copy exacto, valida que Stitch respete el layout de 3 columnas y el contenido correcto; (2) cuando el layout esté bloqueado, agregar encima la paleta DaisyUI.
- **Por qué:** Un prompt corto (~400 palabras) enfocado solo en estructura da a Stitch menos superficie para reinterpretar. Una vez el layout es correcto, los estilos se pueden agregar sin riesgo de perder la estructura.

---

## 2026-05-01 — Sesión 13: VOID_ENGINE Design Guides + Stitch Deprecation

### D55: Gemini/Stitch degradado a herramienta exploratoria — diseño on demand con guías propias
- **Contexto:** Se probaron cuatro prompts para Screen 01 de VOID_ENGINE (`prompt_v1_layout`, `prompt_v2_layout_fix`, `prompt_v3_text_lock`, `prompt_v4_low_trust_renderer`). Aunque algunos outputs capturaron dirección visual general, Gemini/Stitch siguió inventando workflows, labels, navegación lateral, speaker labels, version/build text y cambios de copy a pesar de reglas explícitas.
- **Opciones:** Seguir iterando prompts de Stitch, usar Stitch solo como moodboard exploratorio, o abandonar mocks generales y diseñar directamente desde guías propias en código.
- **Decisión:** Abandonar mocks generales de pantallas en Stitch. VOID_ENGINE usará guías propias de layout y UI/UX como fuente de verdad; las pantallas se diseñarán on demand según el flujo real y se implementarán directamente en AdonisJS/Tailwind/DaisyUI. Gemini/Stitch queda clasificado como herramienta exploratoria visual de baja confianza.
- **Por qué:** La plataforma necesita copy exacto, workflows controlados y layouts reproducibles. Stitch no puede garantizar fidelidad textual ni estructural. El código sí permite controlar datos, componentes, estados y comportamiento.
- **Descartado:** Prompt engineering adicional para Stitch como fuente de verdad de layout/copy; cuatro iteraciones demostraron que el costo marginal supera el valor.
- **Artefactos derivados:** `outputs/void_engine_layout_guide.md` y `outputs/void_engine_ui_ux_guide.md`.

---

## 2026-04-30 — Sesión 14: STORY_019 Validación Modelos Creativos

### D56: Open WebUI conserva puerto fijo 8012
- **Contexto:** Al integrar el modelo multimodal y los creativos, surgió la pregunta de si Open WebUI debía reconfigurar el puerto al cambiar de modelo.
- **Decisión:** Puerto fijo 8012 para todos los modelos. Open WebUI nunca se reconfigura.
- **Por qué:** D04 establece el puerto fijo como invariante. Docker ya apunta a 8012. El switch de modelo es vía systemd/terminal, no vía reconfiguración del cliente.

### D57: Configuración de thinking por rol de modelo
- **Contexto:** STORY_001/020 validaron Ornstein con thinking OFF. STORY_019 necesitaba definir la configuración para los modelos creativos.
- **Decisión:** Ornstein → ctx=24576 + KV q4_0 + **thinking OFF**. SuperGemma/TrevorJS → misma config hardware, **thinking ON** para tareas creativas.
- **Por qué:** Thinking OFF es correcto para tareas estructuradas con output JSON (Ornstein). Para modelos creativos, el thinking enriquece la calidad narrativa — validado en SG-1/TJ-1 donde el CoT produjo output más denso y coherente.

### D58: No-Assumptions Rule actualizada a v2.0
- **Contexto:** Durante el run de story019_suite.py v1, el agente asumió que los scores de 0 indicaban un bug en el scorer antes de verificar el raw output del modelo.
- **Decisión:** Regla ampliada con restricciones específicas para evaluación de métricas y scorers. "Score=0 does NOT mean output was empty — read the actual output first." Guardada en `.agents/rules/no-assumptions.md`.
- **Por qué:** Violación de la regla original causó pérdida de tiempo diagnosticando el scorer en lugar de diagnosticar el script. El error real era max_tokens insuficiente.

### D59: story019_suite.py descartada como approach de validación
- **Contexto:** El script original (455 líneas) tenía dos problemas críticos: (1) no guardaba raw output del modelo — imposible saber qué generó, (2) scorers regex frágiles para modelos uncensored que responden en inglés o sin usar IDs literales.
- **Opciones:** Reescribir suite v2 con raw output, o rediseñar el approach completo.
- **Decisión:** Descartar la suite de 9 tests regex-scored. Reemplazar con 4 tests cualitativos evaluados por humano.
- **Por qué:** Los scorers regex miden cumplimiento de formato, no calidad creativa. Un modelo que produce 600 palabras ricas en inglés puede recibir score=0 por no usar `char_elena` literalmente. El objetivo es validar que el modelo funciona a ctx=24576, no que siga instrucciones de formato estricto.

### D60: Approach de validación creativa — tests cualitativos con criterios de 30 segundos
- **Contexto:** STORY_019 necesitaba un método de validación apropiado para modelos creativos uncensored.
- **Opciones:** Scorers automáticos (descartado por D59), evaluación completamente subjetiva, criterios cualitativos legibles por humano.
- **Decisión:** 4 tests con criterios explícitos evaluables en 30 segundos: presencia de output real, coherencia con el prompt, riqueza de detalle, y — para tests de serie — consistencia de universo entre criaturas. Prompt diseñado con Perplexity. Runner individual `sg19_runner.py` para correr un test a la vez y ajustar antes del siguiente.
- **Por qué:** La validación debe responder "¿el modelo funciona para el pipeline?" no "¿el modelo siguió el formato exacto?". Un humano puede responder esa pregunta en 30 segundos leyendo el output.

### D61: max_tokens=4096 requerido para modelos con thinking ON
- **Contexto:** La suite original usaba max_tokens=512. Con thinking ON, el modelo consumía ~495 tokens de CoT, dejando 0-17 tokens para el contenido. Output vacío en todos los tests.
- **Decisión:** max_tokens mínimo 2,048 con thinking ON; recomendado 4,096 para dar margen real al contenido.
- **Por qué:** En llama.cpp, los thinking tokens cuentan contra max_tokens. Con CTX=24576 hay margen amplio — no hay razón para limitar el output. Validado: SG-1 usó 2,288 tokens de completion (1,346 thinking + ~942 contenido) con max_tokens=4096.

### D62: SuperGemma y TrevorJS validados production-ready a ctx=24576
- **Contexto:** STORY_019 — validar que los modelos creativos mantienen inteligencia y confiabilidad con la ventana de contexto expandida.
- **Tests ejecutados:** SG-1 (smoke + creatividad), TJ-1 (spec técnico visual), SG-2 (stress ctx con 1,400 tokens de lore), TJ-2 (coherencia de serie entre criaturas).
- **Resultados:** 4/4 PASS. SG-1: criatura "El Amalgama de la Veta", 601 palabras, español coherente. TJ-1: brief artista 3D completo con LOD counts y vertex shader. SG-2: escena + dilema integrando lore con precisión. TJ-2: segunda criatura (ENTITY_043) con ADN estético compartido y distinción de rol.
- **Decisión:** Ambos modelos aprobados para producción. Stack completo validado: Ornstein + SuperGemma + TrevorJS, todos a ctx=24576.
- **Por qué importa:** El pipeline de 5 fases puede ejecutarse con el hardware actual. No se necesita upgrade para iniciar producción creativa.
