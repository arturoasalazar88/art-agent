---
id: STORY_003
title: Estructura ~/horror-game/ en servidor Debian
status: pending
priority: medium
created: 2026-04-28
updated: 2026-05-02
depends_on: —
---

# STORY_003 — Estructura ~/horror-game/

Crear la estructura de directorios en el servidor Debian que albergará todo el canon, los capítulos, las entidades, los assets normalizados y los jobs de Unity. Esta estructura es el filesystem del pipeline de 5 fases.

---

## Objetivo

Crear `~/horror-game/` con todos los subdirectorios y archivos de inicialización mínimos para que los modelos y el orquestador puedan operar desde el primer día de producción creativa.

---

## Estructura objetivo

```
~/horror-game/
  canon/
    story_bible.md          # Hechos, entidades, tono, estado canónico
    world_rules.md          # Reglas del mundo — física, magia, restricciones
    timeline.md             # Línea de tiempo del universo
    canon_index.json        # Índice de entradas canónicas
    change_log.json         # Registro de retcons y ajustes
  chapters/
    ch_01.md                # Capítulos de la novela base (SuperGemma → Ornstein)
  chapter_summaries/
    ch_01.json              # Resumen corto + medio por capítulo (Ornstein)
  entities/
    characters/             # Fichas de personaje (Ornstein)
    locations/              # Fichas de locación
    factions/               # Fichas de facción
    creatures/              # Fichas de criatura (TrevorJS → Ornstein)
  scene_specs/              # InteractiveSceneSpec JSON (Ornstein)
  branch_graphs/            # BranchGraphSpec JSON (Ornstein)
  assets/
    prompts/                # Prompts ComfyUI (save_prompt del MCP)
    images/                 # Imágenes generadas por ComfyUI
    specs/                  # AssetSpec3D, CreatureVariantCard JSON (Ornstein)
  jobs/
    unity/                  # UnityPlacementJob, UnitySceneAssemblyJob JSON
  validation/
    reconciliation_report.json
  refs/
    images/                 # Referencias visuales para análisis con Vision
```

---

## Criterios de aceptación

- [ ] Directorios creados en `~/horror-game/` en `asalazar@10.1.0.105`
- [ ] Archivos placeholder `.gitkeep` en carpetas vacías (o README mínimo)
- [ ] `canon/story_bible.md` con template vacío (campos: title, premise, tone, world_rules_refs, entities)
- [ ] `canon/change_log.json` con array vacío `[]`
- [ ] `canon/canon_index.json` con objeto vacío `{}`
- [ ] Permisos correctos para usuario `asalazar`
- [ ] Estructura verificada con `tree ~/horror-game/` (o `find`)

---

## Notas

- Los archivos en `assets/prompts/` son escritos por el MCP server (STORY_002) — crear la carpeta ahora aunque el MCP no esté listo.
- La estructura completa está definida en D38 (conversation_memory.md).
