# Session Handoff — LLM Local Pipeline para Survival Horror

## Propósito del documento

Este documento sirve como handoff de sesión para evitar pérdida de contexto durante compactación o reinicio de conversación. Resume el objetivo real del proyecto, el timeline completo de decisiones, los hallazgos ya validados, el estado actual del despliegue con llama.cpp server y los siguientes pasos recomendados.

---

## Objetivo real del proyecto

El objetivo **no** es encontrar un único modelo ganador para todo. El objetivo es montar un stack local de modelos **Gemma 4 26B A4B** en Debian para un pipeline de survival horror enfocado en:

- Escritura de guiones y escenas crudas
- Generación de prompts visuales para imagen
- Briefs técnicos para modelos 3D en Blender + Three.js
- Integración futura en un workflow multi-modelo por tarea

> **Nota de diseño:** "uncensored" no significa automáticamente "mejor escritor". Para producción de videojuego, la estrategia validada es usar un modelo creativo para ideación y otro más disciplinado para reescritura final y entrega técnica.

---

## Hardware y contexto operativo

### Host principal de inferencia

| Componente | Detalle |
|---|---|
| SO | Debian |
| GPU | KO Nvidia GeForce RTX 3060 V2 OC Edition, 12 GB GDDR6 |
| CPU | Intel Core i5-9600K, 3.7 GHz, 6 núcleos, LGA1151, 9 MB cache |
| RAM | 32 GB |
| Acceso | SSH (`asalazar@10.1.0.105`) |
| Runtime | llama.cpp server |

### ⚠️ Restricción crítica

La RTX 3060 12 GB corre estos modelos en **modo híbrido GPU + RAM obligatorio**. El archivo Q4_K_M ronda los 16 GB, superando la VRAM disponible. Cambios de preset o contexto pueden provocar SEGV si la KV cache no cabe.

### Límites de contexto validados

| ctx-size | Resultado |
|---|---|
| 2048 | ✅ Estable — punto de partida original |
| 8192 | ✅ Estable — valor actual en producción |
| 16384 | ❌ SEGV — KV cache no cabe en VRAM |

### Cuantizaciones evaluadas

| Cuantización | Calidad | Encaje en 3060 12 GB |
|---|---|---|
| Q4_K_M | Alta | ⚠️ Viable en híbrido, ajustado |
| IQ4_XS | Media-alta | ✅ Más estable, algo menos calidad |
| Q3_K_M | Media | ✅ Permitiría ctx-size 12288+ |

### Referencia de tokens en 8192

| Contenido | Tokens aprox. |
|---|---|
| 1 página de texto normal | ~500 |
| Escena de guion detallada | ~800–1200 |
| Brief técnico 3D completo | ~600–900 |
| Conversación larga de chat | ~2000–3000 |
| Guion de nivel completo | ~4000–6000 |

---

## Modelos objetivo

### 1. SuperGemma

**Archivo:** `~/models/gemma4/supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf`

**Servicio systemd:** `llama-supergemma`

**Rol:** Ideación libre, escenas crudas, diálogo oscuro, lore sucio, criaturas y ambientes inquietantes.

**Conclusión de benchmark:** Mejor candidato para creatividad horror sin filtro. No el más confiable para formato técnico estricto.

---

### 2. Ornstein

**Archivo:** `~/models/gemma4/Ornstein-26B-A4B-it-Q4_K_M.gguf`

**Servicio systemd:** `llama-ornstein`

**Rol:** Estructura narrativa, prompts limpios, briefs técnicos, fichas 3D para Blender + Three.js.

**Conclusión de benchmark:** Mejor modelo para estructura, prompts utilizables y documentación técnica.

---

### 3. TrevorJS / uncensored Gemma 4

**Archivo:** `~/models/gemma4/gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf`

**Servicio systemd:** `llama-trevorjs`

**Rol:** Variantes grotescas, prompts visuales extremos, horror corporal, alternativas uncensored.

**Conclusión de benchmark:** Fuerte como segunda opción creativa horror, especialmente visual. No superó a Ornstein en estructura.

---

## Arquitectura del stack

Un solo puerto fijo `8012`. Un modelo activo a la vez. Open WebUI nunca cambia de configuración.

```
Mac (Open WebUI :3000) → llama-server :8012 → modelo activo
```

Cambio de modelo:
```bash
~/switch-model.sh ornstein     # estructura y briefs
~/switch-model.sh supergemma   # creatividad y horror crudo
~/switch-model.sh trevorjs     # grotesco visual uncensored
```

Sin argumentos muestra cuál está activo:
```bash
~/switch-model.sh
```

---

## Servicios systemd

### Archivos

| Servicio | Archivo |
|---|---|
| `llama-ornstein` | `/etc/systemd/system/llama-ornstein.service` |
| `llama-supergemma` | `/etc/systemd/system/llama-supergemma.service` |
| `llama-trevorjs` | `/etc/systemd/system/llama-trevorjs.service` |

### Comandos de operación

```bash
# Ver estado de los tres
sudo systemctl status llama-ornstein llama-supergemma llama-trevorjs

# Cambiar modelo manualmente
sudo systemctl stop llama-supergemma
sudo systemctl start llama-ornstein

# Ver logs en tiempo real
sudo journalctl -u llama-ornstein -f
```

### Preset base compartido (todos los servicios)

```
--ctx-size 8192
--n-gpu-layers 999
--n-cpu-moe 12
--flash-attn on
--jinja
--metrics
--slots
--slot-save-path /home/asalazar/llama-slots
--threads 6
--threads-batch 6
--threads-http 4
```

**Thinking:** Activado en los tres. Ninguno lleva `--chat-template-kwargs '{"enable_thinking":false}'`. Open WebUI maneja `reasoning_content` correctamente.

---

## Open WebUI

| Parámetro | Valor |
|---|---|
| URL desde Mac | `http://10.1.0.105:3000` |
| Contenedor Docker | `open-webui` |
| API apuntada | `http://127.0.0.1:8012/v1` |
| Restart policy | `always` |

```bash
# Ver estado del contenedor
docker ps | grep open-webui

# Reiniciar si hace falta
docker restart open-webui

# Ver logs
docker logs open-webui --tail 50
```

---

## Script switch-model.sh

**Ubicación:** `~/switch-model.sh`

Detecta qué modelo está activo, detiene el que corre, arranca el solicitado y espera confirmación del `/health` antes de reportar éxito.

**Validado:** Cambio Ornstein → SuperGemma funcionando correctamente.

---

## Hallazgos clave del benchmark

El preset base estable para los tres modelos:

```bash
--n-cpu-moe 12 --n-gpu-layers 999 --ctx-size 8192
```

Bajar `--n-cpu-moe` a 10 provocó fallos de memoria. 12 es el mínimo seguro para Q4_K_M en esta RTX 3060 12 GB.

| Tarea | Modelo |
|---|---|
| Ideación horror cruda | SuperGemma |
| Estructura narrativa | Ornstein |
| Prompts de imagen | Ornstein |
| Variantes grotescas | TrevorJS |
| Briefs 3D | Ornstein |

---

## Riesgos identificados

### 1. VRAM al límite
Cambios de ctx-size, cuantización o flags pueden provocar SEGV. Validar siempre con `systemctl status` después de cualquier cambio.

### 2. Puerto único compartido
Solo un modelo puede estar activo en `8012` a la vez. Si dos servicios arrancan simultáneamente, el segundo fallará. El script `switch-model.sh` maneja esto.

### 3. Restart automático en SEGV
Los servicios tienen `Restart=on-failure`. Un SEGV por contexto muy alto puede causar un loop de reinicios. Monitorear con `journalctl -u llama-X -f` si algo se comporta raro.

---

## Qué no debe olvidarse en futuras sesiones

- El runtime es **llama.cpp server** — decisión definitiva.
- Puerto fijo: **8012** — Open WebUI nunca cambia.
- Preset base validado: `--n-cpu-moe 12 --n-gpu-layers 999 --ctx-size 8192`.
- Thinking **activado** en los tres modelos.
- ctx-size 16384 provoca SEGV — no subir de 8192 sin bajar a Q3_K_M primero.
- Ornstein **no reemplaza** a SuperGemma ni TrevorJS — cada uno tiene su rol.

---

## Próximos pasos recomendados

1. Añadir `--api-key` a los tres servicios y configurar autenticación en Open WebUI.
2. Probar SuperGemma y TrevorJS con prompts reales del juego para validar calidad.
3. Evaluar Q3_K_M si se necesita ctx-size mayor a 8192.
4. Definir system prompts por modelo adaptados al workflow de survival horror.
5. Integración con pipeline de generación de imágenes.

---

## 🧠 Resumen operativo mínimo

| Clave | Valor |
|---|---|
| Proyecto | Pipeline local de survival horror con Three.js y Blender |
| Host | `asalazar@10.1.0.105` — Debian + RTX 3060 12 GB + 32 GB RAM |
| Runtime | llama.cpp server — puerto 8012 |
| UI | Open WebUI — `http://10.1.0.105:3000` |
| Preset base | `--n-cpu-moe 12 --n-gpu-layers 999 --ctx-size 8192` |
| Switch de modelo | `~/switch-model.sh [ornstein|supergemma|trevorjs]` |
| Thinking | Activado en los tres |
| ctx-size límite | 8192 ✅ — 16384 ❌ SEGV |
| SuperGemma | Crudeza creativa |
| TrevorJS | Grotesco visual uncensored |
| Ornstein | Estructura y entrega técnica |

---

## ComfyUI — Generación de Imágenes

### Instalación

| Parámetro | Valor |
|---|---|
| Ruta | `~/ComfyUI` |
| Entorno virtual | `~/ComfyUI/venv` |
| Puerto | `8188` |
| URL desde Mac | `http://10.1.0.105:8188` |
| PyTorch | CUDA 12.1 — RTX 3060 validada |

### Modelos descargados

| Modelo | Ruta | Tamaño |
|---|---|---|
| Pony Diffusion V6 XL | `~/ComfyUI/models/checkpoints/ponyDiffusionV6XL.safetensors` | 6.46 GB |

### Workflow base

**Archivo:** `~/ComfyUI/workflows/pony_horror.json`

Prompt positivo base:
```
score_9, score_8_up, dark horror, abandoned hospital corridor, gore, decay, visceral, cinematic lighting, highly detailed
```

Prompt negativo base:
```
score_4, score_3, score_2, score_1, bright colors, clean, cartoon, blurry
```

Parámetros: 1024x1024, 25 steps, CFG 7, sampler euler, scheduler normal.

### Estado validado

- ✅ ComfyUI arranca y es accesible desde Mac
- ✅ Pony Diffusion V6 XL cargado y detectado
- ✅ Primera imagen generada — corredor de hospital con gore, 1024x1024
- ✅ Workflow `pony_horror.json` funcional

### Modo de operación

ComfyUI y llama-server **no corren simultáneamente**. La RTX 3060 no tiene VRAM suficiente para ambos.

**Cambiar a modo imagen:**
```bash
sudo systemctl stop llama-ornstein llama-supergemma llama-trevorjs
cd ~/ComfyUI && source venv/bin/activate && python3 main.py --listen 0.0.0.0 --port 8188
```

**Cambiar a modo LLM:**
- Detener ComfyUI con `Ctrl+C`
- Luego: `~/switch-model.sh ornstein` (o el modelo deseado)

### Arrancar ComfyUI

```bash
cd ~/ComfyUI && source venv/bin/activate && python3 main.py --listen 0.0.0.0 --port 8188
```

### Próximos modelos recomendados para horror

| Modelo | Peso | Uso |
|---|---|---|
| FLUX.1-dev GGUF Q4 | ~8 GB | Concept art de alta calidad |
| IllustriousXL | ~7 GB | Personajes y criaturas |
| VAE sdxl_vae.safetensors | ~320 MB | Mejor calidad de color en SDXL |

---

## Actualizaciones post-sesión 2

### ComfyUI — systemd

Servicio creado en `/etc/systemd/system/comfyui.service` pero **no habilitado para arranque automático** — se gestiona manualmente via `switch-model.sh` para evitar conflicto de VRAM con llama-server.

### VAE descargado

| Archivo | Ruta | Tamaño |
|---|---|---|
| sdxl_vae.safetensors | `~/ComfyUI/models/vae/sdxl_vae.safetensors` | 319 MB |

Mejora notable en colores, sombras y detalle vs VAE integrado del checkpoint.

### LoRAs descargados

| Archivo | Ruta | Strength recomendado |
|---|---|---|
| horror_style.safetensors | `~/ComfyUI/models/loras/horror_style.safetensors` | 0.7 |
| gore_details.safetensors | `~/ComfyUI/models/loras/gore_details.safetensors` | 0.5 |
| dark_fantasy_arch.safetensors | `~/ComfyUI/models/loras/dark_fantasy_arch.safetensors` | 0.4 |

### Workflows disponibles

| Archivo | Descripción |
|---|---|
| `pony_horror.json` | Base — Pony + VAE externo, sin LoRAs |
| `pony_horror_lora.json` | Completo — Pony + VAE + 3 LoRAs encadenados |

### Script switch-model.sh actualizado

Ahora maneja 4 modos:

```bash
~/switch-model.sh ornstein    # LLM estructura
~/switch-model.sh supergemma  # LLM creatividad
~/switch-model.sh trevorjs    # LLM grotesco
~/switch-model.sh image       # ComfyUI — apaga LLMs, arranca ComfyUI
~/switch-model.sh             # muestra estado actual de todos
```

### Resumen del stack completo validado

| Componente | URL | Comando |
|---|---|---|
| Open WebUI | `http://10.1.0.105:3000` | `~/switch-model.sh ornstein` |
| ComfyUI | `http://10.1.0.105:8188` | `~/switch-model.sh image` |
| llama-server | `http://10.1.0.105:8012` | activo con cualquier modelo LLM |

---

## Rol de Claude en el proyecto

Claude es el asistente principal de desarrollo en este proyecto con las siguientes capacidades y limitaciones explícitas.

### Lo que Claude puede hacer

- Arquitectura y código del videojuego en Three.js
- Sistemas de gameplay: inventario, enemigos, triggers, eventos, lógica narrativa
- Pipeline de importación de assets desde Blender
- Shaders y efectos visuales de horror
- Integración de audio y atmósfera
- Sistemas de decisiones y narrativa ramificada
- Prompts técnicos para los modelos locales (Ornstein, SuperGemma, TrevorJS)
- Soporte con Claude Code para trabajar directo en el repositorio
- Mantenimiento y actualización del handoff de sesión

### Limitaciones explícitas

Claude no genera contenido gore, violento o sexualmente explícito directamente. Para ese tipo de contenido el pipeline usa los modelos locales uncensored (SuperGemma y TrevorJS para texto, Pony Diffusion para imagen). Claude ayuda a estructurar los prompts y el workflow pero la generación la hacen los modelos locales.

### Continuidad entre sesiones

El handoff de sesión es el mecanismo de continuidad. Al inicio de cada sesión nueva subir este documento como contexto. Claude retoma desde el estado exacto donde se dejó sin necesidad de reexplicar el proyecto.

---

## Pipeline Artista / Ingeniero

### Concepto central

Separación total entre creatividad y ejecución técnica. El artista y el ingeniero nunca se mezclan.

- **El Artista** — Tú + Open WebUI + llama-server (SuperGemma / TrevorJS / Ornstein). Genera y guarda prompts. Nunca toca código ni herramientas técnicas.
- **El Ingeniero** — Tú + OpenCode / Claude Code / Gemini CLI. Lee prompts del disco y ejecuta la generación. Nunca genera ni modifica contenido creativo.

### El flujo completo

```
EL ARTISTA
Tú + Open WebUI + llama-server
        ↓
Modelo produce prompt visual completo (sin censura)
        ↓
"guarda este prompt como assets/storyboard/frame3"
        ↓
MCP save_prompt → archivo en disco
        ↓
assets/storyboard/frame3.json
        ↓
EL INGENIERO
Tú + OpenCode / Claude Code / Gemini CLI
        ↓
"genera la imagen del storyboard frame 3"
        ↓
Agente lee frame3.json (nunca genera ni modifica el prompt)
        ↓
MCP generate_image → ComfyUI → imagen generada
        ↓
assets/storyboard/frame3.png
```

### Estructura de carpetas del proyecto

```
assets/
├── storyboard/
│   ├── frame1.json      ← prompt guardado por el artista
│   ├── frame1.png       ← imagen generada por el ingeniero
│   ├── frame2.json
│   └── frame2.png
├── characters/
│   ├── antagonist.json
│   └── antagonist.png
├── environments/
│   ├── hospital_corridor.json
│   └── hospital_corridor.png
└── workflows/
    ├── storyboard_base.json    ← workflow ComfyUI base
    ├── character_sheet.json
    └── environment.json
```

### Las dos herramientas MCP

**save_prompt** — la usa el artista via Open WebUI
```
save_prompt(path, prompt, metadata)
→ guarda el prompt en disco en la ruta indicada
→ retorna confirmación
```

**generate_image** — la usa el ingeniero via OpenCode / Claude Code
```
generate_image(prompt_path, workflow_name)
→ lee el archivo JSON del disco
→ inyecta el prompt en el workflow base
→ envía a ComfyUI
→ espera resultado
→ guarda imagen en misma ruta con extensión .png
→ retorna ruta de imagen o error técnico
```

### Reglas de la separación

- El ingeniero nunca llama `save_prompt`
- El artista nunca llama `generate_image` directamente — el modelo local lo hace por él
- El ingeniero nunca lee ni modifica el contenido de los prompts
- El artista nunca toca workflows, parámetros técnicos ni configuración de ComfyUI

### Lo que el ingeniero puede hacer sin violar la separación

- Verificar que el archivo de prompt existe antes de ejecutar
- Validar que el workflow base está disponible
- Reintentar si ComfyUI falla
- Organizar y renombrar outputs
- Generar múltiples frames en batch
- Reportar errores técnicos sin tocar el contenido

### Próximo paso técnico pendiente

Implementar el MCP server en Python con FastMCP corriendo en el servidor Debian. Agnóstico — compatible con Claude Code, Gemini CLI, OpenCode, Open WebUI y cualquier cliente MCP estándar. Las dos herramientas iniciales: `save_prompt` y `generate_image`.

---

## Modelo Multimodal — SuperGemma Vision

### Archivos

| Archivo | Ruta | Tamaño |
|---|---|---|
| Modelo principal | `~/models/multimodal/supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf` | ~15.6 GB |
| Vision encoder | `~/models/multimodal/mmproj-supergemma4-26b-abliterated-multimodal-f16.gguf` | ~1.1 GB |

### Restricción crítica de VRAM

El mmproj requiere ~1,145 MB adicionales. Después de cargar el modelo principal solo quedan ~27 MB libres en VRAM. Solución validada: forzar el mmproj a RAM con `--override-tensor ".*=CPU"` y bajar ctx-size a 4096.

### Comando validado

```bash
~/llama.cpp/build/bin/llama-server \
  --model ~/models/multimodal/supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf \
  --mmproj ~/models/multimodal/mmproj-supergemma4-26b-abliterated-multimodal-f16.gguf \
  --alias supergemma-vision \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 4096 \
  --n-gpu-layers 999 \
  --n-cpu-moe 12 \
  --override-tensor ".*=CPU" \
  --jinja \
  --metrics \
  --slots \
  --slot-save-path ~/llama-slots \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4 \
  --flash-attn on
```

**Nota:** `--mmproj-use-cpu` no existe en este build. Usar `--override-tensor ".*=CPU"` como alternativa.

### Estado

- ✅ Arranca correctamente con mmproj en RAM
- ✅ Responde por `/health`
- ✅ Visión validada en Open WebUI — análisis de composición, paleta, mood y elementos visuales
- ✅ Thinking integrado en respuesta (no como bloque separado en modo multimodal)
- ✅ Listo para análisis de imágenes de referencia en pipeline de estética

### Integración con switch-model.sh

Pendiente — agregar `vision` como quinta opción al script después de validar funcionamiento completo.

---

## Actualizaciones post-sesión 3

### Switch-model.sh — 5 modos validados

```bash
~/switch-model.sh ornstein    # LLM estructura y briefs
~/switch-model.sh supergemma  # LLM creatividad horror crudo
~/switch-model.sh trevorjs    # LLM grotesco visual uncensored
~/switch-model.sh vision      # Multimodal análisis de imágenes
~/switch-model.sh image       # ComfyUI generación de imágenes
~/switch-model.sh             # muestra estado actual de todos
```

### Servicio llama-vision

Registrado en systemd como `llama-vision.service`. Habilitado para arranque bajo demanda via switch-model.sh. No arranca automáticamente en boot.

### Estado final del catálogo de modelos

| Alias | Modelo | Puerto | Rol |
|---|---|---|---|
| ornstein-prod | Ornstein-26B-A4B-it-Q4_K_M | 8012 | Estructura y briefs técnicos |
| supergemma-raw | supergemma4-26b-uncensored-fast-v2-Q4_K_M | 8012 | Creatividad horror sin filtro |
| trevorjs-grotesque | gemma-4-26B-A4B-it-uncensored-Q4_K_M | 8012 | Grotesco visual uncensored |
| supergemma-vision | supergemma4-26b-abliterated-multimodal-Q4_K_M | 8012 | Análisis de imágenes |
| ComfyUI | Pony Diffusion V6 XL + LoRAs | 8188 | Generación de imágenes |

### Resumen operativo mínimo actualizado

| Clave | Valor |
|---|---|
| Proyecto | Pipeline local de survival horror con Three.js y Blender |
| Host | `asalazar@10.1.0.105` — Debian + RTX 3060 12GB + 32GB RAM |
| Runtime LLM | llama.cpp server — puerto 8012 |
| Runtime imagen | ComfyUI — puerto 8188 |
| UI chat | Open WebUI — `http://10.1.0.105:3000` |
| Switch de modo | `~/switch-model.sh [ornstein\|supergemma\|trevorjs\|vision\|image]` |
| Preset base LLM | `--n-cpu-moe 12 --n-gpu-layers 999 --ctx-size 8192` |
| Preset vision | `--ctx-size 4096 --override-tensor ".*=CPU"` |
| ctx-size límite | Q4_K_M: 8192 ✅ — 16384 ❌ SEGV |

### Próximos pasos pendientes

1. Descargar Q3_K_M de SuperGemma para doblar ventana de contexto a ~16384
2. Implementar MCP server (specs en `mcp-specs-survival-horror.md`)
3. Crear estructura de carpetas del proyecto `horror-game/assets/`
4. Definir estética base con imágenes de referencia via supergemma-vision
5. Montar workflow de storyboard con style lock en ComfyUI

---

## Decision Log — Modelo de Visión Uncensored

### Contexto
Se evaluó si era necesario un modelo de visión uncensored específico para el pipeline de generación de assets gore y storyboard.

### Modelos evaluados

| Modelo | Veredicto | Razón |
|---|---|---|
| Gemma 3 12B abliterated GGUF (bartowski) | ❌ Descartado | mmproj no funciona correctamente con llama.cpp + Open WebUI — reportes de comunidad confirman que el modelo no procesa imágenes realmente |
| Gemma 4 26B Uncensored MAX Q8_0 | ❌ Descartado | 26.9 GB — no cabe en hardware disponible |
| Gemma 4 E4B HauhauCS Aggressive | ⏳ Evaluado pero no necesario | Ver decisión final |

### Decisión final

**No se necesita un modelo de visión uncensored.** La censura solo importa en la etapa de generación del prompt, no en el análisis visual.

El flujo correcto es:

```
supergemma-vision analiza imagen de referencia gore/horror
        ↓
produce descripción técnica estructurada
(composición, paleta, mood, elementos visuales)
        ↓
SuperGemma / TrevorJS recibe esa descripción
y genera el prompt gore completo sin censura
        ↓
ComfyUI ejecuta la generación del asset
```

supergemma-vision describe lo que ve sin necesitar ser uncensored porque su output es una descripción técnica, no contenido explícito. El contenido explícito lo genera SuperGemma/TrevorJS en el paso siguiente.

### Catálogo de visión final

| Modelo | Rol | Estado |
|---|---|---|
| supergemma-vision | Análisis de imágenes de referencia, extracción de estética, paleta y composición | ✅ Activo y validado |

No se añadirán más modelos de visión hasta que el pipeline completo Artista/Ingeniero esté implementado y se identifique un gap real.
