# Foco de Sesión

> Última actualización: 2026-05-02 (sesión 25)
> Nota: Las listas de tareas y trabajo pendiente están en `context/stories/INDEX.md`.
> Este archivo contiene solo el contexto de sesión: qué acaba de pasar y restricciones técnicas críticas.

---

## Fase Actual

**Pre-producción** — Stack de modelos completo y validado. Estudio nombrado: **DArkkercornner Studios**. Assets de identidad creados (logos). Siguiente: completar identidad de marca (fuente funcional), VOID_ENGINE base, MCP server.

---

## Completado en Sesión 25 (2026-05-02)

- [x] STORY_024 ✅ — Cerrada como superada por STORY_027. SuperGemma4 Vision cubre el objetivo original.
- [x] Nombre de estudio definido — **DArkkercornner Studios** (D90)
- [x] Logos registrados y renombrados:
  - `assets/logo/darkkercornner_studios_logo.png`
  - `assets/logo/darkkercornner_studios_logo_variant.png` (fondo negro)
  - `assets/logo/darkercornner_font.png` (specimen sheet de la fuente)
- [x] Fork Open WebUI descartado para VOID_ENGINE (D91) — stack equivocado, arquitectura chat-first
- [x] Generación de fuente OTF intentada — `assets/fonts/DArkkercornner.otf` producido con 45/52 glifos pero **no funcional** (D92). Pendiente mejor approach.

---

## Completado en Sesiones Previas

- [x] STORY_028 ✅ — Sage (Huihui Claude 4.7) adoptado, servicio activo
- [x] STORY_027 ✅ — SuperGemma4 Vision adoptado como modelo de visión
- [x] STORY_025 ✅ — Huihui sin mmproj ctx=32768 production-ready
- [x] STORY_026 ✅ — SearXNG instalado, Web Search activado
- [x] Qwen3.6-35B-A3B validado STORY_021, systemd creado STORY_022
- [x] SearXNG web search fix (D86), sudoers NOPASSWD (D87)

---

## Contexto Técnico Crítico

- **ctx-size producción Gemma 4 stack:** 24,576 con `--cache-type-k q4_0 --cache-type-v q4_0`
- **ctx-size producción Qwen3:** 40,960 con `--cache-type-k q8_0 --cache-type-v q8_0` + `--flash-attn on`
- **Qwen3 puerto:** 8013 — nunca simultáneo con 8012
- **Ornstein thinking OFF:** via wrapper `/home/asalazar/start-ornstein.sh`
- **switch-model.sh:** 7 modos — ornstein/supergemma/trevorjs/vision/sage/qwen3/image
- **llama-vision (actual):** SuperGemma4 Vision — `start-supergemma4-vision.sh`, puerto 8012, ctx=8192, thinking OFF
- **SuperGemma4 Vision:** thinking OFF obligatorio — llama.cpp b8998 no soporta Gemma 4 channel markers.
- **SearXNG:** `http://10.1.0.105:8080` — operativo, Docker restart unless-stopped.
- **Servidor sudo:** `asalazar` tiene NOPASSWD en `/etc/sudoers.d/asalazar`
- **Open WebUI web search:** configurado en "Default" — activar manualmente con ícono de búsqueda
- **Open WebUI auth:** `auth=true`, `enable_api_keys=false` — endpoints protegidos devuelven 401
- **Clawdbot:** `rdpuser@10.1.0.104`, primary: DeepSeek R1 (temporal). Restaurar a Sage pendiente.
- **Sage max_tokens:** mínimo 3000 con thinking ON
- **Servidor:** `asalazar@10.1.0.105`
- **VOID_ENGINE stack:** AdonisJS 7.x + HTMX + Alpine.js + Tailwind CSS + DaisyUI
- **DaisyUI theme:** base-100=#0b0d14, base-200=#111522, base-300=#141824, primary=#5b7cff
- **MoE Large (STORY_029):** bloqueada por RAM. Upgrade DDR4 ~$40-60 USD.
- **Modelos en disco:** gemma4/ (47GB), qwen3/ (20GB), huihui47/ (20GB), supergemma4-vision/ (17GB) — total 104GB, 26GB libres
- **Sage (Huihui 4.7):** `~/models/huihui47/`, puerto 8012, ctx=32768, KV q8_0, `llama-huihui47.service`
- **Estudio:** DArkkercornner Studios
- **Fuente DArkkercornner:** OTF generada pero no funcional — 45/52 glifos, approach vía potrace + fonttools desde PNG. Necesita revisión.
- **Font generation tools:** `potrace` (brew), Python venv en `.venv/` con Pillow + fonttools + numpy. Script en `scripts/build_font.py`.

---

## Próximos Pasos (por prioridad)

1. **Sage en Clawdbot** — restaurar primary local en `rdpuser@10.1.0.104`: cambiar de DeepSeek R1 a `http://10.1.0.105:8012/v1`
2. **Eliminar Qwen3 (decisión usuario)** — si UAT manual de Sage aprobado: detener servicio y borrar `~/models/qwen3/` (~20GB)
3. **Fuente DArkkercornner** — revisar approach: ¿intentar reparar OTF generada, o buscar la fuente original de Nano Banana Pro?
4. **VOID_ENGINE implementación base** — shell desktop 3 columnas AdonisJS/Tailwind/DaisyUI
5. **STORY_002** — MCP server FastMCP, 7 herramientas, puerto 8189
6. **STORY_029** — desbloquear con upgrade RAM 64GB (~$40-60 USD DDR4)

---

## Preguntas para el Usuario al Inicio de Sesión

- ¿UAT manual de Sage aprobado? ¿Se elimina Qwen3 (~20GB)?
- ¿Restaurar Sage como primary en Clawdbot?
- ¿Se instaló el upgrade de RAM 64GB? (desbloquea STORY_029)
- ¿Qué falló exactamente con la fuente OTF? ¿No se instaló, se instaló pero los glifos estaban mal, o no apareció en las apps?
