---
id: STORY_010
title: IPAdapter en ComfyUI para consistencia de personajes
status: pending
priority: low
created: 2026-04-22
updated: 2026-05-02
depends_on: —
---

# STORY_010 — IPAdapter para Consistencia de Personajes

IPAdapter es un nodo de ComfyUI que usa una imagen de referencia como guía visual para generar imágenes que mantienen la identidad del personaje (cara, proporciones, estilo) a través de diferentes poses y escenas.

---

## Objetivo

Instalar y configurar IPAdapter en ComfyUI y crear un workflow que permita generar múltiples imágenes de un personaje con identidad visual consistente usando una imagen de referencia.

---

## Componentes a instalar

1. **ComfyUI-IPAdapter-plus** — nodo IPAdapter en ComfyUI Manager
2. **Modelo IPAdapter SDXL** — `ip-adapter_sdxl.safetensors` o `ip-adapter-plus_sdxl_vit-h.safetensors`
3. **CLIP Vision SDXL** — modelo de visión requerido por IPAdapter

---

## Workflow

```
imagen_referencia_personaje.png
    ↓
IPAdapter (strength: 0.6–0.8)
    ↓
Pony Diffusion V6 XL + LoRAs
    ↓
imagen generada con identidad preservada
```

---

## Criterios de aceptación

- [ ] IPAdapter instalado via ComfyUI Manager
- [ ] Modelos IPAdapter SDXL descargados en `~/ComfyUI/models/ipadapter/`
- [ ] CLIP Vision SDXL disponible
- [ ] Workflow `pony_ipadapter_character.json` funcional
- [ ] Test: 3 imágenes del mismo personaje en poses distintas — identidad visual claramente consistente
- [ ] Documentado en `outputs/ipadapter_config.md`

---

## Notas

- IPAdapter requiere una imagen de referencia limpia del personaje — producirla primero con SuperGemma/TrevorJS + ComfyUI base
- La strength del IPAdapter (0.6–0.8) controla el balance entre seguir el prompt y mantener la identidad visual — calibrar por personaje
- Compatible con style lock (STORY_009) — combinar ambas técnicas para storyboard con personaje consistente
