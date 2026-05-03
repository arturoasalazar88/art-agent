---
id: STORY_002
title: MCP Server — Implementación FastMCP, 7 herramientas, puerto 8189
status: pending
priority: high
created: 2026-04-23
updated: 2026-05-02
depends_on: STORY_001
blocks: STORY_008
---

# STORY_002 — MCP Server

Implementar el servidor MCP que conecta al Artista (modelos locales) con el Ingeniero (agente técnico). Es el puente del pipeline: el Artista guarda prompts y el Ingeniero los ejecuta en ComfyUI sin ver el contenido creativo.

---

## Objetivo

Servidor MCP corriendo en `http://10.1.0.105:8189` con FastMCP (Python), transporte SSE + stdio, compatible con Claude Code, Gemini CLI y Open WebUI sin modificaciones adicionales.

**Fuente de verdad técnica:** `inputs/mcp-specs-survival-horror.md` — leer antes de implementar.

---

## Herramientas MCP a implementar

| Herramienta | Rol | Descripción |
|---|---|---|
| `save_prompt` | Artista | Guarda prompt + metadata en `assets/prompts/<id>.json`. El ingeniero nunca lee los campos `prompt`/`negative_prompt`. |
| `generate_image` | Ingeniero | Dispara job ComfyUI usando `generation` + `output` del JSON. No lee el contenido creativo. |
| `list_prompts` | Ambos | Lista prompts disponibles con metadata y estado. |
| `get_prompt_metadata` | Ingeniero | Devuelve solo `metadata`, `generation` y `output` — nunca `prompt`/`negative_prompt`. |
| `get_job_status` | Ingeniero | Estado del job ComfyUI en curso. |
| `list_workflows` | Ingeniero | Lista workflows JSON disponibles en `~/ComfyUI/workflows/`. |
| `list_models` | Ingeniero | Lista checkpoints, VAEs y LoRAs disponibles en ComfyUI. |

---

## Schema JSON para prompts

```json
{
  "id": "prompt_<timestamp>",
  "prompt": "...",
  "negative_prompt": "...",
  "metadata": {
    "title": "...",
    "asset_type": "creature|environment|character|item",
    "tags": [],
    "created_by": "SuperGemma|TrevorJS|Arturo",
    "source_refs": []
  },
  "generation": {
    "workflow": "pony_horror_lora.json",
    "width": 1024,
    "height": 1024,
    "steps": 25,
    "cfg": 7,
    "sampler": "euler"
  },
  "output": {
    "status": "pending|queued|running|completed|failed",
    "job_id": null,
    "image_path": null,
    "generated_at": null
  }
}
```

---

## Criterios de aceptación

- [ ] FastMCP instalado y servidor arranca en puerto 8189
- [ ] `save_prompt` guarda JSON correcto en `assets/prompts/`
- [ ] `generate_image` dispara job real en ComfyUI y devuelve `job_id`
- [ ] `get_prompt_metadata` NO expone campos `prompt` ni `negative_prompt`
- [ ] `get_job_status` retorna estado actualizado del job
- [ ] `list_workflows` y `list_models` funcionan con ComfyUI activo
- [ ] Conecta desde Claude Code via MCP stdio
- [ ] Servicio systemd `mcp-server.service` en el servidor
- [ ] Smoke test end-to-end: save_prompt → generate_image → get_job_status → imagen generada

---

## Notas técnicas

- ComfyUI debe estar activo (modo `image`) para `generate_image`. El MCP debe manejar el caso donde ComfyUI no está corriendo y retornar error descriptivo.
- El servidor MCP corre en el host Debian `10.1.0.105` — Claude Code lo invoca via SSH o red local.
- Leer `inputs/mcp-specs-survival-horror.md` para los contratos exactos antes de escribir código.
