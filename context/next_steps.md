# Foco de Sesión

> Última actualización: 2026-04-30 (sesión 12)
> Nota: Las listas de tareas y trabajo pendiente están en `context/stories/INDEX.md`.
> Este archivo contiene solo el contexto de sesión: qué acaba de pasar y restricciones técnicas críticas.

---

## Fase Actual

**Pre-producción** — Infraestructura validada, pipeline diseñado, agentes especializados diseñados. Iniciando diseño y construcción de plataforma de orquestación VOID_ENGINE.

---

## Completado en Última Sesión (2026-04-30)

- [x] STORY_016 completada — `outputs/agent_memory_spec.md` producido (6 roles, 10 bloques atómicos, presupuestos de tokens, Memory Compiler spec)
- [x] VOID_ENGINE: concepto de plataforma de orquestación iniciado — UI tipo workspace 3 paneles
- [x] Tech stack frontend VOID_ENGINE decidido — Tailwind CSS + DaisyUI, dark theme only
- [x] Paleta de color VOID_ENGINE definida — charcoal sólido + acento único #5b7cff
- [x] Múltiples iteraciones de mockup Stitch — Image #13 mejor resultado previo, Image #16 cercano con DaisyUI prompt
- [x] Auditoría del prompt Stitch v3 — 7 problemas identificados y documentados
- [x] Enfoque cambiado a layout-first — `prompt_v1_layout.md` creado, sin estilos, solo estructura y copy exacto
- [x] AdonisJS 7.x assessment completado — `inputs/adonisjs_assessment.md` disponible como referencia técnica

---

## Contexto Técnico Crítico

- **ctx-size producción:** 24,576 tokens con Q4_K_M + `--cache-type-k q4_0 --cache-type-v q4_0`
- **Servidor:** `asalazar@10.1.0.105` — verificar estado al inicio de cada sesión
- **MCP server (8189):** pendiente de implementación — specs en `inputs/mcp-specs-survival-horror.md`
- **ComfyUI y llama-server:** nunca simultáneos — usar `~/switch-model.sh`
- **VOID_ENGINE stack:** AdonisJS 7.x + HTMX + Alpine.js + Tailwind CSS + DaisyUI
- **DaisyUI theme custom:** base-100=#0b0d14, base-200=#111522, base-300=#141824, primary=#5b7cff, success=#56d38a, warning=#d9a441
- **Mejor mockup base:** Image #16 (DaisyUI prompt) — layout casi correcto, faltan 4 fixes de contenido
- **Stitch lecciones aprendidas:** (1) layout-first sin estilos, (2) copy exacto en el prompt, (3) hex sólidos sin rgba, (4) un solo acento, (5) adjuntar imagen de referencia

---

## Próximos Pasos (por prioridad)

1. **VOID_ENGINE mockup** — enviar `prompt_v1_layout.md` a Stitch para validar layout, luego agregar estilos encima
2. **STORY_019** — validar SuperGemma y TrevorJS (re-descargar modelos primero)
3. **STORY_018** — arquitectura de orquestación VOID_ENGINE (depende de STORY_016 ✅)
4. **STORY_017** — Blueprint Compiler (~150 líneas Python, depende de STORY_016 ✅)
5. **STORY_002** — MCP server FastMCP, 7 herramientas, puerto 8189

---

## Preguntas para el Usuario al Inicio de Sesión

- ¿Hubo cambios en el servidor desde la última sesión?
- ¿Cuál fue el resultado del research de Perplexity sobre Stitch?
- ¿Empezamos con el mockup de layout (Stitch) o con el scaffolding del proyecto AdonisJS?
