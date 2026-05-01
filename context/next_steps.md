# Foco de Sesión

> Última actualización: 2026-05-01 (sesión 15)
> Nota: Las listas de tareas y trabajo pendiente están en `context/stories/INDEX.md`.
> Este archivo contiene solo el contexto de sesión: qué acaba de pasar y restricciones técnicas críticas.

---

## Fase Actual

**Pre-producción** — Infraestructura completamente validada (todos los modelos). Pipeline diseñado. Agentes especializados diseñados. Siguiente: construcción de plataforma VOID_ENGINE e implementación del MCP server.

---

## Completado en Última Sesión (2026-05-01 / sesión 15)

- [x] STORY_021 completada — Qwen3.6-35B-A3B validado production-ready a ctx=32k
- [x] llama.cpp actualizado — v8998 / commit 2098fd616 / soporte nativo qwen3_5_moe
- [x] GGUF descargado — Qwen3.6-35B-A3B-Q4_K_M.gguf (21.3 GB) en ~/models/qwen3/
- [x] Suite de validación diseñada y ejecutada — 4 tests × 5 ctx-sizes (4k/8k/16k/24k/32k)
- [x] T1 PASS — JSON exacto 5/5 en todos los ctx (thinking=OFF, 1.9s a 4k, 52s a 32k)
- [x] T2 PASS — MCP tool call 5/5 en todos los ctx (thinking=OFF, 6.7s a 4k, 53s a 32k)
- [x] T3 PASS — Codegen Python 6/6 en todos los ctx (thinking=ON, ~140-200s por run)
- [x] T4 PASS — Multi-turn agentic 8/8 en todos los ctx (thinking=ON, ~87-110s)
- [x] Diagnóstico y fix de 4 fallos intermedios (max_tokens, gate check, ctx-size servidor)
- [x] outputs/qwen3_validation_results.md generado
- [x] outputs/qwen3_production_config.md generado
- [x] outputs/qwen3_runner.py generado
- [x] Decisiones D66–D70 formalizadas
- [x] Servidor de pruebas Qwen3 corriendo en puerto 8013 (manual, no systemd)

---

## Completado en Sesión 14 (2026-04-30)

- [x] STORY_019 completada — SuperGemma y TrevorJS validados production-ready a ctx=24576
- [x] Diagnóstico y descarte de story019_suite.py original — max_tokens=512 consumido por thinking, scorers regex frágiles
- [x] Rediseño del approach de validación — 4 tests cualitativos con criterios legibles por humano (sugeridos por Perplexity)
- [x] sg19_runner.py creado — runner individual por test para SuperGemma/TrevorJS
- [x] SG-1 PASS — SuperGemma: 601 palabras, criatura rica, español consistente
- [x] TJ-1 PASS — TrevorJS: brief de artista 3D completo, 670 palabras, LOD counts, SSS, vertex shader
- [x] SG-2 PASS — SuperGemma: 1,400 tokens de lore procesados, escena + dilema coherentes
- [x] TJ-2 PASS — TrevorJS: segunda criatura del mismo universo, ADN estético compartido, ENTITY_043
- [x] Ornstein re-validado con 4 tests JSON — T1/T2/T3/T4 PASS a ctx=24576, thinking OFF
- [x] T1 PASS — AssetSpec3D: JSON perfecto, height_m=2.6, limb_count=6, todos los campos correctos
- [x] T2 PASS — Extracción entidades: 5 entidades, has_radio=false (boolean), sin duplicados
- [x] T3 PASS — InteractiveSceneSpec: 3 choices, requires_flag, flags_set, triggers — directo a Unity MCP
- [x] T4 PASS — Multi-turno: has_radio preservado, former_role agregado; last_updated_turn mitigado por harness
- [x] orn_runner.py creado — runner con extractor JSON y validación automática de criterios
- [x] 4 archivos de producción generados y commiteados (resultados + configs para los 3 modelos)
- [x] Decisiones D56–D65 formalizadas (ver conversation_memory.md)

---

## Contexto Técnico Crítico

- **ctx-size producción Gemma 4 stack:** 24,576 tokens con Q4_K_M + `--cache-type-k q4_0 --cache-type-v q4_0`
- **ctx-size producción Qwen3:** 40,960 tokens con `--cache-type-k q8_0 --cache-type-v q8_0` + `--flash-attn on`
- **Todos los modelos validados:** Ornstein (STORY_001/020), SuperGemma + TrevorJS (STORY_019), Qwen3.6-35B-A3B (STORY_021)
- **Qwen3 puerto:** 8013 (Ornstein/creativos: 8012) — nunca simultáneos
- **max_tokens para modelos con thinking ON:** mínimo 2,048; recomendado 4,096 (thinking consume ~500–1,400 tok)
- **Servidor:** `asalazar@10.1.0.105` — verificar estado al inicio de cada sesión
- **MCP server (8189):** pendiente de implementación — specs en `inputs/mcp-specs-survival-horror.md`
- **ComfyUI y llama-server:** nunca simultáneos — usar `~/switch-model.sh`
- **VOID_ENGINE stack:** AdonisJS 7.x + HTMX + Alpine.js + Tailwind CSS + DaisyUI
- **DaisyUI theme custom:** base-100=#0b0d14, base-200=#111522, base-300=#141824, primary=#5b7cff, success=#56d38a, warning=#d9a441
- **VOID_ENGINE diseño:** guías propias son fuente de verdad — `outputs/void_engine_layout_guide.md` y `outputs/void_engine_ui_ux_guide.md`
- **Ornstein thinking OFF:** el flag `--chat-template-kwargs '{"enable_thinking":false}'` no sobrevive parsing de systemd — usar terminal directo o EnvironmentFile

---

## Próximos Pasos (por prioridad)

1. **Qwen3 systemd + switch-model.sh** — crear `llama-qwen3.service` y agregar como 6ª opción al switcher (pendiente confirmación del usuario tras ver resultados)
2. **VOID_ENGINE implementación base** — construir shell desktop 3 columnas en AdonisJS/Tailwind/DaisyUI desde las guías propias
3. **STORY_018** — arquitectura de orquestación VOID_ENGINE (depende de STORY_016 ✅, STORY_019 ✅, STORY_021 ✅, Ornstein ✅)
4. **STORY_017** — Blueprint Compiler (~150 líneas Python, depende de STORY_016 ✅)
5. **STORY_002** — MCP server FastMCP, 7 herramientas, puerto 8189
6. **Fix Ornstein systemd** — resolver parsing de `--chat-template-kwargs` en servicio systemd

---

## Preguntas para el Usuario al Inicio de Sesión

- ¿Hubo cambios en el servidor desde la última sesión? (Qwen3 server en puerto 8013 puede haberse caído si hubo reinicio)
- ¿Integramos Qwen3 a systemd + switch-model.sh, o primero construimos VOID_ENGINE?
- ¿Validamos ctx >32k para Qwen3, o con 32k es suficiente para el pipeline actual?
