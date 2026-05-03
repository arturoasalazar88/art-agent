# Handoff — Modelos Locales, Validaciones y Configuración llama.cpp

Fecha: 2026-05-02
Proyecto: Survival Horror Video Game
Servidor principal: `asalazar@10.1.0.105`
GPU: RTX 3060 12 GB
RAM: 32 GB
Runtime: `llama.cpp server`
Binario: `/home/asalazar/llama.cpp/build/bin/llama-server`
Build validado: `b8998-2098fd616`

Regla crítica: con RTX 3060 solo debe estar activo un modelo pesado o ComfyUI, nunca ambos.

---

## Servicios y puertos

| Servicio | Puerto | Estado/rol |
|---|---:|---|
| `llama-ornstein` | 8012 | Modelo creativo estructurador / JSON técnico |
| `llama-supergemma` | 8012 | Creatividad libre / narrativa |
| `llama-trevorjs` | 8012 | Especificación visual creativa |
| `llama-vision` | 8012 | Actualmente apunta a Qwen2.5-VL, pero UAT falló por latencia |
| `llama-qwen3` | 8013 | Ingeniería/codegen/tool use |
| `comfyui` | 8188 | Generación de imágenes |
| `open-webui` | 3000 | UI web, Docker host network |
| `searxng` | 8080 | Web Search para Open WebUI |

Switcher:

```text
/home/asalazar/switch-model.sh
```

Modos actuales:

```text
ornstein, supergemma, trevorjs, vision, vision-test, qwen3, image
```

---

## Reglas operativas de hardware

- RTX 3060 12 GB es el límite principal.
- ComfyUI y llama-server no deben correr simultáneamente.
- Para Gemma4 Q4_K_M, `ctx=8192` sin KV quant es seguro; mayor contexto requiere KV quant.
- Para Gemma4 Q4_K_M validado:
  - `ctx=24576`
  - `--cache-type-k q4_0 --cache-type-v q4_0`
- Para Qwen3 MoE validado:
  - `ctx=40960`
  - `--cache-type-k q8_0 --cache-type-v q8_0`
  - `--n-cpu-moe 99`
- Para vision/mmproj:
  - `--mmproj-use-cpu` no existe en este build.
  - Usar `--override-tensor ".*=CPU"` para forzar vision encoder/mmproj a RAM.

---

## 1. Ornstein

Modelo:

```text
Ornstein-26B-A4B-it-Q4_K_M.gguf
```

Ruta:

```text
/home/asalazar/models/gemma4/
```

Servicio:

```text
llama-ornstein
```

Rol:

- Estructura narrativa
- Normalización
- JSON técnico
- Handoff contracts
- StoryBibleEntry / InteractiveSceneSpec / AssetSpec3D

Configuración validada:

```bash
--ctx-size 24576
--cache-type-k q4_0
--cache-type-v q4_0
--n-gpu-layers 999
--n-cpu-moe 12
--flash-attn on
--jinja
--chat-template-kwargs '{"enable_thinking":false}'
```

Wrapper:

```text
/home/asalazar/start-ornstein.sh
```

Resultado: PASS production-ready.

Hallazgos:

- Thinking OFF obligatorio para JSON/outputs estructurados.
- Thinking ON causaba prosa/markdown y fallos de formato.
- Validado con tests JSON cualitativos:
  - T1 AssetSpec3D PASS
  - T2 Extracción entidades PASS
  - T3 InteractiveSceneSpec PASS
  - T4 Multi-turn casi PASS; campo determinístico se resuelve con Canonical State Pattern.

Regla: Ornstein no debe tener autoridad final sobre estado determinístico. Inventario, flags,
posiciones y estados canónicos los controla el harness externo.

---

## 2. SuperGemma

Modelo:

```text
supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf
```

Servicio:

```text
llama-supergemma
```

Rol:

- Ideación creativa local
- Narrativa libre
- Escenas / tono / conversación creativa
- No usar para ejecución técnica

Configuración:

```bash
--ctx-size 24576
--cache-type-k q4_0
--cache-type-v q4_0
--n-gpu-layers 999
--n-cpu-moe 12
--flash-attn on
--jinja
```

Inferencia recomendada:

```json
{
  "temperature": 0.85,
  "max_tokens": 4096,
  "chat_template_kwargs": { "enable_thinking": true }
}
```

Resultado: PASS production-ready para tareas creativas.

Hallazgos:

- Thinking ON sí aporta en creatividad.
- `max_tokens=512` falla porque el thinking consume todo el presupuesto.
- Usar mínimo `max_tokens=2048`; recomendado `4096`.

---

## 3. TrevorJS

Modelo:

```text
gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf
```

Servicio:

```text
llama-trevorjs
```

Rol:

- Especificación visual creativa
- Diseño de criaturas/assets desde el lado creativo
- No usar como modelo técnico/codegen

Configuración:

```bash
--ctx-size 24576
--cache-type-k q4_0
--cache-type-v q4_0
--n-gpu-layers 999
--n-cpu-moe 12
--flash-attn on
--jinja
```

Inferencia recomendada:

```json
{
  "temperature": 0.85,
  "max_tokens": 4096,
  "chat_template_kwargs": { "enable_thinking": true }
}
```

Resultado: PASS production-ready para especificaciones visuales creativas.

Hallazgos:

- Validado en STORY_019 con 4 tests cualitativos.
- Mejor evaluarlo por criterios humanos rápidos, no regex scorers.

---

## 4. Qwen3.6-35B-A3B

Modelo:

```text
Qwen3.6-35B-A3B-Q4_K_M.gguf
```

Ruta:

```text
/home/asalazar/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf
```

Servicio:

```text
llama-qwen3
```

Puerto: 8013

Rol:

- Ingeniería
- Codegen
- Debugging
- MCP tool calls
- Orquestación técnica
- VOID_ENGINE

Wrapper:

```text
/home/asalazar/start-qwen3.sh
```

Configuración production:

```bash
--ctx-size 40960
--cache-type-k q8_0
--cache-type-v q8_0
--n-gpu-layers 99
--n-cpu-moe 99
--flash-attn on
--jinja
--port 8013
--metrics
--slots
--slot-save-path /home/asalazar/llama-slots
--threads 6
--threads-batch 6
--threads-http 4
```

Resultado: PASS perfecto, production-ready.

Validación:

- 4 tests x 5 ctx sizes hasta 32k
- T1 JSON PASS
- T2 MCP/tool-like PASS
- T3 codegen PASS
- T4 multi-turn PASS

Perfiles recomendados:

```json
{
  "json_tool_calls": {
    "enable_thinking": false,
    "temperature": 0.1,
    "max_tokens": 2048
  },
  "codegen_debugging": {
    "enable_thinking": true,
    "temperature": 0.3,
    "max_tokens": 5000
  },
  "multi_turn_agentic": {
    "enable_thinking": true,
    "preserve_thinking": true,
    "temperature": 0.2,
    "max_tokens": 2048
  }
}
```

Hallazgos:

- Thinking OFF para extracción/tool calls: rápido y suficiente.
- Thinking ON para codegen largo.
- `ctx=32768` no daba margen para T3 32k; producción usa `ctx=40960`.
- Es el mejor modelo técnico del stack.

---

## 5. Huihui Vision

Modelo:

```text
Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf
```

mmproj:

```text
Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf
```

Ruta:

```text
/home/asalazar/models/huihui/
```

Servicio histórico:

```text
llama-vision
```

Rol:

- Análisis visual provisional
- Imagen de referencia: composición, paleta, mood

Configuración usada:

```bash
--ctx-size 4096
--override-tensor ".*=CPU"
--mmproj /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf
```

Resultado: PASS funcional como solución provisional.

Hallazgos:

- Requiere thinking ON.
- `enable_thinking=false` no es confiable.
- Usar `max_tokens>=2048`.
- Con `max_tokens` bajo puede devolver `content=""` porque consume salida en `reasoning_content`.
- No usar para codegen largo; falló por context exceeded.
- Qwen3 sigue siendo el modelo de ingeniería.

Estado actual:

Fue reemplazado temporalmente por Qwen2.5-VL en `llama-vision.service`, pero Qwen2.5-VL falló
UAT por velocidad. Recomendación: revertir `llama-vision` a Huihui Vision mientras se busca
alternativa.

---

## 6. Huihui Texto sin mmproj

Modelo:

```text
Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf
```

Rol:

- Razonamiento conversacional largo uncensored
- Arquitectura
- Diseño de sistemas
- Análisis multi-turn
- Open WebUI conversational use

Configuración validada:

```bash
--ctx-size 32768
--cache-type-k q8_0
--cache-type-v q8_0
--n-gpu-layers 99
--n-cpu-moe 99
--flash-attn on
--jinja
--port 8012
```

Resultado: PASS production-ready para conversación.

UAT:

- Lógica: PASS
- Arquitectura inventario videojuego: PASS
- Multi-turn / búsqueda binaria: PASS

Restricciones:

- No usar en pipelines automatizados.
- No usar para extracción JSON encadenada.
- No usar para codegen de producción.
- Latencia mayor que Qwen3, pero aceptable para conversación humana.

Recomendación:

Usarlo como modelo conversacional de análisis, no como worker técnico.

---

## 7. Qwen2.5-VL-32B-Instruct-abliterated

Modelo:

```text
Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf
```

Repo:

```text
mradermacher/Qwen2.5-VL-32B-Instruct-abliterated-GGUF
```

Archivos exactos:

```text
Qwen2.5-VL-32B-Instruct-abliterated.Q4_K_M.gguf
Qwen2.5-VL-32B-Instruct-abliterated.mmproj-Q8_0.gguf
```

Rutas locales:

```text
/home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf
/home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf
```

Tamaños:

```text
GGUF: 19G / 19851336736 bytes
mmproj: 701M / 734862560 bytes
```

Arquitectura:

```text
qwen2vl
```

Parámetros:

```text
32.76B denso
```

Servicio actual:

```text
llama-vision.service
```

Wrapper:

```text
/home/asalazar/start-qwen25vl-vision.sh
```

Config actual:

```bash
--model /home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf
--mmproj /home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf
--alias qwen25vl-vision
--host 0.0.0.0
--port 8012
--ctx-size 16384
--n-gpu-layers 64
--override-tensor ".*=CPU"
--flash-attn on
--jinja
--metrics
--slots
--slot-save-path /home/asalazar/llama-slots
--threads 6
--threads-batch 6
--threads-http 4
```

Calibración:

```text
n-gpu-layers=64
VRAM con servicio final: ~6550 MiB used, ~5491 MiB free
```

Validación técnica: PASS.

Evidencia:

```text
general.architecture = qwen2vl
arch = qwen2vl
model loaded
server is listening
```

API tests:

- V1: 609 palabras, PASS funcional
- V2: 569 palabras, PASS funcional

Velocidad:

```text
V1 prompt eval: 1417 tokens at 83.75 tok/s
V1 generation: 789 tokens at 1.46 tok/s
V1 total: ~555.9s
```

UAT UI:

FAIL por latencia.

Conclusión:

- Calidad descriptiva: muy buena.
- Compatibilidad: buena.
- Multimodal: funciona.
- Producción: no viable por velocidad en RTX 3060 12 GB.
- Requisito para siguiente candidato: al menos 2x más rápido, objetivo provisional >=3 tok/s o 50% menos latencia percibida.

Estado importante:

`llama-vision.service` todavía apunta a Qwen2.5-VL. Si se quiere producción usable, revertir a
Huihui Vision.

Backups:

```text
/etc/systemd/system/llama-vision.service.bak-story027
/home/asalazar/switch-model.sh.bak-story027
```

---

## ComfyUI

Servicio:

```text
comfyui
```

Puerto:

```text
8188
```

Ruta:

```text
/home/asalazar/ComfyUI/
```

Checkpoint:

```text
Pony Diffusion V6 XL
```

VAE:

```text
sdxl_vae.safetensors
```

LoRAs:

```text
horror_style: 0.7
gore_details: 0.5
dark_fantasy_arch: 0.4
```

Workflow:

```text
/home/asalazar/ComfyUI/workflows/pony_horror.json
/home/asalazar/ComfyUI/workflows/pony_horror_lora.json
```

Regla:

Nunca correr ComfyUI simultáneo con llama-server en RTX 3060.

---

## Open WebUI

URL:

```text
http://10.1.0.105:3000
```

Docker:

```bash
docker ps
# open-webui ghcr.io/open-webui/open-webui:main
```

Network:

```text
host
```

Env relevante:

```text
OPENAI_API_BASE_URL=http://127.0.0.1:8012/v1
OPENAI_API_KEY=dummy
USE_OLLAMA_DOCKER=false
```

Nota:

Como el contenedor usa `network=host`, `127.0.0.1:8012` apunta al host.

Problema reciente:

Open WebUI mostró 500 por error SQLite:

```text
sqlite3.OperationalError: unable to open database file
```

Acción tomada:

- Backup DB creado:
  `/home/asalazar/openwebui-db-backup-20260502_004248`
- `PRAGMA integrity_check`: ok
- Reinicio de contenedor corrigió HTTP 500.
- Health tras reinicio: `{"status":true}`

---

## Recomendaciones próximas

1. Revertir `llama-vision.service` a Huihui Vision para producción usable.
2. Mantener Qwen2.5-VL documentado como alta calidad pero inviable por velocidad.
3. Crear nueva búsqueda de modelo de visión con objetivo:
   - multimodal real
   - abliterated/uncensored preferible
   - >=3 tok/s en RTX 3060 12 GB
   - idealmente menor que 32B denso o arquitectura más eficiente
4. Mantener Qwen3.6 como único modelo técnico/codegen.
5. Mantener Huihui Texto para conversación larga y arquitectura no automatizada.
6. No usar modelos vision para codegen.

---

## Comandos útiles

Estado de servicios:

```bash
~/switch-model.sh
systemctl is-active llama-vision llama-qwen3 comfyui
pgrep -af llama-server
nvidia-smi
```

Arrancar Qwen3 ingeniería:

```bash
~/switch-model.sh qwen3
```

Arrancar visión:

```bash
~/switch-model.sh vision
```

Arrancar ComfyUI:

```bash
~/switch-model.sh image
```

Ver modelo activo en 8012:

```bash
curl -s http://localhost:8012/v1/models
curl -s http://localhost:8012/health
```

Logs:

```bash
journalctl -u llama-vision -n 100 --no-pager
journalctl -u llama-qwen3 -n 100 --no-pager
docker logs --tail 100 open-webui
```

Revertir llama-vision a backup pre-STORY_027:

```bash
sudo cp /etc/systemd/system/llama-vision.service.bak-story027 /etc/systemd/system/llama-vision.service
sudo systemctl daemon-reload
sudo systemctl restart llama-vision
curl -s http://localhost:8012/v1/models
```

