---
id: STORY_004
title: Investigar Unity MCP — compatibilidad con pipeline local
status: research
priority: medium
created: 2026-04-28
updated: 2026-05-02
depends_on: —
blocks: STORY_012
---

# STORY_004 — Unity MCP Research

Antes de construir el layer de ensamblaje Unity del pipeline, necesitamos validar que Unity MCP funciona con nuestra configuración local y entender exactamente qué herramientas expone.

---

## Objetivo

Determinar si Unity MCP es viable como capa de ensamblaje interactivo para el pipeline de 5 fases. Producir un documento de hallazgos con: herramientas disponibles, limitaciones conocidas, requerimientos de versión, y gaps vs lo que necesita el pipeline.

---

## Preguntas a responder

1. ¿Cuál es la versión mínima de Unity compatible con Unity MCP?
2. ¿Qué herramientas expone el servidor MCP de Unity? (import_prefab, place_object, assign_material, add_trigger, etc.)
3. ¿Cómo se instala y configura el servidor MCP en un proyecto Unity?
4. ¿El servidor corre local o requiere conexión a servicios de Anthropic?
5. ¿Soporta SSE y stdio (mismos transportes que nuestro MCP server)?
6. ¿Puede recibir contratos JSON (`UnityPlacementJob`, `UnitySceneAssemblyJob`) directamente?
7. ¿Cuáles son las limitaciones conocidas para uso en pipeline automatizado?

---

## Herramientas que necesitamos (mínimo viable)

Según D36 y el pipeline de 5 fases:

| Herramienta | Descripción |
|---|---|
| `import_prefab` | Importar asset al proyecto |
| `place_object` | Colocar GameObject en la escena con posición/rotación/escala |
| `assign_material` | Asignar material a un objeto |
| `add_trigger` | Agregar trigger/collider de evento |
| `create_scene` | Crear nueva escena vacía |
| `save_scene` | Guardar escena actual |

---

## Output esperado

Documento `outputs/unity_mcp_research.md` con:
- Tabla de herramientas disponibles vs herramientas necesarias (gap analysis)
- Instrucciones de instalación paso a paso
- Decisión de viabilidad: ¿proceder con Unity MCP o buscar alternativa?

---

## Notas

- Repo de referencia: `https://github.com/CoderGamester/mcp-unity` (o el oficial de Anthropic si existe)
- Si Unity MCP no cubre las herramientas necesarias, evaluar alternativa: script Python que llame a la Unity Editor API via `UnityEditor` reflection o la API REST de Unity Cloud.
