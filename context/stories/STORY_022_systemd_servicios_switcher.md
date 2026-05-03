# STORY_022 — Servicios systemd completos + fix Ornstein thinking + Qwen3 + Vision + switch-model.sh

> Estado: ✅ Completada
> Área: Infraestructura
> Desarrollada por: modelo de ingeniería (Qwen3 u otro agente externo)
> Sesión de creación: 16 (2026-05-01)
> Sesión de cierre: 17 (2026-05-01)
> Depende de: STORY_001 ✅, STORY_019 ✅, STORY_021 ✅

---

## Objetivo

Dejar la infraestructura de servicios systemd y el script `switch-model.sh` en estado de producción completo y correcto para los 6 servicios del stack: Ornstein, SuperGemma, TrevorJS, Vision, Qwen3 y ComfyUI.

**Al final de esta story:**
- Cada modelo tiene un servicio systemd correcto y funcional
- Ornstein tiene `--chat-template-kwargs '{"enable_thinking":false}'` activo y verificable
- `llama-qwen3.service` existe y arranca el modelo en puerto 8013
- `llama-vision.service` existe y arranca el modelo en puerto 8012 (bloqueado si no hay GGUF)
- `~/switch-model.sh` tiene 6 modos: ornstein, supergemma, trevorjs, vision, qwen3, image
- Todos los servicios pasan su health check correspondiente

---

## Resultado de ejecución — 2026-05-01

**Estado final:** ✅ completada para todos los servicios disponibles. `llama-vision.service` queda bloqueado correctamente porque `/home/asalazar/models/multimodal/` existe pero está vacío; no se creó un servicio con rutas inválidas.

### Cambios aplicados en servidor

| Archivo | Estado | Resultado |
|---|---|---|
| `/home/asalazar/start-ornstein.sh` | ✅ Creado | Wrapper con `--chat-template-kwargs '{"enable_thinking":false}'` |
| `/etc/systemd/system/llama-ornstein.service` | ✅ Modificado | Ahora apunta al wrapper; eliminada variable `LLAMA_CHAT_TEMPLATE_KWARGS` rota |
| `/home/asalazar/start-qwen3.sh` | ✅ Creado | Wrapper Qwen3 con flags MoE validados |
| `/etc/systemd/system/llama-qwen3.service` | ✅ Creado | Servicio Qwen3 en puerto `8013` |
| `/home/asalazar/switch-model.sh` | ✅ Reemplazado | 6 modos: `ornstein`, `supergemma`, `trevorjs`, `vision`, `qwen3`, `image` |
| `/home/asalazar/switch-model.sh.bak` | ✅ Creado | Backup del switcher anterior |
| `/home/asalazar/apply-story022-root.sh` | ✅ Creado | Script idempotente usado para aplicar los cambios root |
| `/etc/systemd/system/llama-vision.service` | 🔴 Bloqueado | No creado: faltan GGUF + mmproj multimodales |

### Auditoría inicial

- `llama-vision.service`: no existía.
- `llama-qwen3.service`: no existía.
- `llama-ornstein.service`: existía con bug confirmado; `Environment=LLAMA_CHAT_TEMPLATE_KWARGS={"enable_thinking":false}` causaba error de parsing y no activaba thinking OFF.
- `/home/asalazar/models/multimodal/`: directorio presente pero vacío.
- Qwen3 estaba corriendo manualmente en `8013`; se detuvo antes de pasar a systemd.

### Verificación end-to-end

| Check | Resultado |
|---|---|
| `~/switch-model.sh ornstein` | ✅ Health OK en `8012` |
| Ornstein process args | ✅ Muestra `--chat-template-kwargs {"enable_thinking":false}` |
| Ornstein functional test | ✅ Sin `<think>`, JSON válido |
| `~/switch-model.sh supergemma` | ✅ Health OK en `8012` |
| `~/switch-model.sh trevorjs` | ✅ Health OK en `8012` |
| `~/switch-model.sh qwen3` | ✅ Health OK en `8013` |
| Qwen3 functional test | ✅ Respuesta JSON sin `<think>` con `enable_thinking=false` por request |
| `~/switch-model.sh ornstein` después de Qwen3 | ✅ Detuvo `llama-qwen3`, arrancó Ornstein en `8012` |
| `~/switch-model.sh image` | ✅ Detuvo LLMs y arrancó ComfyUI en `8188` |
| `~/switch-model.sh` sin argumentos | ✅ Muestra Ornstein, SuperGemma, TrevorJS, Vision, Qwen3 y ComfyUI |

**Estado final del servidor tras la verificación:** ComfyUI activo; todos los LLMs inactivos.

---

## Contexto técnico de fondo

### Hardware
- Servidor: `asalazar@10.1.0.105` (Debian Linux)
- GPU: NVIDIA RTX 3060 12GB GDDR6
- CPU: Intel Core i5-9600K, 6 núcleos
- RAM: 32 GB
- **Solo un modelo puede estar activo a la vez — no hay VRAM para dos modelos simultáneamente**

### Rutas absolutas en el servidor
| Recurso | Ruta absoluta |
|---|---|
| Binario llama-server | `/home/asalazar/llama.cpp/build/bin/llama-server` |
| Modelos Gemma 4 | `/home/asalazar/models/gemma4/` |
| Modelo Qwen3 | `/home/asalazar/models/qwen3/` |
| Modelos multimodal | `/home/asalazar/models/multimodal/` (existe, vacío al cierre de STORY_022) |
| Slots KV cache | `/home/asalazar/llama-slots/` |
| Switch script | `/home/asalazar/switch-model.sh` |
| Servicios systemd | `/etc/systemd/system/` |

### Archivos GGUF en disco (verificado 2026-05-01)
| Archivo | Ruta | Estado |
|---|---|---|
| `Ornstein-26B-A4B-it-Q4_K_M.gguf` | `/home/asalazar/models/gemma4/` | ✅ Presente |
| `supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf` | `/home/asalazar/models/gemma4/` | ✅ Presente |
| `gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf` | `/home/asalazar/models/gemma4/` | ✅ Presente |
| `Qwen3.6-35B-A3B-Q4_K_M.gguf` | `/home/asalazar/models/qwen3/` | ✅ Presente |
| `supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf` | `/home/asalazar/models/multimodal/` | ❌ NO descargado |
| mmproj correspondiente al multimodal | `/home/asalazar/models/multimodal/` | ❌ NO descargado |

### Servicios systemd actuales (verificado al cierre, 2026-05-01)
| Servicio | Archivo | Estado |
|---|---|---|
| `llama-ornstein.service` | `/etc/systemd/system/llama-ornstein.service` | ✅ Existe — OK, thinking=false verificado por process args |
| `llama-supergemma.service` | `/etc/systemd/system/llama-supergemma.service` | ✅ Existe — OK |
| `llama-trevorjs.service` | `/etc/systemd/system/llama-trevorjs.service` | ✅ Existe — OK |
| `llama-vision.service` | `/etc/systemd/system/llama-vision.service` | 🔴 Bloqueado — NO existe porque faltan GGUF/mmproj |
| `llama-qwen3.service` | `/etc/systemd/system/llama-qwen3.service` | ✅ Existe — OK, health verificado en 8013 |
| `comfyui.service` | `/etc/systemd/system/comfyui.service` | ✅ Existe — OK |

---

## Bug crítico: Ornstein thinking=false NO está activo

### Descripción del bug
El servicio `llama-ornstein.service` tiene esta línea:
```ini
Environment=LLAMA_CHAT_TEMPLATE_KWARGS={"enable_thinking":false}
```
Esta variable de entorno **NO es leída por llama-server**. El binario `llama-server` acepta `--chat-template-kwargs` como argumento CLI, no como variable de entorno. El flag fue documentado como "no sobrevive parsing de systemd" en la sesión donde se detectó, pero la workaround no se implementó.

**Consecuencia:** Ornstein corre con thinking ON en producción. Esto causa goal-completion bias — el modelo produce prosa o cierra el output antes de completar el JSON. Validado en STORY_001/STORY_020: thinking OFF es obligatorio para outputs JSON correctos.

### Solución: wrapper script por servicio
En systemd, las comillas dentro de `ExecStart` con líneas continuation (`\`) no se interpretan como en bash. La solución más simple y robusta es un script bash intermedio que llame al binario con los parámetros correctos.

---

## Tareas

### Tarea 0 — Auditoría inicial (antes de cualquier cambio)

Ejecutar estos comandos y registrar el output antes de hacer nada:

```bash
# Estado de todos los servicios
systemctl status llama-ornstein llama-supergemma llama-trevorjs llama-vision llama-qwen3 comfyui --no-pager

# Contenido de los servicios actuales
cat /etc/systemd/system/llama-ornstein.service
cat /etc/systemd/system/llama-supergemma.service
cat /etc/systemd/system/llama-trevorjs.service

# Verificar si llama-ornstein tiene thinking=false activo (debe mostrar el flag en el proceso)
systemctl cat llama-ornstein
ps aux | grep llama-server | grep -v grep

# Verificar modelos en disco
ls -lh /home/asalazar/models/gemma4/
ls -lh /home/asalazar/models/qwen3/
ls -lh /home/asalazar/models/multimodal/ 2>/dev/null || echo "multimodal: directorio no existe"

# Switch script actual
cat /home/asalazar/switch-model.sh
```

---

### Tarea 1 — Fix llama-ornstein.service (thinking=false obligatorio)

#### 1.1 Crear wrapper script de Ornstein

```bash
cat > /home/asalazar/start-ornstein.sh << 'EOF'
#!/bin/bash
exec /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/gemma4/Ornstein-26B-A4B-it-Q4_K_M.gguf \
  --alias ornstein-prod \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 24576 \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --n-gpu-layers 999 \
  --n-cpu-moe 12 \
  --jinja \
  --chat-template-kwargs '{"enable_thinking":false}' \
  --flash-attn on \
  --metrics \
  --slots \
  --slot-save-path /home/asalazar/llama-slots \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4
EOF
chmod +x /home/asalazar/start-ornstein.sh
```

> **Importante:** El script usa `exec` (no `bash`) para que el proceso sea el llama-server directamente, no un subshell. Esto permite que systemd gestione el PID correctamente y que `Restart=on-failure` funcione.

#### 1.2 Reescribir llama-ornstein.service

Contenido final del archivo `/etc/systemd/system/llama-ornstein.service`:

```ini
[Unit]
Description=llama.cpp server - Ornstein (estructura y briefs, thinking=OFF)
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar
ExecStart=/home/asalazar/start-ornstein.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **Qué cambió respecto al servicio anterior:**
> - Se elimina `Environment=LLAMA_CHAT_TEMPLATE_KWARGS={"enable_thinking":false}` (no tenía efecto)
> - `ExecStart` apunta al wrapper script en lugar del binario directamente
> - El flag `--chat-template-kwargs '{"enable_thinking":false}'` ahora está en el wrapper donde las comillas sí funcionan

#### 1.3 Aplicar cambios y verificar

```bash
sudo systemctl daemon-reload
sudo systemctl restart llama-ornstein

# Esperar ~25 segundos a que cargue el modelo, luego verificar
sleep 30
curl -s http://localhost:8012/health
# Respuesta esperada: {"status":"ok"}

# Verificar que el proceso tiene el flag correcto
ps aux | grep llama-server | grep -v grep | grep enable_thinking
# Debe mostrar: --chat-template-kwargs {"enable_thinking":false}
```

#### 1.4 Test funcional de thinking=OFF

Enviar una petición real y verificar que no hay bloque `<think>...</think>` en la respuesta:

```bash
curl -s http://localhost:8012/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ornstein-prod",
    "messages": [
      {"role": "system", "content": "You are Ornstein. Output ONLY valid JSON."},
      {"role": "user", "content": "Extract entities from: Elena entered the vault. She carried a radio."}
    ],
    "max_tokens": 256,
    "temperature": 0
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content']
print('--- RESPONSE ---')
print(content)
print('--- CHECK ---')
if '<think>' in content:
    print('❌ FAIL: thinking está ON — hay bloque <think>')
else:
    print('✅ PASS: no hay bloque <think> — thinking está OFF')
try:
    json.loads(content.strip())
    print('✅ PASS: es JSON válido')
except:
    # puede estar en bloque de código
    import re
    m = re.search(r'\`\`\`(?:json)?\s*([\s\S]+?)\`\`\`', content)
    if m:
        try:
            json.loads(m.group(1))
            print('✅ PASS: JSON válido dentro de bloque código')
        except:
            print('❌ FAIL: JSON inválido')
    else:
        print('⚠️  WARN: no es JSON directo — revisar manualmente')
"
```

**Criterio de éxito:** respuesta sin `<think>`, con JSON válido, en menos de 10 segundos.

---

### Tarea 2 — Verificar llama-supergemma.service y llama-trevorjs.service

Estos servicios existen y tienen los parámetros correctos. Solo verificar que arrancan sin errores y que el health check responde.

```bash
# SuperGemma
sudo systemctl restart llama-supergemma
sleep 30
curl -s http://localhost:8012/health
# Esperado: {"status":"ok"}
systemctl status llama-supergemma --no-pager | head -20

# TrevorJS
sudo systemctl stop llama-supergemma
sudo systemctl restart llama-trevorjs
sleep 30
curl -s http://localhost:8012/health
systemctl status llama-trevorjs --no-pager | head -20
```

Si alguno falla, revisar `journalctl -u llama-supergemma -n 50` o `journalctl -u llama-trevorjs -n 50`.

**No modificar estos servicios si no hay error.** Los parámetros actuales son:
- `--ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0`
- `--n-gpu-layers 999 --n-cpu-moe 12 --jinja --flash-attn on`
- `--metrics --slots --slot-save-path /home/asalazar/llama-slots`
- `--threads 6 --threads-batch 6 --threads-http 4`

---

### Tarea 3 — Crear llama-qwen3.service

Qwen3 usa **puerto 8013** (distinto de todos los demás que usan 8012). Requiere flags especiales para su arquitectura MoE.

#### 3.1 Crear wrapper script de Qwen3

```bash
cat > /home/asalazar/start-qwen3.sh << 'EOF'
#!/bin/bash
exec /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/qwen3/Qwen3.6-35B-A3B-Q4_K_M.gguf \
  --alias qwen3-coder \
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
EOF
chmod +x /home/asalazar/start-qwen3.sh
```

> **Por qué estos valores:**
> - `--port 8013`: Qwen3 corre en puerto distinto. Ornstein y los modelos creativos usan 8012. Nunca simultáneos por VRAM, pero puertos distintos para distinguirlos.
> - `--n-gpu-layers 99` + `--n-cpu-moe 99`: Los expertos MoE se ejecutan en RAM (32GB disponibles). Sin `--n-cpu-moe`, Qwen3 no puede cargar en 12GB de VRAM. Validado en STORY_021.
> - `--cache-type-k q8_0 --cache-type-v q8_0`: KV cache comprimido para que ctx=40960 quepa en VRAM. Con q4_0 el modelo producía outputs incorrectos; q8_0 fue el valor validado.
> - `--ctx-size 40960`: Tareas T3 (codegen largo) requieren 27k input + 5k output + overhead de template. Con ctx=32768 el T3-32k fallaba. Validado en STORY_021.
> - `--threads-batch 24`: Qwen3 MoE se beneficia de más threads para el batch processing en CPU. Valor validado en suite de STORY_021.
> - **SIN** `--chat-template-kwargs`: Qwen3 recibe `enable_thinking` vía parámetros de inferencia en cada llamada, no como flag global. Esto permite alternar thinking ON/OFF por tarea desde el cliente.

#### 3.2 Crear llama-qwen3.service

Contenido del archivo `/etc/systemd/system/llama-qwen3.service`:

```ini
[Unit]
Description=llama.cpp server - Qwen3.6-35B-A3B (ingeniería y codegen, puerto 8013)
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar
ExecStart=/home/asalazar/start-qwen3.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **Nota:** `WantedBy=multi-user.target` pero **NO ejecutar** `systemctl enable llama-qwen3`. El servicio es de inicio manual, igual que los otros LLMs. Solo ComfyUI tiene el mismo patrón de no-autostart. `systemctl enable` activaría el arranque automático con el sistema, lo que conflictuaría con otros modelos en VRAM.

#### 3.3 Aplicar y verificar

```bash
sudo systemctl daemon-reload
sudo systemctl start llama-qwen3

# Esperar carga — Qwen3 tarda más que los Gemma (~60-90 segundos) por el volumen MoE
sleep 90
curl -s http://localhost:8013/health
# Respuesta esperada: {"status":"ok"}

systemctl status llama-qwen3 --no-pager | head -20
```

#### 3.4 Test funcional de Qwen3

```bash
# Test mínimo: extracción JSON con thinking=OFF
curl -s http://localhost:8013/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder",
    "messages": [
      {"role": "user", "content": "Return ONLY this JSON: {\"status\": \"ok\", \"model\": \"qwen3\"}"}
    ],
    "max_tokens": 64,
    "temperature": 0.1,
    "chat_template_kwargs": {"enable_thinking": false}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content']
print(content)
if '<think>' in content:
    print('❌ WARN: thinking ON en este request — revisar parámetros')
else:
    print('✅ thinking OFF: OK')
"
```

**Criterio de éxito:** health check `{"status":"ok"}` en puerto 8013, respuesta JSON válida sin `<think>`.

Si falla, revisar logs:
```bash
journalctl -u llama-qwen3 -n 100 --no-pager
# Errores comunes:
# - "model not found": verificar ruta exacta en start-qwen3.sh
# - "CUDA error": VRAM insuficiente — verificar que no hay otro modelo activo
# - "unknown architecture": llama.cpp no tiene soporte qwen3_5_moe compilado
#   Solución: verificar build llama.cpp v8998+ con gated_delta_net.cu.o
```

---

### Tarea 4 — Crear llama-vision.service

> ⚠️ **BLOQUEADA hasta que los modelos estén descargados.**

#### 4.1 Verificar si los modelos existen

```bash
ls -lh /home/asalazar/models/multimodal/ 2>/dev/null || echo "DIRECTORIO NO EXISTE"
```

**Si el directorio no existe o está vacío:** los GGUFs no fueron descargados. La tarea de creación del servicio está bloqueada. **NO crear el servicio con rutas inválidas.** Un servicio apuntando a un modelo que no existe entrará en restart loop.

#### 4.2 Descargar los modelos (si no existen)

Los modelos del SuperGemma Vision fueron descargados originalmente del mirror `kof1467` (el repo oficial requería auth). Si el mirror ya no está disponible, buscar alternativas antes de proceder.

```bash
mkdir -p /home/asalazar/models/multimodal/

# Archivo principal (GGUF del modelo multimodal)
# Nombre esperado: supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf
# Tamaño aproximado: ~15-17 GB (Q4_K_M de 26B)

# Archivo mmproj (vision encoder — archivo separado pequeño)
# Nombre esperado: algo como mmproj-supergemma4-26b-abliterated-multimodal-f16.gguf
# Tamaño aproximado: ~700MB-1.5GB
```

> **Pregunta al usuario antes de continuar:** ¿Tienes los archivos descargados? ¿Cuáles son los nombres exactos de los archivos GGUF y mmproj? El servicio no puede crearse sin saber los nombres de archivo exactos.

#### 4.3 Crear wrapper script de Vision (cuando los modelos existan)

Reemplazar `<GGUF_FILE>` y `<MMPROJ_FILE>` con los nombres reales:

```bash
cat > /home/asalazar/start-vision.sh << 'SCRIPT'
#!/bin/bash
exec /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/multimodal/<GGUF_FILE> \
  --mmproj /home/asalazar/models/multimodal/<MMPROJ_FILE> \
  --alias supergemma-vision \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 4096 \
  --override-tensor ".*=CPU" \
  --n-gpu-layers 999 \
  --n-cpu-moe 12 \
  --jinja \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4
SCRIPT
chmod +x /home/asalazar/start-vision.sh
```

> **Por qué estos valores:**
> - `--ctx-size 4096`: reducido para liberar VRAM para el mmproj. Con ctx más alto, el modelo causa SEGV.
> - `--override-tensor ".*=CPU"`: fuerza el mmproj a RAM. Sin este flag, llama.cpp intenta cargar el mmproj en VRAM, pero con el modelo principal ya cargado solo quedan ~27MB libres — insuficiente para el mmproj (~1.1GB). El flag `--mmproj-use-cpu` no existe en el build actual.
> - `--n-cpu-moe 12`: mismo que los otros modelos Gemma 4.
> - **SIN** `--metrics --slots --slot-save-path`: el vision model usa ctx pequeño y no tiene casos de uso multi-turn; los slots KV no aportan aquí.

#### 4.4 Crear llama-vision.service (cuando los modelos existan)

```ini
[Unit]
Description=llama.cpp server - SuperGemma Vision (análisis multimodal, puerto 8012)
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar
ExecStart=/home/asalazar/start-vision.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 4.5 Aplicar y verificar (cuando los modelos existan)

```bash
sudo systemctl daemon-reload
sudo systemctl start llama-vision
sleep 40
curl -s http://localhost:8012/health
```

---

### Tarea 5 — Actualizar switch-model.sh

El script actual tiene estos problemas:
1. `MODELS` solo incluye `"ornstein supergemma trevorjs"` — falta qwen3
2. `stop_all_llm()` no detiene `llama-qwen3`
3. No hay modo `qwen3`
4. El status display no muestra qwen3
5. La verificación de salud usa siempre `http://localhost:8012/health` — pero Qwen3 usa 8013

**Contenido completo del nuevo `~/switch-model.sh`:**

```bash
#!/bin/bash

# Modelos en puerto 8012 (creativos + normalización)
MODELS_8012="ornstein supergemma trevorjs vision"
# Modelos en puerto 8013 (ingeniería)
MODELS_8013="qwen3"

TARGET=$1

usage() {
  echo "Uso: switch-model.sh [ornstein|supergemma|trevorjs|vision|qwen3|image]"
  echo ""
  echo "Estado actual:"
  for m in $MODELS_8012; do
    STATUS=$(systemctl is-active llama-$m 2>/dev/null || echo "inactivo")
    echo "  llama-$m: $STATUS"
  done
  for m in $MODELS_8013; do
    STATUS=$(systemctl is-active llama-$m 2>/dev/null || echo "inactivo")
    echo "  llama-$m: $STATUS"
  done
  echo "  comfyui: $(systemctl is-active comfyui 2>/dev/null || echo inactivo)"
}

stop_all_llm() {
  for m in $MODELS_8012; do
    systemctl is-active --quiet llama-$m 2>/dev/null && sudo systemctl stop llama-$m && echo "  detenido: llama-$m"
  done
  for m in $MODELS_8013; do
    systemctl is-active --quiet llama-$m 2>/dev/null && sudo systemctl stop llama-$m && echo "  detenido: llama-$m"
  done
}

wait_health() {
  local PORT=$1
  local NAME=$2
  for i in $(seq 1 45); do
    sleep 2
    STATUS=$(curl -s "http://localhost:${PORT}/health" 2>/dev/null | grep -o '"ok"')
    if [[ "$STATUS" == '"ok"' ]]; then
      echo "✅ $NAME activo en http://10.1.0.105:${PORT}"
      return 0
    fi
  done
  echo "⚠️  El servidor tardó más de lo esperado. Revisa: sudo journalctl -u llama-$NAME -n 50"
  return 1
}

if [[ -z "$TARGET" ]]; then
  usage
  exit 0
fi

# ── Modo imagen ───────────────────────────────────────────────────────────────
if [[ "$TARGET" == "image" ]]; then
  echo "Deteniendo modelos LLM..."
  stop_all_llm
  echo "Iniciando ComfyUI..."
  sudo systemctl start comfyui
  for i in $(seq 1 30); do
    sleep 2
    STATUS=$(curl -s http://localhost:8188 2>/dev/null | grep -oi "comfyui")
    if [[ -n "$STATUS" ]]; then
      echo "✅ ComfyUI activo en http://10.1.0.105:8188"
      exit 0
    fi
  done
  echo "✅ ComfyUI iniciado en http://10.1.0.105:8188"
  exit 0
fi

# ── Modo vision ───────────────────────────────────────────────────────────────
if [[ "$TARGET" == "vision" ]]; then
  echo "Deteniendo ComfyUI si está activo..."
  systemctl is-active --quiet comfyui && sudo systemctl stop comfyui && echo "  detenido: comfyui"
  echo "Deteniendo modelos LLM activos..."
  stop_all_llm
  echo "Iniciando llama-vision..."
  sudo systemctl start llama-vision
  wait_health 8012 "vision"
  exit $?
fi

# ── Modo Qwen3 (puerto 8013) ──────────────────────────────────────────────────
if [[ "$TARGET" == "qwen3" ]]; then
  echo "Deteniendo ComfyUI si está activo..."
  systemctl is-active --quiet comfyui && sudo systemctl stop comfyui && echo "  detenido: comfyui"
  echo "Deteniendo modelos LLM activos..."
  stop_all_llm
  echo "Iniciando llama-qwen3 (puede tardar 60-90 segundos)..."
  sudo systemctl start llama-qwen3
  wait_health 8013 "qwen3"
  exit $?
fi

# ── Modos LLM puerto 8012 (ornstein, supergemma, trevorjs) ───────────────────
if echo "$MODELS_8012" | grep -qw "$TARGET"; then
  echo "Deteniendo ComfyUI si está activo..."
  systemctl is-active --quiet comfyui && sudo systemctl stop comfyui && echo "  detenido: comfyui"
  echo "Deteniendo modelos activos..."
  stop_all_llm
  echo "Iniciando llama-$TARGET..."
  sudo systemctl start llama-$TARGET
  wait_health 8012 "$TARGET"
  exit $?
fi

echo "Error: modo desconocido '$TARGET'"
usage
exit 1
```

#### 5.1 Aplicar el nuevo switch-model.sh

```bash
# Hacer backup del actual
cp /home/asalazar/switch-model.sh /home/asalazar/switch-model.sh.bak

# Escribir el nuevo contenido (copiar el bloque de arriba al archivo)
# Verificar que el nuevo script es ejecutable
chmod +x /home/asalazar/switch-model.sh

# Test: modo sin argumentos debe mostrar status de todos los servicios
/home/asalazar/switch-model.sh
```

---

### Tarea 6 — Verificación end-to-end del switcher

Ejecutar en secuencia para confirmar que el switcher funciona correctamente con todos los modelos disponibles:

```bash
# 1. Arrancar Ornstein
~/switch-model.sh ornstein
# Esperar: "✅ ornstein activo en http://10.1.0.105:8012"
# Verificar thinking=OFF:
ps aux | grep llama-server | grep -v grep | grep enable_thinking
# Debe mostrar: {"enable_thinking":false}

# 2. Cambiar a SuperGemma
~/switch-model.sh supergemma
# Esperado: detiene llama-ornstein, arranca llama-supergemma, health OK en 8012

# 3. Cambiar a TrevorJS
~/switch-model.sh trevorjs
# Esperado: detiene llama-supergemma, arranca llama-trevorjs, health OK en 8012

# 4. Cambiar a Qwen3
~/switch-model.sh qwen3
# Esperado: detiene llama-trevorjs, arranca llama-qwen3, health OK en 8013
# NOTA: tarda 60-90 segundos en cargar

# 5. Volver a Ornstein
~/switch-model.sh ornstein
# Esperado: detiene llama-qwen3, arranca llama-ornstein, health OK en 8012

# 6. Modo imagen (no LLM)
~/switch-model.sh image
# Esperado: detiene todos los LLMs, arranca ComfyUI en 8188

# 7. Status final
~/switch-model.sh
# Debe mostrar todos los servicios y sus estados
```

**NO testear vision en este ciclo si los modelos no están descargados.**

---

## Criterios de aceptación

- [x] `ps aux | grep llama-server | grep enable_thinking` muestra `{"enable_thinking":false}` cuando Ornstein está activo
- [x] `~/switch-model.sh ornstein` → health OK en 8012, thinking=OFF verificado
- [x] `~/switch-model.sh supergemma` → health OK en 8012, sin errores
- [x] `~/switch-model.sh trevorjs` → health OK en 8012, sin errores
- [x] `~/switch-model.sh qwen3` → health OK en **8013**, sin errores
- [x] `~/switch-model.sh` (sin args) muestra los 6 servicios + comfyui en el status
- [x] `~/switch-model.sh ornstein` después de tener qwen3 activo → detiene llama-qwen3 correctamente
- [x] `llama-vision`: servicio creado Y health OK en 8012 (solo si los GGUFs multimodal existen) — no aplica; GGUF/mmproj ausentes
- [x] Ningún wrapper script tiene errores de permisos o sintaxis bash

---

## Archivos a crear/modificar

| Archivo | Operación | Descripción |
|---|---|---|
| `/home/asalazar/start-ornstein.sh` | **Crear** | Wrapper con `--chat-template-kwargs '{"enable_thinking":false}'` |
| `/etc/systemd/system/llama-ornstein.service` | **Modificar** | Apuntar a wrapper, eliminar env var que no funciona |
| `/home/asalazar/start-qwen3.sh` | **Crear** | Wrapper Qwen3 con flags MoE validados |
| `/etc/systemd/system/llama-qwen3.service` | **Crear** | Nuevo servicio Qwen3 en puerto 8013 |
| `/home/asalazar/start-vision.sh` | **Crear** (si GGUFs existen) | Wrapper Vision con `--override-tensor ".*=CPU"` |
| `/etc/systemd/system/llama-vision.service` | **Crear** (si GGUFs existen) | Nuevo servicio Vision en puerto 8012 |
| `/home/asalazar/switch-model.sh` | **Reemplazar** | Añadir modo qwen3, refactor de stop/health functions |

---

## Notas importantes para el agente que ejecute esta story

1. **No hacer cambios especulativos.** Si algo no está en esta story, no cambiarlo. Esto aplica especialmente a los servicios de SuperGemma y TrevorJS que ya funcionan.

2. **Verificar antes de modificar.** Siempre leer el estado actual (Tarea 0) antes de aplicar cambios. Los archivos en servidor pueden haber cambiado entre sesiones.

3. **Switch-model.sh backup obligatorio.** Antes de reemplazar el script, copiar a `.bak`. Un error en el switcher deja inutilizables todos los modelos.

4. **Vision es bloqueada por ausencia de GGUFs.** Si `/home/asalazar/models/multimodal/` está vacío o no existe, el servicio llama-vision.service **NO debe crearse**. Crear el servicio con una ruta de modelo inválida causará restart loops. Preguntar al usuario por los archivos antes de continuar.

5. **Puerto 8013 para Qwen3.** El health check de Qwen3 es `curl http://localhost:8013/health`, no 8012. Verificar en el puerto correcto.

6. **VRAM exclusiva.** Solo un modelo puede estar activo. `stop_all_llm()` en el nuevo switcher para todos antes de arrancar cualquier otro.

7. **Qwen3 demora en cargar.** ~60-90 segundos hasta health OK. El `wait_health` hace 45 intentos de 2s = 90s máximo de espera. No interrumpir el proceso si parece lento.

8. **Confirmar con el usuario** antes de ejecutar `systemctl enable` en cualquier servicio. Ningún LLM debe tener auto-start habilitado.
