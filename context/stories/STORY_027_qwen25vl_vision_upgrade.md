# STORY_027 — Qwen2.5-VL-32B Vision Upgrade: Reemplazar Huihui Vision

> Estado: ✅ Completada — Objetivo cumplido con SuperGemma4 Vision (no Qwen2.5-VL-32B)
> Área: Infraestructura / Modelos
> Desarrollada por: Codex (agente externo) + sesión 22
> Sesión de creación: 21 (2026-05-01) — Cierre: sesión 22 (2026-05-02)
> Depende de: STORY_023 ✅, STORY_025 ✅

---

## Objetivo

Reemplazar el backend de visión actual (`Huihui-Qwen3.5-35B-A3B` con mmproj genérico) por
`Qwen2.5-VL-32B-Instruct-abliterated` — un modelo diseñado nativamente para visión con ViT
propio y soporte de dynamic resolution tiling a 32K tokens de contexto.

El modelo actual fue adoptado como solución provisional en STORY_023. Sus limitaciones son
conocidas: mmproj genérico, ctx=4096 para imágenes, arquitectura `qwen35moe` no nativa de
visión. Qwen2.5-VL-32B es la arquitectura correcta.

---

## Resultado UAT — 2026-05-02

**Decisión:** Qwen2.5-VL-32B no es viable para producción en el hardware actual por latencia,
aunque la calidad descriptiva es muy buena.

**Contexto:** Tareas 0-3 pasaron técnicamente: el modelo descarga, carga como `qwen2vl`, el
mmproj funciona, la API multimodal responde y Open WebUI puede usar el endpoint. Sin embargo,
la prueba UI real mostró latencia excesiva para el usuario final.

**Evidencia técnica:**
- V1 API: 609 palabras, PASS funcional, pero generación a ~1.46 tok/s.
- V1 API total: ~555.9s para 789 tokens generados.
- UAT UI: respuesta perceptiblemente demasiado lenta para flujo interactivo.
- El cuello de botella es generación textual del modelo denso 32B, no el procesamiento visual.

**Criterio actualizado:** el siguiente candidato de visión debe entregar como mínimo el doble de
velocidad percibida. Objetivo técnico provisional: >=3 tok/s o reducir la latencia de una
descripción visual típica al menos 50% vs Qwen2.5-VL-32B en este hardware.

**Conclusión:** Qwen2.5-VL-32B queda documentado como funcional y de alta calidad descriptiva,
pero rechazado para prod por latencia. Buscar alternativa más rápida antes de adoptarlo como
backend definitivo de visión.

---

## Por qué este modelo

| Atributo | Huihui Vision (actual) | Qwen2.5-VL-32B (objetivo) |
|---|---|---|
| Arquitectura | qwen35moe — texto con mmproj añadido | qwen2vl — nativa de visión |
| Vision encoder | mmproj genérico F16 | ViT propio con dynamic resolution tiling |
| ctx para imágenes | 4,096 | 32,000 |
| MMMU benchmark | no medido | **70.0** (supera al 72B predecesor con 64.5) |
| Abliterado | ✅ huihui-ai | ✅ huihui-ai |
| mmproj size | 858 MB (F16) | 0.8 GB (Q8_0) o 1.5 GB (F16) |

El dato decisivo: MMMU 70.0 con 32B supera al Qwen2-VL-72B con 64.5. La nueva arquitectura
es estrictamente superior en análisis visual con menos parámetros.

---

## Modelo objetivo

| Campo | Valor |
|---|---|
| Nombre | Qwen2.5-VL-32B-Instruct-abliterated |
| Abliterado por | huihui-ai |
| GGUF repo (abliterated) | `mradermacher/Qwen2.5-VL-32B-Instruct-abliterated-GGUF` |
| GGUF repo (vanilla, alternativo) | `second-state/Qwen2.5-VL-32B-Instruct-GGUF` |
| iMatrix variant | `mradermacher/Qwen2.5-VL-32B-Instruct-abliterated-i1-GGUF` |
| Parámetros | 32.8B — Denso (no MoE) |
| Arquitectura | qwen2vl |
| Q4_K_M size | ~20.0 GB |
| Q5_K_M size | ~23.4 GB |
| mmproj Q8_0 | ~0.8 GB |
| mmproj F16 | ~1.5 GB |
| ctx máximo | 32,000 tokens |
| Cuantizado con | llama.cpp b5196 |

**Cuantización recomendada:** Q4_K_M (20 GB). Q5_K_M si el espacio lo permite.
**mmproj recomendado:** Q8_0 (0.8 GB) — ahorra VRAM vs F16 con impacto mínimo en calidad.

---

## Consideraciones de hardware

El modelo es **denso** (32.8B), no MoE. Diferencia con los modelos actuales:
- Modelos MoE del stack (Huihui, Qwen3.6): ~3B parámetros activos/token → rápidos
- Qwen2.5-VL-32B denso: todos los parámetros activos → más lento en tokens/s

Para inferencia de visión se asumió inicialmente que una latencia de 30–90s por imagen sería
operacionalmente aceptable. Esa premisa quedó invalidada por UAT UI el 2026-05-02: la latencia
real y la velocidad de generación (~1.46 tok/s en V1) son demasiado lentas para producción.

**Offload GPU+RAM:** con 12GB VRAM + 32GB RAM, usar `--n-gpu-layers` para offload parcial.
Estimar cuántas capas caben en VRAM y el resto se ejecuta en RAM. El calibrado se hace en
Tarea 1.

---

## Rutas en servidor

| Recurso | Ruta |
|---|---|
| Binario llama-server | `/home/asalazar/llama.cpp/build/bin/llama-server` |
| Directorio destino modelo | `/home/asalazar/models/qwen25vl/` |
| GGUF principal (objetivo) | `/home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf` |
| mmproj (objetivo) | `/home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf` |
| Modelo Huihui Vision actual | `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf` |
| mmproj Huihui actual | `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf` |
| Servicio systemd visión | `/etc/systemd/system/llama-vision.service` |
| Wrapper actual visión | `/home/asalazar/start-huihui-vision.sh` |
| Script switch | `/home/asalazar/switch-model.sh` |

---

## Tareas

### Tarea 0 — Verificar espacio y descargar modelo

#### 0.1 Verificar espacio disponible

```bash
df -h /home/asalazar/
# Necesario: ~21 GB para Q4_K_M + ~1 GB para mmproj = ~22 GB libres mínimo
# Si no hay suficiente espacio, reportar y detener aquí.
```

#### 0.2 Crear directorio y descargar GGUF + mmproj

```bash
mkdir -p /home/asalazar/models/qwen25vl/

# Descargar GGUF principal (~20 GB) — abliterated Q4_K_M
wget -c "https://huggingface.co/mradermacher/Qwen2.5-VL-32B-Instruct-abliterated-GGUF/resolve/main/Qwen2.5-VL-32B-Instruct-abliterated.Q4_K_M.gguf" \
  -O /home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf

# Descargar mmproj Q8_0 (~0.8 GB)
# Nota: el mmproj viene incluido en el repo de mradermacher o en el repo de second-state
# Verificar el nombre exacto del archivo mmproj en HuggingFace antes de ejecutar
wget -c "https://huggingface.co/mradermacher/Qwen2.5-VL-32B-Instruct-abliterated-GGUF/resolve/main/mmproj-Q8_0.gguf" \
  -O /home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf
```

> **IMPORTANTE:** Verificar los nombres exactos de archivo en HuggingFace antes de ejecutar
> los wget. Los repos de mradermacher pueden usar nomenclaturas distintas para el mmproj.
> Si el mmproj no está en el repo abliterated, buscarlo en `second-state/Qwen2.5-VL-32B-Instruct-GGUF`.

> Usar `-c` en todos los wget para reanudar descargas interrumpidas.

#### 0.3 Verificar integridad básica

```bash
ls -lh /home/asalazar/models/qwen25vl/
# GGUF debe ser ~20 GB
# mmproj debe ser ~0.8 GB (Q8_0) o ~1.5 GB (F16)
# Si alguno es 0 bytes o notoriamente más pequeño, la descarga falló
```

---

### Tarea 1 — Verificar compatibilidad de arquitectura y calibrar GPU layers

#### 1.1 Test de arranque mínimo

```bash
# Detener cualquier modelo activo en 8012
sudo systemctl stop llama-vision llama-ornstein llama-supergemma llama-trevorjs 2>/dev/null
sleep 5

# Arranque mínimo — solo verificar que no hay error de arquitectura
/home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf \
  --mmproj /home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf \
  --n-gpu-layers 20 \
  --port 8012 \
  --ctx-size 4096 \
  --jinja 2>&1 | head -60
```

**Interpretar output:**
- ✅ CONTINUAR si aparece: `llm_load_tensors`, `model loaded`, `server is listening`
- ❌ DETENER si aparece: `unknown model architecture`, `unsupported model type`, o error antes de cargar tensores

Si falla por arquitectura: reportar el mensaje exacto y terminar story. El bloqueo requiere
actualizar llama.cpp.

#### 1.2 Calibrar --n-gpu-layers para offload óptimo

El modelo es denso 32.8B. Con 12GB VRAM, el objetivo es maximizar las capas en GPU
sin causar OOM. Probar en incrementos:

```bash
# Método: arrancar y observar cuánta VRAM se usa con nvidia-smi
# Probar: 20 layers primero, luego subir si no hay OOM

# En terminal 1: monitor de VRAM
watch -n 2 nvidia-smi --query-gpu=memory.used,memory.free --format=csv

# En terminal 2: arrancar con layers incrementales
# Empezar con 20, subir a 30, 40 si la VRAM aguanta

/home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf \
  --mmproj /home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf \
  --n-gpu-layers 30 \
  --port 8012 \
  --ctx-size 8192 \
  --override-tensor ".*=CPU" \
  --jinja 2>&1 | grep -E "llm_load|ggml_cuda|VRAM|error|loaded"
```

> `--override-tensor ".*=CPU"` fuerza el vision encoder (mmproj) a RAM, liberando VRAM
> para las capas del LLM. Este flag es el mismo que se usa con Huihui Vision (D16).

Registrar el valor de `--n-gpu-layers` que maximiza VRAM sin OOM. Usarlo en todas las
tareas siguientes y en el wrapper final.

---

### Tarea 2 — Validación de visión

Arrancar el servidor con los parámetros calibrados en Tarea 1.

#### 2.1 Arrancar servidor en modo visión

```bash
# Matar proceso anterior si existe
pkill -f "llama-server.*qwen25vl" 2>/dev/null
sleep 10

# Usar el n-gpu-layers calibrado en Tarea 1 (reemplazar N con el valor)
nohup /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf \
  --mmproj /home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf \
  --alias qwen25vl-vision \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 16384 \
  --n-gpu-layers N \
  --override-tensor ".*=CPU" \
  --flash-attn on \
  --jinja \
  --metrics \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4 \
  > /home/asalazar/qwen25vl-vision.log 2>&1 &

sleep 90
curl -s http://localhost:8012/health
# Esperado: {"status":"ok"}
```

#### 2.2 Test V1 — Descripción de imagen de referencia (smoke test)

```bash
# Usar cualquier imagen JPG/PNG disponible en el servidor
# Si no hay ninguna: wget -O /tmp/test.jpg https://picsum.photos/800/600

IMAGE_B64=$(base64 -w 0 /tmp/test.jpg)

curl -s http://localhost:8012/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"qwen25vl-vision\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/jpeg;base64,${IMAGE_B64}\"}},
          {\"type\": \"text\", \"text\": \"Describe in detail: composition, color palette, lighting, textures, and emotional mood of this image.\"}
        ]
      }
    ],
    \"max_tokens\": 2048,
    \"temperature\": 0.3,
    \"chat_template_kwargs\": {\"enable_thinking\": true}
  }" | python3 -c "
import sys, json
r = json.load(sys.stdin)
if 'error' in r:
    print('ERROR:', r['error'])
    sys.exit(1)
content = r['choices'][0]['message']['content']
word_count = len(content.split())
print(f'--- RESPUESTA ({word_count} palabras) ---')
print(content[:1200])
print('...' if len(content) > 1200 else '')
print('--- RESULTADO ---')
print('PASS' if word_count >= 100 else 'FAIL: respuesta muy corta')
"
```

**Criterio PASS V1:** descripción coherente de 100+ palabras que mencione al menos 3 de:
composición, colores, iluminación, texturas, mood.

#### 2.3 Test V2 — Contexto largo (validar 16K)

```bash
# Mismo test con ctx=16384 para verificar que el tiling funciona a mayor resolución
# Usar imagen de mayor resolución si está disponible (~1024x1024 o más)

IMAGE_B64=$(base64 -w 0 /ruta/imagen_hd.jpg)

curl -s http://localhost:8012/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"qwen25vl-vision\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/jpeg;base64,${IMAGE_B64}\"}},
          {\"type\": \"text\", \"text\": \"Analyze this image as an art director for a survival horror video game. Describe: (1) composition and framing, (2) color palette with approximate hex values, (3) lighting quality and direction, (4) texture details, (5) emotional atmosphere and mood, (6) specific elements that could inspire horror game assets.\"}
        ]
      }
    ],
    \"max_tokens\": 3000,
    \"temperature\": 0.3,
    \"chat_template_kwargs\": {\"enable_thinking\": true}
  }" | python3 -c "
import sys, json
r = json.load(sys.stdin)
if 'error' in r:
    print('ERROR:', r['error'])
    sys.exit(1)
content = r['choices'][0]['message']['content']
word_count = len(content.split())
print(f'--- ART DIRECTOR ANALYSIS ({word_count} palabras) ---')
print(content[:2000])
print('...' if len(content) > 2000 else '')
print('--- RESULTADO ---')
print('PASS' if word_count >= 200 else 'FAIL: análisis insuficiente')
"
```

**Criterio PASS V2:** análisis de 200+ palabras cubriendo los 6 puntos del prompt.

#### 2.4 Test V3 — Comparación con Huihui Vision (benchmark subjetivo)

Si Huihui Vision sigue disponible, correr el mismo prompt V1 contra el modelo actual
y comparar la riqueza descriptiva de ambas respuestas. No hay score automatizado —
evaluación visual del usuario.

```bash
# Arrancar Huihui Vision temporalmente para comparación
# (solo si el usuario quiere comparar antes de hacer el switch)
```

---

### Tarea 3 — Configuración de producción

Solo ejecutar si Tarea 2 pasa V1 y V2.

#### 3.1 Crear wrapper de arranque

```bash
cat > /home/asalazar/start-qwen25vl-vision.sh << 'EOF'
#!/bin/bash
exec /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf \
  --mmproj /home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf \
  --alias qwen25vl-vision \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 16384 \
  --n-gpu-layers N_CALIBRADO \
  --override-tensor ".*=CPU" \
  --flash-attn on \
  --jinja \
  --metrics \
  --slots \
  --slot-save-path /home/asalazar/llama-slots \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4
EOF

# Reemplazar N_CALIBRADO con el valor encontrado en Tarea 1.2
# Ejemplo: sed -i 's/N_CALIBRADO/30/' /home/asalazar/start-qwen25vl-vision.sh

chmod +x /home/asalazar/start-qwen25vl-vision.sh
```

#### 3.2 Actualizar llama-vision.service

```bash
sudo tee /etc/systemd/system/llama-vision.service << 'EOF'
[Unit]
Description=llama.cpp server - Qwen2.5-VL-32B Vision (nativa, abliterated, puerto 8012)
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar
ExecStart=/home/asalazar/start-qwen25vl-vision.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart llama-vision
sudo systemctl status llama-vision
```

#### 3.3 Actualizar switch-model.sh — agregar modo qwen25vl

El switch-model.sh actual tiene 6 modos: `ornstein`, `supergemma`, `trevorjs`, `vision`,
`qwen3`, `image`. El modo `vision` actualmente arranca `llama-vision.service` (que apuntará
al nuevo Qwen2.5-VL tras el paso 3.2).

Agregar adicionalmente un modo `vision-test` que permita arrancar el nuevo modelo en
puerto temporal **sin tocar el servicio vision de producción**, para que el usuario pueda
probarlo antes de hacer el switch definitivo.

```bash
# Hacer backup antes de modificar
cp /home/asalazar/switch-model.sh /home/asalazar/switch-model.sh.bak-story027

# Ver la sección de modos del switch actual para identificar dónde insertar
grep -n "vision\|qwen3\|ornstein" /home/asalazar/switch-model.sh | head -30
```

Agregar bloque `vision-test` en switch-model.sh (insertar antes del bloque `image`):

```bash
# Fragmento a agregar — adaptar al estilo del script existente:
#
# "vision-test")
#   echo "Arrancando Qwen2.5-VL-32B Vision TEST en puerto 8015..."
#   sudo systemctl stop llama-vision llama-ornstein llama-supergemma llama-trevorjs llama-qwen3 2>/dev/null
#   sleep 5
#   nohup /home/asalazar/llama.cpp/build/bin/llama-server \
#     --model /home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf \
#     --mmproj /home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf \
#     --alias qwen25vl-vision-test \
#     --host 0.0.0.0 --port 8015 \
#     --ctx-size 16384 --n-gpu-layers N_CALIBRADO \
#     --override-tensor ".*=CPU" --flash-attn on --jinja \
#     --threads 6 --threads-batch 6 --threads-http 4 \
#     > /home/asalazar/qwen25vl-test.log 2>&1 &
#   echo "Servidor vision-test en http://10.1.0.105:8015 — log: ~/qwen25vl-test.log"
#   ;;
```

> El modo `vision-test` usa puerto 8015 para no pisar el puerto 8012 de producción.
> Así el usuario puede probar el modelo en Open WebUI apuntando manualmente a 8015
> antes de aprobar el cambio definitivo en `llama-vision.service`.

---

### Tarea 4 — UAT manual por el usuario

**Esta tarea la ejecuta el usuario, no Codex.**

Una vez que Tarea 3 está completa y el modo `vision-test` está disponible:

1. Correr `~/switch-model.sh vision-test`
2. En Open WebUI: agregar conexión manual a `http://10.1.0.105:8015/v1` o usar la API directamente
3. Subir una imagen de referencia para el juego (ambiente, criatura, o referencia visual)
4. Prompt sugerido: *"Analiza esta imagen como director de arte para un videojuego survival horror. Describe composición, paleta de colores, iluminación, texturas y atmósfera."*
5. Comparar la riqueza descriptiva vs Huihui Vision anterior
6. Si el análisis es superior: confirmar switch definitivo → `~/switch-model.sh vision` (ya usa el nuevo servicio tras Tarea 3.2)

**Criterio de aprobación UAT:** el usuario confirma que la descripción visual es más rica,
más detallada y más útil para el pipeline creativo que la salida de Huihui Vision.

**Resultado UAT 2026-05-02:** FAIL. La calidad visual/descriptiva es muy buena, pero la
velocidad no es viable para producción. Se requiere al menos 2x más velocidad percibida antes
de aprobar un reemplazo.

---

## Criterios de aceptación

- [x] Tarea 0: GGUF (~20 GB) y mmproj (~0.8 GB) descargados y verificados
- [x] Tarea 1: arquitectura `qwen2vl` reconocida por llama.cpp actual
- [x] Tarea 1: `--n-gpu-layers` calibrado sin OOM en 12GB VRAM
- [x] Tarea 2 V1: descripción visual coherente de 100+ palabras (smoke test)
- [x] Tarea 2 V2: análisis art-director de 200+ palabras con ctx=16384
- [x] Tarea 3: `start-qwen25vl-vision.sh` creado con n-gpu-layers correcto
- [x] Tarea 3: `llama-vision.service` actualizado y reiniciado apuntando al nuevo modelo
- [x] Tarea 3: `switch-model.sh` actualizado con modo `vision-test` en puerto 8015
- [ ] Tarea 4: UAT manual aprobado por el usuario antes de considerar la story completada
- [x] Tarea 4: UAT manual ejecutado — FAIL por latencia; no aprobar para producción

---

## Al finalizar: actualizar memoria del proyecto

Registrar en `context/conversation_memory.md`:
- Decisión: Qwen2.5-VL-32B evaluado; calidad muy buena, pero rechazado para producción por latencia.
- Contexto: arquitectura nativa qwen2vl funciona, pero el modelo denso 32B genera demasiado lento en RTX 3060 12 GB.
- Impacto: se requiere buscar candidato alternativo de visión con al menos 2x más velocidad percibida.

Actualizar `context/project_state.md` tabla de modelos:
- No declarar Qwen2.5-VL-32B como backend definitivo sin resolver la latencia o revertir el servicio a Huihui Vision.

Actualizar `context/artifacts_registry.md` con nuevos artefactos del servidor.

Actualizar `context/stories/INDEX.md` con estado 🔴 o crear nueva story de búsqueda de alternativa rápida.

---

## Cierre — Sesión 22 (2026-05-02)

El objetivo de reemplazar Huihui Vision se cumplió con un modelo diferente al planificado.

**Modelo final adoptado:** `supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf` (kof1467)
- Arquitectura: Gemma 4 26B-A4B MoE — misma base que Ornstein/SuperGemma/TrevorJS
- Fuente: `kof1467/supergemma4-26b-abliterated-multimodal-gguf-4bit`
- Rutas: `~/models/supergemma4-vision/` (GGUF 16GB + mmproj 1.2GB + chat_template.jinja)
- Wrapper: `/home/asalazar/start-supergemma4-vision.sh`
- Servicio: `llama-vision.service` actualizado

**UAT resultado:** PASS — descripción visual estructurada en iluminación, composición y assets. Sin alucinaciones de IP. Prompt de imagen generado automáticamente.

**Limitación documentada:** thinking OFF obligatorio. llama.cpp b8998 emite los channel markers de Gemma 4 multimodal (`<channel|>`) como tokens en el output en lugar de separarlos en `reasoning_content`. Intentos fallidos: `enable_thinking:true` sin template, con chat_template.jinja customizado.

**Modelos descartados en el proceso:**
- Qwen2.5-VL-32B: calidad excelente, latencia ~1.46 tok/s — rechazado
- Huihui Vision: velocidad OK, alucinaciones de IP — rechazado
- Qwen2.5-VL-7B: velocidad OK, calidad pobre, sin thinking — rechazado
- Todos los archivos eliminados del servidor para liberar espacio
