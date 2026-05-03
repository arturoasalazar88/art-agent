---
id: STORY_013
title: Fichas de personaje con Ornstein
status: pending
priority: medium
created: 2026-04-28
updated: 2026-05-02
depends_on: —
---

# STORY_013 — Fichas de Personaje con Ornstein

Generar las fichas canónicas de los personajes del juego usando Ornstein como normalizador. Las fichas son el input del sistema de memoria de agentes especializados y la fuente de verdad para Unity.

---

## Objetivo

Producir fichas JSON canónicas para los personajes principales del juego en `~/horror-game/entities/characters/`. Cada ficha sigue el formato `StoryBibleEntry` y es directamente consumible por Ornstein en tareas de continuidad narrativa.

---

## Flujo de trabajo

1. Arturo define los personajes principales (nombres, roles, conceptos) con SuperGemma
2. Ornstein normaliza cada personaje en formato `StoryBibleEntry`
3. El Ingeniero guarda las fichas en `~/horror-game/entities/characters/`
4. Las fichas se registran en `canon/canon_index.json`

---

## Schema StoryBibleEntry (personaje)

```json
{
  "id": "char_<slug>",
  "type": "character",
  "name": "",
  "role": "protagonist|antagonist|npc|creature",
  "status": "alive|dead|unknown",
  "facts": [],
  "appearance": {
    "height": "",
    "build": "",
    "notable_features": []
  },
  "inventory": {},
  "relationships": {},
  "last_known_location": "",
  "arc": "",
  "source_refs": [],
  "normalized_by": "Ornstein",
  "created": "",
  "updated": ""
}
```

---

## Criterios de aceptación

- [ ] Al menos 3 fichas de personaje creadas (protagonista + 2 NPCs/antagonistas clave)
- [ ] Todas en formato JSON válido con campos `StoryBibleEntry`
- [ ] Guardadas en `~/horror-game/entities/characters/<id>.json`
- [ ] Registradas en `canon/canon_index.json`
- [ ] Revisadas y aprobadas por Arturo

---

## Notas

- Arturo define la historia y los personajes — el Ingeniero solo ejecuta la normalización con Ornstein
- Las fichas son living documents — se actualizan a medida que la novela evoluciona
- El Canonical State Pattern (D51) aplica cuando Ornstein actualiza fichas en multi-turn
