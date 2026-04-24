# 🎮 art-agent

> Un compañero de IA con memoria persistente para el desarrollo de un videojuego de survival horror indie, construido con Three.js, Blender y un pipeline de producción completamente local.

---

## ¿Qué es esto?

**art-agent** es un agente de [context-engineering](SPEC_context_engineering_agent.md) que corre dentro de [Claude Code](https://claude.ai/code). Funciona como co-piloto técnico para un videojuego de survival horror — recordando cada decisión, cada detalle de infraestructura y cada tarea pendiente entre sesiones, sin necesidad de ser re-briefeado nunca.

No es un chatbot. Es un **compañero de ingeniería con estado persistente**, respaldado por archivos de memoria en markdown.

---

## El Proyecto

Un videojuego de survival horror construido con:

| Capa | Tecnología |
|---|---|
| Motor del juego | Three.js |
| Assets 3D | Blender |
| Generación de imágenes | ComfyUI + Pony Diffusion V6 XL |
| LLMs creativos | Gemma 4 26B (local, uncensored) |
| Runtime | llama.cpp server en Debian + RTX 3060 |
| Protocolo de agente | MCP (Model Context Protocol) via FastMCP |

El pipeline aplica una separación estricta **Artista / Ingeniero**: los LLMs locales uncensored manejan el contenido creativo (lore, prompts gore, diálogos), mientras el agente ingeniero maneja solo la ejecución técnica — sin ver ni generar contenido creativo.

---

## Arquitectura del Agente

```
art-agent/
├── CLAUDE.md                          ← Identidad, reglas y protocolos del agente
├── context/
│   ├── project_state.md               ← Infraestructura, equipo, modelos, riesgos (estable)
│   ├── artifacts_registry.md          ← Todos los archivos y su estado
│   ├── conversation_memory.md         ← Log comprimido de decisiones (D01–D22+)
│   └── next_steps.md                  ← Estado actual y próximas acciones (volátil)
├── .claude/commands/
│   ├── context-start.md               ← /context-start — carga memoria, abre sesión
│   ├── context-close.md               ← /context-close — guarda memoria, cierra sesión
│   └── context-save.md                ← /context-save — persistencia on-demand
├── inputs/                            ← Documentos fuente (read-only)
├── outputs/                           ← Artefactos generados por el agente
└── scripts/                           ← Scripts de automatización
```

La memoria está dividida por volatilidad:

| Archivo | Se actualiza | Contiene |
|---|---|---|
| `project_state.md` | Raramente | Infraestructura, equipo, hardware, glosario |
| `artifacts_registry.md` | Por artefacto | Todos los archivos con estado y descripción |
| `conversation_memory.md` | Por sesión | Decisiones comprimidas: contexto → opciones → por qué |
| `next_steps.md` | Cada sesión | Completado, urgente, en progreso, en cola |

---

## Cómo Usar

### Requisitos

- [Claude Code](https://claude.ai/code) instalado
- Este repositorio clonado localmente

### Abrir una sesión

Abre este repositorio en Claude Code y ejecuta:

```
/context-start
```

El agente carga todos los archivos de memoria y presenta:
- Fase actual del proyecto y estado de infraestructura
- Las 3–5 decisiones activas más recientes
- Items pendientes por prioridad (🔴 urgente / 🟡 en progreso / ⬜ en cola)
- Una pregunta sobre en qué trabajar hoy

Sin briefing manual. El agente ya sabe todo.

### Cerrar una sesión

```
/context-close
```

El agente:
1. Resume lo que se logró en la sesión
2. Actualiza `next_steps.md`
3. Añade nuevas decisiones a `conversation_memory.md`
4. Actualiza `artifacts_registry.md` por cada archivo nuevo o modificado
5. Confirma que todos los archivos de memoria fueron guardados

### Guardar en medio de una sesión

```
/context-save
```

Úsalo en cualquier momento para persistir una decisión o descubrimiento sin esperar al cierre de sesión.

---

## Infraestructura

| Servicio | Host | Puerto | Estado |
|---|---|---|---|
| llama-server (Ornstein / SuperGemma / TrevorJS / Vision) | `10.1.0.105` | 8012 | ✅ Operativo |
| Open WebUI | `10.1.0.105` | 3000 | ✅ Operativo |
| ComfyUI | `10.1.0.105` | 8188 | ✅ Operativo |
| MCP server | `10.1.0.105` | 8189 | 🔧 Pendiente |

Cambio entre modos con un solo comando en el servidor Debian:

```bash
~/switch-model.sh ornstein    # estructura narrativa y briefs técnicos
~/switch-model.sh supergemma  # ideación horror cruda, lore oscuro
~/switch-model.sh trevorjs    # visual grotesco, prompts gore
~/switch-model.sh vision      # análisis de imágenes (multimodal)
~/switch-model.sh image       # generación de imágenes con ComfyUI
```

> La RTX 3060 tiene 12 GB de VRAM — solo un servicio corre a la vez. El script maneja esto automáticamente.

---

## Pipeline de Producción

```
[Arturo]  →  supergemma-vision analiza imágenes de referencia
                          ↓
         SuperGemma / TrevorJS generan prompts creativos
                          ↓
              Ornstein estructura el prompt y el brief 3D
                          ↓
         [save_prompt MCP] guarda JSON en assets/storyboard/
                          ↓
         [generate_image MCP] → ComfyUI → imagen PNG
                          ↓
              Blender → modelo 3D → motor Three.js
```

El agente ingeniero opera solo desde el paso `generate_image` en adelante. Nunca lee los campos `prompt` ni `negative_prompt` de ningún archivo JSON.

---

## Principios de Diseño

- **La memoria son archivos, no prompts.** Si no está escrito en `context/`, no existe en la próxima sesión.
- **Separar lo estable de lo volátil.** `project_state.md` cambia raramente. `next_steps.md` cambia cada sesión.
- **Comprimir decisiones, no conversaciones.** El log de memoria captura el *por qué*, no lo que se dijo.
- **El registry es el contrato.** Todo archivo producido por el agente debe registrarse antes de cerrar la sesión.
- **Artista e Ingeniero nunca se mezclan.** El contenido creativo y la ejecución técnica son manejados por actores completamente separados.

---

## Patrón Base

Construido sobre el patrón [Context-Engineering](SPEC_context_engineering_agent.md) de [davidkimai/Context-Engineering](https://github.com/davidkimai/Context-Engineering).
Implementado y validado en Claude Code (Anthropic) + Claude Sonnet 4.6.
