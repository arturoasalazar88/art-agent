---
id: STORY_006
title: Afinar LoRA strengths por tipo de asset
status: in_progress
priority: medium
created: 2026-04-22
updated: 2026-05-02
depends_on: —
---

# STORY_006 — LoRA Strengths por Tipo de Asset

Los tres LoRAs activos (horror_style, gore_details, dark_fantasy_arch) tienen strengths fijas actualmente: 0.7, 0.5, 0.4. Esta story los calibra por tipo de asset para maximizar la calidad de cada categoría de generación.

---

## Objetivo

Determinar los strengths óptimos de cada LoRA para los tipos de asset del juego: criaturas, environments, personajes e ítems. Producir una tabla de configuración que se incorpore al workflow `pony_horror_lora.json`.

---

## LoRAs activos

| LoRA | Strength actual | Función |
|---|---|---|
| `horror_style` | 0.7 | Atmósfera y mood general |
| `gore_details` | 0.5 | Anatomía gore y detalles viscerales |
| `dark_fantasy_arch` | 0.4 | Arquitectura decadente y ambientes |

---

## Tipos de asset a calibrar

| Tipo | Descripción | LoRAs más relevantes |
|---|---|---|
| Criatura | Entidades horror, monsters, aberraciones | gore_details (alto), horror_style (medio) |
| Environment | Escenas, locaciones, arquitectura | dark_fantasy_arch (alto), horror_style (medio) |
| Personaje | Protagonistas, NPCs | horror_style (bajo), gore_details (mínimo) |
| Ítem | Objetos, armas, herramientas | dark_fantasy_arch (bajo), horror_style (bajo) |

---

## Proceso de calibración

1. Generar 3–5 imágenes por tipo de asset con diferentes combinaciones de strengths
2. Evaluar visualmente con Arturo
3. Registrar la combinación ganadora por tipo
4. Actualizar `pony_horror_lora.json` con los perfiles por tipo
5. Opcionalmente crear workflows específicos por tipo: `pony_creature.json`, `pony_environment.json`, etc.

---

## Criterios de aceptación

- [ ] Al menos 3 variaciones generadas por cada tipo de asset (12 imágenes mínimo)
- [ ] Tabla de strengths óptimos definida y aprobada por Arturo
- [ ] `pony_horror_lora.json` actualizado con los strengths base aprobados
- [ ] Workflows específicos por tipo (opcional si los strengths varían significativamente)

---

## Notas

- ComfyUI debe estar activo (switch a modo `image`) para las generaciones
- Los prompts de test los genera Arturo con SuperGemma/TrevorJS — el Ingeniero solo ejecuta los jobs
- La tabla final se incorpora al `ArtDirectionBrief` de STORY_005 como sección de configuración técnica
