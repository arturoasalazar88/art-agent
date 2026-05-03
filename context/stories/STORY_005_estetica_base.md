---
id: STORY_005
title: Estética base del juego — vision + imágenes de referencia
status: in_progress
priority: medium
created: 2026-04-22
updated: 2026-05-02
depends_on: —
---

# STORY_005 — Estética Base del Juego

Definir la dirección de arte del juego usando imágenes de referencia analizadas con Vision, para producir un `ArtDirectionBrief` canónico que guíe todos los assets visuales del proyecto.

---

## Objetivo

Producir `outputs/art_direction_brief.md` — el documento de referencia visual que define la estética, paleta, iluminación, mood y restricciones visuales del juego. Este documento es el input para STORY_006 (LoRAs) y el system prompt visual de TrevorJS.

---

## Flujo de trabajo

1. Arturo reúne 3–5 imágenes de referencia visual en `~/horror-game/refs/images/` en el servidor
2. SuperGemma4 Vision analiza cada imagen (switch a modo `vision`)
3. Ornstein normaliza los análisis en un `ArtDirectionBrief` estructurado
4. El Ingeniero registra el brief en `outputs/art_direction_brief.md`

---

## Criterios de aceptación

- [ ] Al menos 3 imágenes de referencia en `~/horror-game/refs/images/`
- [ ] Vision analiza cada imagen y produce descripción técnica (composición, paleta, iluminación, mood)
- [ ] Ornstein produce `ArtDirectionBrief` con: paleta de color dominante, tipo de iluminación, mood visual, restricciones de estética, keywords para prompts
- [ ] Documento registrado en `outputs/art_direction_brief.md`
- [ ] Brief revisado y aprobado por Arturo

---

## Campos esperados en ArtDirectionBrief

```json
{
  "palette": {
    "dominant": [],
    "accent": [],
    "forbidden": []
  },
  "lighting": {
    "type": "",
    "mood": "",
    "shadows": ""
  },
  "visual_keywords": [],
  "style_references": [],
  "forbidden_elements": [],
  "asset_guidelines": {
    "creatures": "",
    "environments": "",
    "characters": ""
  }
}
```

---

## Notas

- Está marcado como 🟡 en el INDEX porque es un trabajo recurrente — se actualiza cada vez que se añaden nuevas referencias.
- Las referencias pueden ser imágenes propias o capturas de juegos/películas de referencia.
- Vision solo describe — nunca genera contenido creativo. Ornstein traduce las descripciones a guidelines técnicas.
