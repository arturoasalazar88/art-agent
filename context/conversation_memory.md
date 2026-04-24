# Memoria de Conversación — Log de Decisiones

> Última actualización: 2026-04-24
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
