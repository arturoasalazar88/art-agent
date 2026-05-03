# Session Log

> Formato: YYYY-MM-DD | Trabajado en | Artefactos | Decisiones
> Actualizar en cada /context-close — append only, nunca modificar entradas existentes.

---

2026-04-21 | Setup servidor Debian — llama.cpp, 3 modelos LLM, Open WebUI | switch-model.sh, systemd services x4 | D01–D05
2026-04-22 | ComfyUI + Pony Diffusion + VAE + LoRAs + switch image mode | pony_horror.json, pony_horror_lora.json, comfyui.service | D06–D11
2026-04-23 | Pipeline Artista/Ingeniero + MCP specs + SuperGemma Vision + switch vision | llama-vision.service, mcp-specs-survival-horror.md, pipeline-context.md | D12–D21
2026-04-24 | Context Engineering Agent — art-agent implementado y bootstrapped | CLAUDE.md, context/*.md, .claude/commands/*.md | D22
2026-04-26 | Auditoría art-agent + research hardware dual GPU + evaluación modelos (Qwen-Image, Qwen3) | context/*.md actualizados, session_log.md creado | D23–D28
2026-04-28 | Ingesta specs workflow creativo + orquestador Unity + sistema memoria — motor cambiado Three.js→Unity | project_state.md, conversation_memory.md, next_steps.md, artifacts_registry.md actualizados | D29–D39
2026-05-02 | STORY_024 Huihui Vision + Open WebUI — API validada, UI bloqueada por auth, codegen descartado para Huihui | outputs/story024_huihui_vision_openwebui_results.md, context/stories/STORY_024_huihui_vision_openwebui.md, context/*.md actualizados | D74–D75
2026-05-02 | STORY_025 Huihui texto puro — ctx=32768 OK, T1/T2 PASS hasta 32k, descartado por latencia | outputs/story025_huihui_text_ctx_validation_results.md, outputs/huihui_text_runner.py, logs STORY_025, context/*.md actualizados | D76
2026-05-02 | STORY_028 Sage (Huihui Claude 4.7) — descarga Q4_K_M, UAT 5/5 PASS (T1-T5 + ctx=32k), llama-huihui47.service, switch-model.sh sage | start-huihui47-text.sh, llama-huihui47.service, switch-model.sh actualizado, context/*.md actualizados | D89
2026-05-02 | Sesión 25 — Identidad de estudio: DArkkercornner Studios, logos registrados, fork Open WebUI descartado, fuente OTF intentada (parcial/no funcional), STORY_024 cerrada como superada por STORY_027 | assets/logo/*.png, assets/fonts/DArkkercornner.otf, scripts/build_font.py, context/*.md actualizados | D90–D92
