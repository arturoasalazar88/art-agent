---
id: STORY_018
title: Plataforma de orquestación VOID_ENGINE — arquitectura general
status: pending
priority: high
created: 2026-04-29
updated: 2026-05-02
depends_on: STORY_001, STORY_016
---

# STORY_018 — VOID_ENGINE: Plataforma de Orquestación

VOID_ENGINE es la plataforma web que centraliza y orquesta todos los workflows del pipeline de producción: LLMs creativos, ComfyUI, MCP server, y Unity. Es la interfaz operativa del estudio.

**Stack:** AdonisJS 7.x + HTMX + Alpine.js + Tailwind CSS + DaisyUI
**Fuentes de verdad de diseño:**
- `outputs/void_engine_layout_guide.md` — shell, columnas, dimensiones
- `outputs/void_engine_ui_ux_guide.md` — paleta, tipografía, componentes, copy
- `inputs/adonisjs_assessment.md` — fuente de verdad técnica para el stack AdonisJS

---

## Objetivo

Implementar el shell base de VOID_ENGINE: layout de 3 columnas, navegación, y la pantalla principal (Main Workspace) con los primeros widgets funcionales.

---

## Stack técnico

| Capa | Tecnología |
|---|---|
| Backend | AdonisJS 7.x (TypeScript) |
| Templates | Edge.js (motor de plantillas de Adonis) |
| Partial updates | HTMX (atributos HTML, sin JS framework) |
| Interactividad local | Alpine.js (directivas x-data, x-show, x-on) |
| Estilos | Tailwind CSS + DaisyUI |
| Streaming LLM | Server-Sent Events (SSE) via HTMX |
| Dev server | `node ace serve --hmr` (localhost:3333) |

---

## Paleta DaisyUI

```css
base-100: #0b0d14
base-200: #111522
base-300: #141824
border: #1f2535
primary: #5b7cff
success: #56d38a
warning: #d9a441
text-primary: #f4f7ff
text-muted: #8b9ec0
```

---

## Layout — Shell desktop 3 columnas

```
┌─────────────────────────────────────────────────────┐
│ Sidebar (240px) │  Main Content  │  Panel (320px)   │
│  navegación     │  (flex-1)      │  contexto/output │
│  modelos        │                │                  │
│  estado         │                │                  │
└─────────────────────────────────────────────────────┘
```

Ver `outputs/void_engine_layout_guide.md` para dimensiones exactas, reglas de scroll y breakpoints.

---

## Fases de implementación

### Fase 1 — Shell base (esta story)
- [ ] Proyecto AdonisJS 7.x inicializado con Tailwind + DaisyUI
- [ ] Layout de 3 columnas funcional (CSS Grid o Flexbox)
- [ ] Sidebar con navegación básica: Dashboard, LLMs, ComfyUI, Stories, Canon
- [ ] DaisyUI theme custom configurado con la paleta exacta
- [ ] Ruta `/` que devuelve el Main Workspace vacío
- [ ] Dev server funcionando en localhost:3333

### Fase 2 — Widget de estado de modelos
- [ ] Widget que muestra estado de cada servicio llama-server (activo/inactivo)
- [ ] HTMX polling cada 30s a endpoint `/api/services/status`
- [ ] Backend llama a `http://10.1.0.105:8012/health` y `8013/health`
- [ ] Indicadores visuales: dot verde/rojo + nombre del modelo activo

### Fase 3 — Panel de conversación con LLM
- [ ] Formulario de prompt en Main Content
- [ ] Submit via HTMX POST a `/api/chat`
- [ ] Streaming de respuesta via SSE (hx-ext="sse")
- [ ] Historial de mensajes con scroll

### Fase 4 — Integración ComfyUI
- [ ] Widget de estado ComfyUI
- [ ] Trigger de generación via API ComfyUI
- [ ] Polling de job status con HTMX
- [ ] Preview de imagen generada en el Panel derecho

---

## Criterios de aceptación (Fase 1)

- [ ] Proyecto AdonisJS 7.x corriendo en localhost:3333 sin errores
- [ ] Layout de 3 columnas visible y responsivo
- [ ] DaisyUI theme aplicado — background #0b0d14, accents correctos
- [ ] Sidebar con links de navegación funcionales (aunque las rutas devuelvan placeholder)
- [ ] Build sin errores TypeScript

---

## Notas

- Leer `inputs/adonisjs_assessment.md` antes de empezar — es el assessment técnico completo del stack
- No usar React, Vue ni Svelte — VOID_ENGINE es intenciones HTMX + Alpine.js + Edge.js
- Las pantallas se diseñan con guías propias, no con mocks de Stitch (D55)
- El proyecto VOID_ENGINE vive en el repositorio `art-agent` en la carpeta `void_engine/` o como repositorio separado (definir antes de implementar)
