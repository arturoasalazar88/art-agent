# VOID_ENGINE — Screen 01
# Prompt v1 — Layout only

---

## PROMPT PARA STITCH

Design a desktop web app UI called VOID_ENGINE. Focus only on layout structure and exact content placement. Do not add decorative elements. Use any dark color scheme.

---

## STRUCTURE

Full 1440px desktop viewport. Five zones top to bottom:

1. Top bar — 44px tall
2. Three columns side by side, filling all remaining height:
   - Left column: exactly 260px wide, fixed
   - Center column: fills all remaining space (flex-1)
   - Right column: exactly 260px wide, fixed
3. Bottom bar — 28px tall

The three columns must touch each other with no gap. Only a 1px line separates them.

---

## ZONE 1 — TOP BAR

Left side:
- Small square with text "V_"
- Next to it: text "VOID_ENGINE"

Right side:
- Three icon buttons: settings gear, eye, sliders/filter

---

## ZONE 2A — LEFT COLUMN (260px)

Title: CONTEXTO ACTIVO

Block: MEMORIA CARGADA
Five rows. Each row has a label on the left and a value on the right:
- project_state — ✓ cargado
- artifacts_registry — ✓ cargado
- conversation_memory — D01–D51
- next_steps — ✓ cargado
- stories_index — 18 stories

Block: STORY ACTIVA
- Text: STORY_017
- Small badge next to it with text: pendiente

Block: ENTIDADES ACTIVAS
- Two small pill/chips side by side: Ornstein · Memory Compiler

Block: ESTADO CANÓNICO
Three rows, label left and value right:
- ctx_used — 11,240
- workflow — WF-02
- turno — 2/3

---

## ZONE 2B — CENTER COLUMN

This column has four sub-zones stacked top to bottom:

**Sub-zone 1 — Session buttons** (thin bar at top of column)
Four buttons in a row:
- Checkpoint
- Guardar decisión
- Cerrar sesión
- Limpiar chat

**Sub-zone 2 — Context bar** (thin bar below buttons)
Left side:
- Filled pill: "WF-02 Escritura capítulo"
- Thin vertical divider
- Label: "Model"
- Outline pill: "Ornstein"

Right side:
- Three dots: ●●●
- Text: "Turno 2/3"

**Sub-zone 3 — Chat messages** (fills remaining height, scrollable)
Two messages:

Message 1 — aligned to the LEFT:
- Text: "Aquí está el SceneBlueprint normalizado para el Capítulo 3:"
- Code block below the text containing:
```
{
  "scene_id": "CH03_MANSION",
  "entities": ["Viktor", "Sombra"],
  "mood": "paranoia"
}
```
- Small label below the code block: "guardado en outputs/"

Message 2 — aligned to the RIGHT:
- Text: "Perfecto. Ahora extrae las entidades activas del capítulo."

**Sub-zone 4 — Input area** (thin bar at bottom of column)
- Wide text input field with placeholder: "Escribe un mensaje..."
- Send button on the right of the input

---

## ZONE 2C — RIGHT COLUMN (260px)

Title: STUDIO

Block: WORKFLOWS
Nine items in a vertical list. WF-02 is the active/highlighted item:
- WF-01 Preparación
- WF-02 Escritura capítulo  ← ACTIVE
- WF-03 Revisión de estilo
- WF-04 Integración de lore
- WF-05 Normalización
- WF-06 Extracción
- WF-07 Interactividad
- WF-08 Firewall semántico
- WF-09 Compilación final

Block: OUTPUTS DE SESIÓN
Three items in a list with a small file icon each:
- CH03_blueprint.json
- entities_extracted.json
- session_checkpoint.md

---

## ZONE 3 — BOTTOM BAR

Single horizontal row left to right:
- Green dot + text: "Ornstein online"
- Thin vertical divider
- Text "CTX" + a small horizontal progress bar at 46% + text "11,240 / 24,576"
- Thin vertical divider
- Text: "WF-02 Escritura capítulo · STORY_017"

---

## RULES

- Render at 1440px wide desktop
- All nine workflow items must be visible in the right column
- Both chat messages must be visible (left-aligned AI, right-aligned user)
- Do not invent content — use the exact text specified above
- Do not add sections or elements not listed here
