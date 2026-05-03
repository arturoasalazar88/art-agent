---
id: STORY_008
title: Pipeline automatizado LLM → ComfyUI
status: pending
priority: medium
created: 2026-04-23
updated: 2026-05-02
depends_on: STORY_002
---

# STORY_008 — Pipeline Automatizado LLM → ComfyUI

Automatizar el flujo completo desde que Ornstein produce un `AssetSpec3D` hasta que ComfyUI genera la imagen. El objetivo es que el Ingeniero pueda ejecutar el pipeline completo con un solo comando.

---

## Objetivo

Script o conjunto de scripts que tomen un `AssetSpec3D` JSON como input y produzcan una imagen generada en ComfyUI como output, pasando por el MCP server sin que el Ingeniero vea el contenido creativo.

---

## Flujo completo

```
Arturo + TrevorJS → prompt gore/visual
    ↓
Ornstein → AssetSpec3D JSON (incluye prompt normalizado en campo opaco)
    ↓
MCP save_prompt → assets/prompts/<id>.json
    ↓
MCP generate_image → ComfyUI job
    ↓
MCP get_job_status (polling) → job completado
    ↓
imagen en assets/images/<id>.png
    ↓
AssetSpec3D.output.image_path actualizado
```

---

## Componentes a implementar

1. **`pipeline_run.py`** — script orquestador que:
   - Toma `<asset_spec_id>` como argumento
   - Lee `assets/specs/<id>.json` (solo campos no creativos)
   - Llama `generate_image` via MCP
   - Hace polling de `get_job_status` cada 5s
   - Actualiza `output.image_path` y `output.status` en el JSON
   - Imprime progreso en consola

2. **Switch automático a modo imagen** — antes de llamar a ComfyUI, verificar si está activo. Si no, advertir al usuario (no auto-switch — riesgo de cortar modelo LLM en uso).

---

## Criterios de aceptación

- [ ] `python3 pipeline_run.py <asset_spec_id>` ejecuta el flujo completo
- [ ] El script lee solo metadata/generation/output — nunca prompt/negative_prompt
- [ ] Polling funciona correctamente hasta job completado o fallido
- [ ] Imagen guardada en `assets/images/` con nombre basado en el ID del asset
- [ ] JSON del asset actualizado con `image_path` y `generated_at`
- [ ] Manejo de error si ComfyUI no está activo (mensaje descriptivo, no crash)
- [ ] Test end-to-end documentado en `outputs/pipeline_test_results.md`

---

## Notas

- Depende de STORY_002 (MCP server) que debe estar implementado primero
- El switch de modelo es manual — el script advierte pero no cambia de modo automáticamente
- En producción, este script es invocado por VOID_ENGINE desde su backend
