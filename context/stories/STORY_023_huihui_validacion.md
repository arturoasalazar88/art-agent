# STORY_023 — Validación Huihui-Qwen3.5-35B-A3B: Ingeniería + Visión (dos en uno)

> Estado: ✅ Completada
> Área: Infraestructura / Modelos
> Desarrollada por: modelo de ingeniería (Codex u otro agente externo)
> Sesión de creación: 17 (2026-05-01)
> Sesión de cierre: 17 (2026-05-01)
> Depende de: STORY_021 ✅, STORY_022 ✅

---

## Objetivo

Validar si `Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M` puede:

1. **Reemplazar** el actual `Qwen3.6-35B-A3B-Q4_K_M` como modelo de ingeniería (puerto 8013)
2. **Cubrir el rol de visión** usando su mmproj (cerrando el bloqueo de STORY_022 Tarea 4)

Si ambas validaciones pasan, este modelo se convierte en el único activo en el stack de ingeniería+visión, simplificando la infraestructura.

---

## Resultado de ejecución — 2026-05-01

**Decisión final:** Huihui-Qwen3.5-35B-A3B **NO reemplaza** a Qwen3.6 como modelo de ingeniería. Sí queda **adoptado como modelo de visión** mediante `llama-vision.service`, cerrando el bloqueo de STORY_022 para el rol multimodal.

### Tarea 0 — Descarga e integridad

| Archivo | Resultado |
|---|---|
| GGUF principal | ✅ Descargado: `20G` |
| mmproj | ✅ Descargado: `858M` |
| Espacio final | ✅ `/home/asalazar`: `43G` libres tras descarga |

Rutas:
- `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf`
- `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf`

### Tarea 1 — Compatibilidad de arquitectura

✅ PASS. El build actual `llama.cpp b8998-2098fd616` reconoce `general.architecture = qwen35moe`, carga el modelo y arranca server en `8013`.

Evidencia del log:
- `main: model loaded`
- `main: server is listening on http://127.0.0.1:8013`
- `sched_reserve: fused Gated Delta Net (chunked) enabled`

### Tarea 2 — Suite de ingeniería

| Test | ctx | PASS/FAIL | Tiempo | Notas |
|---|---:|---|---:|---|
| T1 JSON | 4k | ✅ PASS | 19.137s | 5/5 correcto, pero falla criterio de velocidad ≤10s |
| T1 JSON | 8k | ✅ PASS | 41.405s | 5/5 correcto |
| T1 JSON | 32k | ✅ PASS | 133.600s | 5/5 correcto |
| T2 MCP | 8k | ✅ PASS | 39.200s | 5/5 correcto |
| T2 MCP | 32k | ✅ PASS | 128.430s | 5/5 correcto |
| T3 Codegen | 8k | ✅ PASS | 66.151s | 6/6 correcto |
| T3 Codegen | 32k | ✅ PASS | 165.702s | 6/6 correcto |
| T4 Multi-turn | 8k | ✅ PASS | 50.349s | 8/8 correcto |
| T4 Multi-turn | 32k | ✅ PASS | 143.387s | 8/8 correcto |

**Hallazgo crítico:** `chat_template_kwargs.enable_thinking=false` no es confiable con Huihui. En un request simple de JSON, el servidor devolvió `content=""`, `finish_reason="length"` y razonamiento en `reasoning_content`. Esto rompe el uso determinístico rápido que Qwen3.6 sí cumple.

Comparación clave:

| Métrica | Qwen3.6-35B-A3B | Huihui |
|---|---:|---:|
| T1 4k thinking=OFF | 1.9s | 19.137s |
| T1 32k thinking=OFF | 52s | 133.600s |
| T3 8k thinking=ON | ~140s | 66.151s |

Interpretación: Huihui razona/codea bien y es más rápido que Qwen3.6 en T3 8k, pero no puede reemplazar el perfil de ingeniería porque falla el requisito operativo de JSON/tool-calls rápidos con thinking OFF.

### Tarea 3 — Validación de visión

✅ PASS con configuración de visión y `max_tokens=2048`.

Arranque:
- `--mmproj ...Huihui...mmproj-F16.gguf`
- `--ctx-size 4096`
- `--override-tensor ".*=CPU"`
- Health OK en `8012`

Primer intento con `max_tokens=512`: el modelo procesó la imagen correctamente, pero agotó tokens en `reasoning_content` y dejó `content=""`.

Segundo intento con `max_tokens=2048`: PASS.
- `CONTENT_WORDS=83`
- `VISION_CONTENT_PASS=True`
- Descripción coherente de composición, colores y elementos de la imagen.

### Tarea 4 — Configuración final aplicada

Escenario real: **visión PASS + ingeniería precisa pero no adoptable por latencia/thinking OFF no confiable**.

Acciones aplicadas:
- ✅ Crear `/home/asalazar/start-huihui-vision.sh`
- ✅ Crear `/etc/systemd/system/llama-vision.service` apuntando a Huihui Vision
- ✅ Verificar `~/switch-model.sh vision`
- ✅ Health OK en `8012`
- ❌ No crear servicio de ingeniería Huihui; Qwen3.6 se mantiene como modelo de ingeniería en `llama-qwen3.service`

---

## Por qué es un candidato fuerte

| Atributo | Valor |
|---|---|
| Arquitectura | qwen35moe — MoE, 35B total, ~3B activos/token, 256 experts / 8 activos |
| Base | Qwen/Qwen3.5-35B-A3B |
| Destilado de | Claude 4.6 Opus (CoT, instruction following, structured output) |
| Abliterado | ✅ Sí — por huihui-ai (0 refusals para contenido sensible) |
| GGUF principal | `Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf` (~20 GB) |
| mmproj visión | `Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf` (~858 MB) |
| Contexto | 262,144 tokens nativos |
| Cuantizado con | llama.cpp b8352 |
| Repo | `cesarsal1nas/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M-GGUF` |

**Linaje completo:**
```
Qwen/Qwen3.5-35B-A3B
  → Jackrong/Qwen3.5-35B-A3B-Claude-4.6-Opus-Reasoning-Distilled  (destilado Opus)
    → huihui-ai/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated  (abliterado)
      → cesarsal1nas/...-Q4_K_M-GGUF  (cuantizado Q4_K_M)
```

---

## Advertencia crítica: Qwen3.5 vs Qwen3.6

El modelo actual (`Qwen3.6-35B-A3B`) usó arquitectura `qwen3_5_moe` con GatedDeltaNet, que requirió compilar llama.cpp v8998+ con `gated_delta_net.cu.o`. Este modelo es `Qwen3.5-35B-A3B` (versión anterior). Puede tener arquitectura diferente (`qwen35moe`).

**Tarea 0 debe verificar si el binario actual arranca este modelo antes de continuar.**
Si llama.cpp rechaza la arquitectura, la story termina ahí y se reporta el bloqueo.

---

## Rutas en servidor

| Recurso | Ruta |
|---|---|
| Binario llama-server | `/home/asalazar/llama.cpp/build/bin/llama-server` |
| Directorio destino modelo | `/home/asalazar/models/huihui/` |
| GGUF principal | `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf` |
| mmproj | `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf` |
| Modelo actual Qwen3 | `/home/asalazar/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf` |
| Runner actual Qwen3 | `/home/asalazar/qwen3_runner.py` |

---

## Tareas

### Tarea 0 — Verificación de espacio y descarga

#### 0.1 Verificar espacio disponible

```bash
df -h /home/asalazar/
# Necesario: ~21 GB para el GGUF + ~1 GB para mmproj = ~22 GB libres mínimo
```

Si no hay espacio suficiente, reportar y detener. No descargar parcialmente.

#### 0.2 Crear directorio y descargar

```bash
mkdir -p /home/asalazar/models/huihui/

# Descargar GGUF principal (~20 GB)
wget -c "https://huggingface.co/cesarsal1nas/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M-GGUF/resolve/main/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf" \
  -O /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf

# Descargar mmproj (~858 MB)
wget -c "https://huggingface.co/cesarsal1nas/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M-GGUF/resolve/main/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf" \
  -O /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf
```

> Usar `-c` para reanudar si la descarga se interrumpe.

#### 0.3 Verificar integridad básica

```bash
ls -lh /home/asalazar/models/huihui/
# GGUF debe ser ~20 GB, mmproj ~858 MB
# Si alguno es 0 bytes o notoriamente más pequeño, la descarga falló
```

---

### Tarea 1 — Prueba de arranque (verificar compatibilidad de arquitectura)

Antes de correr la suite completa, verificar que el binario actual soporta esta arquitectura.

```bash
# Detener cualquier modelo activo
sudo systemctl stop llama-ornstein llama-supergemma llama-trevorjs llama-qwen3 2>/dev/null

# Arranque mínimo — solo verificar que no hay error de arquitectura
/home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --port 8013 \
  --ctx-size 4096 \
  --jinja 2>&1 | head -40
```

**Interpretar output:**

- ✅ CONTINUAR si aparece: `llm_load_tensors`, `model loaded`, o el servidor arranca y responde en 8013
- ❌ DETENER si aparece: `unknown model architecture`, `unsupported model type`, o cualquier error antes de cargar tensores

Si falla: reportar el mensaje de error exacto y terminar la story aquí. El bloqueo es de arquitectura — requiere recompilar llama.cpp o buscar otro modelo.

Si pasa: matar el proceso y continuar con Tarea 2.

```bash
# Matar el proceso de prueba
pkill -f "llama-server.*huihui" 2>/dev/null
sleep 5
```

---

### Tarea 2 — Suite de validación de ingeniería (espejo de STORY_021)

Misma metodología que STORY_021: needle-in-haystack, criterio PASS = `json_valid=true` + `values_correct=N/N`.

Arrancar el servidor en modo ingeniería (sin mmproj):

```bash
nohup /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf \
  --alias huihui-eng \
  --host 0.0.0.0 \
  --port 8013 \
  --ctx-size 40960 \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --flash-attn on \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --jinja \
  --threads 6 \
  --threads-batch 24 \
  --threads-http 4 \
  > /home/asalazar/huihui-eng.log 2>&1 &

sleep 90
curl -s http://localhost:8013/health
# Esperado: {"status":"ok"}
```

#### 2.1 Correr suite T1–T4 con el runner existente de Qwen3

El runner `~/qwen3_runner.py` acepta el alias del modelo como tercer argumento. Usarlo con `huihui-eng`:

```bash
# T1 — Extracción JSON (thinking=OFF, rápido)
python3 ~/qwen3_runner.py T1 8k huihui-eng false
python3 ~/qwen3_runner.py T1 32k huihui-eng false

# T2 — MCP tool call (thinking=OFF)
python3 ~/qwen3_runner.py T2 8k huihui-eng false
python3 ~/qwen3_runner.py T2 32k huihui-eng false

# T3 — Codegen Python (thinking=ON, lento ~140-200s)
python3 ~/qwen3_runner.py T3 8k huihui-eng true
python3 ~/qwen3_runner.py T3 32k huihui-eng true

# T4 — Multi-turn agentic (thinking=ON)
python3 ~/qwen3_runner.py T4 8k huihui-eng true
python3 ~/qwen3_runner.py T4 32k huihui-eng true
```

> Si el runner no acepta el alias como argumento o tiene el modelo hardcodeado, editar `~/qwen3_runner.py` para parametrizar el modelo antes de correr.

#### 2.2 Test de thinking=OFF para JSON (crítico)

Verificar que el destilado de Opus no fuerza thinking ON incluso cuando se pide OFF:

```bash
curl -s http://localhost:8013/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui-eng",
    "messages": [
      {"role": "user", "content": "Return ONLY this JSON, nothing else: {\"status\": \"ok\", \"model\": \"huihui\"}"}
    ],
    "max_tokens": 64,
    "temperature": 0.1,
    "chat_template_kwargs": {"enable_thinking": false}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content']
print(content)
has_think = '<think>' in content
print('❌ thinking ON — abliterado puede haber afectado el flag' if has_think else '✅ thinking OFF: OK')
"
```

#### 2.3 Tabla de resultados esperada

Registrar los resultados en este formato:

| Test | ctx | PASS/FAIL | Tiempo | Notas |
|---|---|---|---|---|
| T1 JSON | 8k | | | |
| T1 JSON | 32k | | | |
| T2 MCP | 8k | | | |
| T2 MCP | 32k | | | |
| T3 Codegen | 8k | | | |
| T3 Codegen | 32k | | | |
| T4 Multi-turn | 8k | | | |
| T4 Multi-turn | 32k | | | |

**Criterio PASS para reemplazar Qwen3.6-35B-A3B:** todos los tests pasan en 8k y 32k. Si T3/T4 fallan en 32k pero pasan en 8k, el modelo es usable con limitaciones de ctx.

#### 2.4 Comparación de velocidad vs modelo actual

Registrar los tiempos de T1 (thinking=OFF) para comparar con los valores de referencia de STORY_021:

| Métrica | Qwen3.6-35B-A3B (referencia STORY_021) | Huihui (resultado) |
|---|---|---|
| T1 4k thinking=OFF | 1.9s | |
| T1 32k thinking=OFF | 52s | |
| T3 8k thinking=ON | ~140s | |

---

### Tarea 3 — Validación de visión con mmproj

Si la Tarea 2 pasa (o incluso si falla parcialmente), testear el mmproj independientemente. La visión es un caso de uso distinto al de ingeniería.

#### 3.1 Matar servidor de ingeniería y arrancar en modo visión

```bash
pkill -f "llama-server.*huihui" 2>/dev/null
sleep 10

nohup /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf \
  --mmproj /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf \
  --alias huihui-vision \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 4096 \
  --override-tensor ".*=CPU" \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --jinja \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4 \
  > /home/asalazar/huihui-vision.log 2>&1 &

sleep 60
curl -s http://localhost:8012/health
```

> `--override-tensor ".*=CPU"` fuerza el mmproj a RAM. Sin este flag el mmproj intenta cargar en VRAM, donde no hay espacio con el modelo principal ya cargado. Este fue el mismo problema y solución del SuperGemma Vision original (D16 en conversation_memory.md).

#### 3.2 Test de visión con imagen de prueba

Necesitas una imagen de prueba. Usar cualquier imagen local en el servidor o descargar una pequeña:

```bash
# Descargar imagen de prueba pequeña (o usar cualquier JPG/PNG que tengas)
wget -O /tmp/test_image.jpg "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png" 2>/dev/null || \
  echo "Usar imagen propia: cp /ruta/imagen.jpg /tmp/test_image.jpg"

# Convertir imagen a base64
IMAGE_B64=$(base64 -w 0 /tmp/test_image.jpg)

# Test de análisis visual
curl -s http://localhost:8012/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"huihui-vision\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/jpeg;base64,${IMAGE_B64}\"}},
          {\"type\": \"text\", \"text\": \"Describe this image in detail: composition, colors, mood, and any notable visual elements.\"}
        ]
      }
    ],
    \"max_tokens\": 512,
    \"temperature\": 0.3
  }" | python3 -c "
import sys, json
r = json.load(sys.stdin)
if 'error' in r:
    print('❌ ERROR:', r['error'])
else:
    content = r['choices'][0]['message']['content']
    print('--- RESPUESTA VISIÓN ---')
    print(content[:800])
    print('...' if len(content) > 800 else '')
    print('--- RESULTADO ---')
    print('✅ PASS: mmproj funciona' if len(content) > 50 else '❌ FAIL: respuesta vacía o muy corta')
"
```

**Criterio PASS para visión:** respuesta coherente de más de 50 palabras describiendo la imagen. No importa el formato exacto, solo que el modelo procese la imagen.

#### 3.3 Si el arranque con mmproj falla

Revisar los logs:
```bash
tail -50 /home/asalazar/huihui-vision.log
```

Errores comunes y qué hacer:
- `mmproj: failed to load` → verificar que el archivo mmproj se descargó completo (debe ser ~858MB)
- `CUDA out of memory` → el modelo + mmproj no caben; probar reducir `--n-gpu-layers` a 60 o 50
- `unsupported mmproj architecture` → este mmproj no es compatible con el build actual de llama.cpp — reportar y cerrar tarea de visión como bloqueada

---

### Tarea 4 — Decisión y configuración final

Basado en los resultados de Tarea 2 y Tarea 3, tomar una de estas decisiones:

#### Escenario A — Ingeniería PASS + Visión PASS (ideal)
Huihui reemplaza Qwen3.6-35B-A3B Y cubre visión. Un solo modelo para dos roles.

Acciones:
1. Crear `/home/asalazar/start-huihui-eng.sh` (sin mmproj, port 8013, ctx=40960)
2. Crear `/home/asalazar/start-huihui-vision.sh` (con mmproj, port 8012, ctx=4096)
3. Crear `/etc/systemd/system/llama-huihui-eng.service`
4. Crear `/etc/systemd/system/llama-huihui-vision.service`
5. Actualizar `~/switch-model.sh`: renombrar modo `qwen3` → `huihui` (o agregar `huihui` y deprecar `qwen3`)
6. El modelo Qwen3.6-35B-A3B queda como backup (no borrar el GGUF)

#### Escenario B — Ingeniería PASS + Visión FAIL
Huihui reemplaza Qwen3.6-35B-A3B pero no sirve para visión.

Acciones:
1. Crear solo `start-huihui-eng.sh` y `llama-huihui-eng.service`
2. Actualizar switch-model.sh
3. Visión sigue bloqueada — documentar en STORY_022 que el mmproj no funciona

#### Escenario C — Ingeniería FAIL (arquitectura no soportada)
El modelo no arranca en el build actual de llama.cpp.

Acciones:
1. No crear ningún servicio
2. Reportar el error exacto
3. Evaluar si recompilar llama.cpp con soporte adicional resolvería el problema

#### Escenario D — Ingeniería PARCIAL (pasa T1/T2 pero falla T3/T4)
El modelo funciona para JSON/tool-calls pero no para codegen largo.

Acciones:
1. Documentar las limitaciones exactas
2. El modelo puede usarse para tareas de baja complejidad pero no reemplaza completamente a Qwen3.6-35B-A3B
3. Mantener ambos modelos activos con roles distintos

---

#### Contenido de los scripts (completar solo si Escenario A o B)

**start-huihui-eng.sh** (modo ingeniería, sin mmproj):
```bash
#!/bin/bash
exec /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf \
  --alias huihui-eng \
  --host 0.0.0.0 \
  --port 8013 \
  --ctx-size 40960 \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --flash-attn on \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --jinja \
  --metrics \
  --slots \
  --slot-save-path /home/asalazar/llama-slots \
  --threads 6 \
  --threads-batch 24 \
  --threads-http 4
```

**start-huihui-vision.sh** (modo visión, con mmproj):
```bash
#!/bin/bash
exec /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf \
  --mmproj /home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf \
  --alias huihui-vision \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 4096 \
  --override-tensor ".*=CPU" \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --jinja \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4
```

**llama-huihui-eng.service**:
```ini
[Unit]
Description=llama.cpp server - Huihui Qwen3.5-35B MoE (ingeniería + Opus distill, puerto 8013)
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar
ExecStart=/home/asalazar/start-huihui-eng.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**llama-huihui-vision.service**:
```ini
[Unit]
Description=llama.cpp server - Huihui Qwen3.5-35B Vision (mmproj uncensored, puerto 8012)
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar
ExecStart=/home/asalazar/start-huihui-vision.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## Criterios de aceptación

- [x] Tarea 0: archivos descargados y verificados (~20GB + ~858MB)
- [x] Tarea 1: servidor arranca sin error de arquitectura
- [x] Tarea 2: T1 y T2 PASS en 8k y 32k
- [x] Tarea 2: T3 y T4 PASS en al menos 8k
- [ ] Tarea 2: velocidad T1 thinking=OFF ≤ 10s en 4k (comparable a Qwen3.6-35B-A3B) — FAIL: 19.137s
- [x] Tarea 3: mmproj arranca sin CUDA OOM
- [x] Tarea 3: respuesta de visión coherente en imagen de prueba
- [x] Tarea 4: servicios systemd creados según el escenario que corresponda
- [x] Tarea 4: switch-model.sh actualizado con el nuevo modo — ya existía modo `vision`; ahora apunta a `llama-vision.service` implementado con Huihui

---

## Al finalizar: actualizar memoria del proyecto

Registrar en `context/conversation_memory.md` la decisión tomada (D71):
- Contexto: validación Huihui-Qwen3.5-35B-A3B Claude Opus distill + abliterated
- Opciones: Escenario A/B/C/D según resultados
- Decisión: cuál escenario se eligió y por qué
- Impacto: qué cambió en el stack

Actualizar `context/project_state.md` sección "Equipo y Roles" tabla de modelos si el modelo fue adoptado.

Actualizar `context/stories/INDEX.md` y `context/artifacts_registry.md` con estado final.
