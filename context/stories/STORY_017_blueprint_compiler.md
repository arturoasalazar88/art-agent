---
id: STORY_017
title: Blueprint Compiler — Ornstein → SceneBlueprint sin arte
status: pending
priority: medium
created: 2026-04-29
updated: 2026-05-02
depends_on: STORY_016
---

# STORY_017 — Blueprint Compiler

Script Python determinístico que transforma un `InteractiveSceneSpec` (producido por Ornstein, puede contener referencias narrativas) en un `SceneBlueprint` puramente técnico, apto para ser consumido por El Ingeniero sin exposición a contenido narrativo.

---

## Objetivo

El Blueprint Compiler es el firewall semántico entre la capa creativa (Ornstein + historia) y la capa técnica (El Ingeniero + Unity). Un script Python de ~100 líneas, determinístico, cero LLM, que filtra mecánicamente los campos técnicos de los campos narrativos.

**Referencia:** D43 en `conversation_memory.md` — la decisión de implementarlo como script Python, no como LLM.

---

## Input: InteractiveSceneSpec

```json
{
  "scene_id": "scene_vault_antechamber",
  "description": "Sala antes de la bóveda. Elena huele a sangre...",
  "choices": [
    {
      "id": "choice_open_door",
      "label": "Abrir la puerta",
      "description": "Elena empuja la puerta con el hombro ensangrentado...",
      "requires_flag": "has_key",
      "sets_flag": "vault_opened",
      "next_scene": "scene_vault_interior"
    }
  ],
  "triggers": [...],
  "spawn_points": [...],
  "assets": ["asset_door_001", "asset_bloodstain_003"],
  "source_refs": ["ch_04", "scene_specs/s003.json"]
}
```

---

## Output: SceneBlueprint (limpio para El Ingeniero)

```json
{
  "scene_id": "scene_vault_antechamber",
  "choices": [
    {
      "id": "choice_open_door",
      "requires_flag": "has_key",
      "sets_flag": "vault_opened",
      "next_scene": "scene_vault_interior"
    }
  ],
  "triggers": [...],
  "spawn_points": [...],
  "asset_ids": ["asset_door_001", "asset_bloodstain_003"]
}
```

**Campos eliminados:** `description` (a cualquier nivel), `label` (texto visible), `source_refs`.

---

## Reglas de transformación

| Campo | Acción |
|---|---|
| `description` (raíz o anidado) | Eliminar siempre |
| `label` (texto de choice) | Eliminar — El Ingeniero no necesita el label |
| `source_refs` | Eliminar — solo relevante para trazabilidad literaria |
| `scene_id`, `choices[].id`, flags, `next_scene` | Conservar — son IDs técnicos |
| `triggers`, `spawn_points` | Conservar campos técnicos, eliminar descripciones internas |
| `asset_ids` | Conservar como lista plana de IDs |

---

## Criterios de aceptación

- [ ] Script `outputs/blueprint_compiler.py` implementado
- [ ] Input: `InteractiveSceneSpec` JSON válido
- [ ] Output: `SceneBlueprint` JSON sin ningún campo narrativo (description, label, source_refs)
- [ ] Test con 3 specs de ejemplo — output validado manualmente
- [ ] Caso borde: spec con descripciones anidadas en N niveles — todas eliminadas
- [ ] Script idempotente — correr dos veces produce el mismo output
- [ ] Cero dependencias externas (solo stdlib Python)

---

## Notas

- Este script es ~100 líneas de Python — no LLM, no FastMCP, solo transformación de diccionarios
- El Ingeniero llama este script como pre-procesamiento antes de ejecutar cualquier `UnityPlacementJob`
- VOID_ENGINE lo invocará automáticamente en el workflow de "montaje de escena"
