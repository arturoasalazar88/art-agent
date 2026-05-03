---
id: STORY_011
title: Script batch generation storyboard via API ComfyUI
status: pending
priority: low
created: 2026-04-22
updated: 2026-05-02
depends_on: STORY_008
---

# STORY_011 — Batch Generation Storyboard via API ComfyUI

Script de generación en lote para producir múltiples imágenes de storyboard en una sola sesión, usando la API REST de ComfyUI sin intervención manual por imagen.

---

## Objetivo

Automatizar la generación de lotes de imágenes para storyboard. Dado un archivo de entrada con los prompts del storyboard, el script genera todas las imágenes en secuencia y las organiza por escena.

---

## Input esperado

```json
{
  "batch_id": "storyboard_acto1_escena3",
  "style_lock": {
    "workflow": "pony_storyboard_lock.json",
    "seed": 42,
    "steps": 25,
    "cfg": 7
  },
  "frames": [
    {"frame": 1, "prompt_ref": "prompt_abc123", "description": "Elena entra al pasillo"},
    {"frame": 2, "prompt_ref": "prompt_def456", "description": "La puerta se cierra sola"},
    {"frame": 3, "prompt_ref": "prompt_ghi789", "description": "Criatura en las sombras"}
  ]
}
```

---

## Componentes

1. **`batch_storyboard.py`** — script que:
   - Lee el JSON de lote
   - Para cada frame: llama `generate_image` via MCP server
   - Hace polling hasta completar cada imagen antes de pasar a la siguiente
   - Guarda en `assets/images/storyboard/<batch_id>/frame_001.png`, etc.
   - Genera `assets/images/storyboard/<batch_id>/manifest.json` al final

2. **Modo paralelo opcional** — generar N frames simultáneamente (solo si ComfyUI lo soporta con la carga de VRAM disponible)

---

## Criterios de aceptación

- [ ] Lote de 5+ frames generado sin intervención manual
- [ ] Imágenes organizadas por batch_id con nombres secuenciales
- [ ] `manifest.json` generado con: batch_id, timestamp, lista de frames con status y path
- [ ] Manejo de fallos por frame — continúa con el siguiente si uno falla, reporta al final
- [ ] Depende de STORY_008 (pipeline_run.py) como base

---

## Notas

- Este script es el que VOID_ENGINE invocará internamente en el workflow de "producción de storyboard"
- Los `prompt_ref` apuntan a IDs del MCP server (guardados con `save_prompt`)
- El Ingeniero nunca lee el contenido de los prompts — solo el ID y el frame number
