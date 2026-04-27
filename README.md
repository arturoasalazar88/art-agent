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
│   ├── conversation_memory.md         ← Log comprimido de decisiones (D01–D28+)
│   ├── next_steps.md                  ← Estado actual y próximas acciones (volátil)
│   ├── session_log.md                 ← Una línea por sesión — audit trail
│   └── working_memory.md              ← Checkpoint a corto plazo (volátil, se crea con /context-checkpoint)
├── .claude/commands/
│   ├── context-start.md               ← /context-start — carga memoria, abre sesión
│   ├── context-close.md               ← /context-close — guarda memoria, cierra sesión
│   ├── context-save.md                ← /context-save — persistencia on-demand
│   └── context-checkpoint.md          ← /context-checkpoint — snapshot de corto plazo
├── inputs/                            ← Documentos fuente (read-only)
├── outputs/                           ← Artefactos generados por el agente
└── scripts/                           ← Scripts de automatización
```

---

## Sistema de Memoria

La memoria está separada en dos capas: **permanente** y **corto plazo**.

### Memoria Permanente

Cinco archivos que juntos forman el estado completo del proyecto:

| Archivo | Volatilidad | Contiene |
|---|---|---|
| `project_state.md` | Raramente cambia | Infraestructura, hardware, modelos, servicios, glosario, riesgos, upgrade pendiente |
| `artifacts_registry.md` | Por artefacto | Todos los archivos con estado (✅ Activo / 🔒 Histórico / 🔧 En progreso) |
| `conversation_memory.md` | Por sesión | Decisiones comprimidas: contexto → opciones → decisión → por qué |
| `next_steps.md` | Cada sesión | Completado, urgente (🔴), en progreso (🟡), en cola (⬜) |
| `session_log.md` | Cada sesión | Una línea por sesión — fecha, trabajo, artefactos, decisiones |

### Memoria a Corto Plazo

Un archivo volátil creado bajo demanda:

| Archivo | Cuándo existe | Contiene |
|---|---|---|
| `working_memory.md` | Solo si la sesión fue interrumpida o se hizo checkpoint | Tarea activa, hilo de conversación reciente, decisiones no formalizadas, trabajo en vuelo, próximo paso exacto |

**Ciclo de vida de working_memory.md:**
1. Se crea o sobreescribe con `/context-checkpoint`
2. Se carga automáticamente en `/context-start` si existe
3. Se elimina al hacer `/context-close` exitoso

---

## Skills — Comandos de Sesión

### `/context-start` — Apertura de sesión

Carga los 5 archivos de memoria en orden. Presenta al usuario:
- Estado del proyecto y fase actual
- ⚡ Checkpoint activo (si existe `working_memory.md`) con pregunta de retomar
- Decisiones activas recientes
- Pendientes por prioridad (🔴 urgente / 🟡 en progreso / ⬜ en cola)
- Último artefacto registrado
- Pregunta sobre qué trabajar hoy

```
/context-start
```

---

### `/context-close` — Cierre de sesión

Ejecuta en orden:
1. Resume lo logrado en la sesión
2. Actualiza `next_steps.md` — marca completados, agrega pendientes
3. Añade nuevas decisiones a `conversation_memory.md`
4. Actualiza `artifacts_registry.md` por archivos nuevos o modificados
5. Actualiza `project_state.md` si hubo cambios de infraestructura
6. Limpia `working_memory.md` — el cierre exitoso invalida el checkpoint
7. Confirma con resumen de cierre

```
/context-close
```

**Este skill no es opcional.** Cada sesión debe terminar con `/context-close`. Si el usuario olvida, el agente lo recuerda.

---

### `/context-save` — Guardado on-demand

Persiste una decisión, artefacto o cambio de infraestructura a los archivos permanentes en cualquier momento de la sesión, sin esperar al cierre.

Úsalo cuando:
- Se toma una decisión importante que no quieres perder si la sesión se interrumpe
- Se instala o configura algo nuevo en el servidor
- Se descubre una restricción técnica o gotcha
- El usuario pide explícitamente guardar algo

```
/context-save
```

---

### `/context-checkpoint` — Snapshot de corto plazo

Crea o sobreescribe `context/working_memory.md` con un snapshot completo del hilo vivo: qué se está haciendo, conversación reciente, decisiones no formalizadas, trabajo en vuelo, y el próximo paso exacto.

**Cuándo usarlo:**
- Cada ~30 mensajes como higiene preventiva
- Antes de operaciones largas (descargas, compilaciones, esperar procesos del servidor)
- Cuando el contexto se está volviendo denso
- Antes de una operación con riesgo de ruptura de sesión

```
/context-checkpoint
```

**Recuperación tras compactación o ruptura:**
1. `/context-start` detecta automáticamente el checkpoint y lo anuncia ⚡
2. El agente pregunta si retomar desde el checkpoint o empezar tarea nueva
3. Si se retoma, las decisiones pendientes del checkpoint se formalizan con `/context-save`
4. Al terminar, `/context-close` limpia el checkpoint

---

## Flujo de Sesión Típica

```
Abrir Claude Code en el repo art-agent
          ↓
/context-start
  → carga 5 archivos de memoria
  → detecta checkpoint si existe
  → presenta resumen + pregunta qué trabajar
          ↓
Trabajo de la sesión
  → /context-checkpoint cada ~30 mensajes (preventivo)
  → /context-save cuando se toma una decisión importante
          ↓
/context-close
  → actualiza todos los archivos de memoria
  → limpia working_memory.md
  → confirma cierre
```

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

Sin briefing manual. El agente ya sabe todo.

### Cerrar una sesión

```
/context-close
```

### Guardar progreso durante la sesión

```
/context-save          ← para decisiones individuales
/context-checkpoint    ← para snapshot completo del hilo
```

---

## Infraestructura

| Servicio | Host | Puerto | Estado |
|---|---|---|---|
| llama-server (Ornstein / SuperGemma / TrevorJS / Vision) | `10.1.0.105` | 8012 | ✅ Operativo |
| Open WebUI | `10.1.0.105` | 3000 | ✅ Operativo |
| ComfyUI | `10.1.0.105` | 8188 | ✅ Operativo |
| MCP server | `10.1.0.105` | 8189 | 🔧 Pendiente implementación |

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

## Reglas del Agente Ingeniero

1. **Idioma:** Siempre en español
2. **Separación Artista/Ingeniero:** Nunca genera contenido creativo
3. **Prompts son opacos:** Nunca lee `prompt` ni `negative_prompt` de archivos JSON
4. **Registry antes de crear:** Verifica `artifacts_registry.md` antes de generar archivos
5. **Restricciones de hardware:** RTX 3060 12GB — ctx-size máximo 8192 con Q4_K_M
6. **Cierre obligatorio:** Cada sesión termina con `/context-close`
7. **inputs/ es read-only:** Nunca modificar documentos fuente
8. **MCP specs son la fuente de verdad:** `inputs/mcp-specs-survival-horror.md`
9. **Registrar todo:** Cada archivo nuevo va a `artifacts_registry.md`
10. **Decisiones a memoria:** Formato: contexto → opciones → decisión → por qué
11. **Checkpoint proactivo:** `/context-checkpoint` cada ~30 mensajes
12. **Recuperación de sesión rota:** Cargar `working_memory.md` si existe al retomar

---

## Principios de Diseño

- **La memoria son archivos, no prompts.** Si no está escrito en `context/`, no existe en la próxima sesión.
- **Separar lo estable de lo volátil.** `project_state.md` cambia raramente. `next_steps.md` cambia cada sesión. `working_memory.md` es desechable.
- **Comprimir decisiones, no conversaciones.** El log de memoria captura el *por qué*, no lo que se dijo.
- **El registry es el contrato.** Todo archivo producido debe registrarse antes de cerrar la sesión.
- **Artista e Ingeniero nunca se mezclan.** El contenido creativo y la ejecución técnica son manejados por actores completamente separados.
- **El checkpoint es seguro de red.** `working_memory.md` permite recuperar cualquier sesión interrumpida sin perder el hilo.

---

## Patrón Base

Construido sobre el patrón [Context-Engineering](SPEC_context_engineering_agent.md) de [davidkimai/Context-Engineering](https://github.com/davidkimai/Context-Engineering).
Implementado y validado en Claude Code (Anthropic) + Claude Sonnet 4.6.
