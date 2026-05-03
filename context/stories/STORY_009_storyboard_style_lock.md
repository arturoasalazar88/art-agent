---
id: STORY_009
title: Workflow storyboard con style lock en ComfyUI
status: pending
priority: low
created: 2026-04-22
updated: 2026-05-02
depends_on: —
---

# STORY_009 — Workflow Storyboard con Style Lock

Para el storyboard del juego necesitamos consistencia visual entre imágenes de la misma escena o secuencia. Style lock es la técnica de fijar los parámetros visuales (seed, sampler, LoRA strengths) y solo variar el prompt de contenido.

---

## Objetivo

Crear un workflow ComfyUI con style lock implementado que permita generar múltiples imágenes de una secuencia de storyboard con consistencia visual garantizada.

---

## Concepto de style lock

```
Parámetros fijos (el "lock"):
  seed: 42 (o cualquier seed fija)
  sampler: euler
  steps: 25
  cfg: 7
  LoRA strengths: horror_style 0.7, dark_fantasy_arch 0.4

Parámetros variables (el contenido):
  prompt: cambia por cada frame del storyboard
  negative_prompt: igual para toda la serie
```

---

## Componentes

1. **`pony_storyboard_lock.json`** — workflow ComfyUI con:
   - Parámetros visuales fijos (seed, sampler, steps, cfg, LoRA strengths)
   - Campo de prompt como único input variable
   - Salida con nombre de archivo que incluye número de frame

2. **`storyboard_batch.py`** — script que:
   - Lee una lista de prompts de escena (de un JSON o archivo de texto)
   - Ejecuta el workflow para cada prompt via API ComfyUI
   - Guarda las imágenes con nombres secuenciales: `storyboard_frame_001.png`, etc.

---

## Criterios de aceptación

- [ ] Workflow `pony_storyboard_lock.json` creado y validado en ComfyUI
- [ ] 3 imágenes de prueba de la misma escena con prompts distintos muestran consistencia visual clara
- [ ] `storyboard_batch.py` ejecuta un lote de 5+ prompts sin intervención manual
- [ ] Imágenes guardadas con nombres secuenciales en `assets/images/storyboard/`

---

## Notas

- IPAdapter (STORY_010) puede complementar el style lock con consistencia de personaje específico — son técnicas ortogonales
- El seed fijo garantiza misma composición base; IPAdapter garantiza identidad visual del personaje
