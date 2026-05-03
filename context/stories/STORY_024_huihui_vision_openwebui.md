# STORY_024 — Activar Huihui Vision en servidor y validar en Open WebUI

> Estado: ✅ Completada
> Área: Infraestructura / Validación
> Asignado a: Codex
> Sesión de creación: 18 (2026-05-01)
> Depende de: STORY_023 ✅

---

## Objetivo

Activar `llama-vision.service` (Huihui Vision con mmproj) en el servidor mediante `switch-model.sh vision` y verificar que Open WebUI puede chatear con el modelo y analizar imágenes.

---

## Contexto

STORY_023 completó la instalación y configuración de Huihui Vision:
- GGUF: `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf`
- mmproj: `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-mmproj-F16.gguf`
- Wrapper: `/home/asalazar/start-huihui-vision.sh`
- Servicio: `/etc/systemd/system/llama-vision.service`
- Puerto: 8012

Open WebUI corre en Docker en `http://10.1.0.105:3000` y apunta fijo al puerto 8012 — no requiere reconfiguración.

**Parámetro crítico:** `max_tokens` mínimo 2048. Con 512 el modelo agota tokens en `reasoning_content` y devuelve `content=""`. Verificar que Open WebUI no limita por defecto a 512.

---

## Tareas

### Tarea 1 — Activar modo visión

```bash
~/switch-model.sh vision
```

El script detiene cualquier modelo activo y levanta `llama-vision.service`.

Esperar ~60 segundos para que el modelo cargue, luego verificar health:

```bash
curl -s http://localhost:8012/health
# Esperado: {"status":"ok"}
```

Si el health no responde después de 90s, revisar logs:

```bash
journalctl -u llama-vision -n 50 --no-pager
```

Errores comunes:
- `CUDA out of memory` → el modelo anterior no se detuvo correctamente. Ejecutar `sudo systemctl stop llama-ornstein llama-supergemma llama-trevorjs llama-qwen3 2>/dev/null` y repetir.
- `model file not found` → verificar que los GGUFs existen en `/home/asalazar/models/huihui/`

---

### Tarea 2 — Test de chat simple (sin imagen)

Antes de probar visión, verificar que el modelo responde en modo texto:

```bash
curl -s http://localhost:8012/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Di hola en español en una frase corta."}],
    "max_tokens": 256,
    "temperature": 0.3,
    "chat_template_kwargs": {"enable_thinking": false}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message'].get('content', '')
reasoning = r['choices'][0]['message'].get('reasoning_content', '')
print('content:', content[:200])
print('reasoning presente:', bool(reasoning))
print('PASS' if len(content) > 5 else 'FAIL: content vacío')
"
```

**Criterio PASS:** `content` contiene texto, no está vacío.

Si `content=""` y `reasoning_content` tiene texto → el modelo está pensando con max_tokens insuficiente. Aumentar a 512 o 1024.

---

### Tarea 3 — Test de visión con imagen

Usar una imagen de prueba pequeña. Si hay alguna imagen en el servidor usarla; si no, descargar una:

```bash
# Opción A: usar imagen existente si la hay
ls ~/refs/images/ 2>/dev/null | head -5

# Opción B: descargar imagen de prueba pequeña
wget -q -O /tmp/test_vision.jpg \
  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Biome.jpg/320px-Biome.jpg" \
  || echo "descarga fallida — usar imagen local"

# Convertir a base64 y testear
IMAGE_B64=$(base64 -w 0 /tmp/test_vision.jpg)

curl -s http://localhost:8012/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/jpeg;base64,${IMAGE_B64}\"}},
          {\"type\": \"text\", \"text\": \"Describe esta imagen: composición, colores dominantes, mood y elementos visuales notables.\"}
        ]
      }
    ],
    \"max_tokens\": 2048,
    \"temperature\": 0.3,
    \"chat_template_kwargs\": {\"enable_thinking\": false}
  }" | python3 -c "
import sys, json
r = json.load(sys.stdin)
if 'error' in r:
    print('ERROR:', r['error'])
    sys.exit(1)
content = r['choices'][0]['message'].get('content', '')
word_count = len(content.split())
print('--- DESCRIPCIÓN ---')
print(content[:600])
print('---')
print(f'Palabras: {word_count}')
print('PASS' if word_count >= 30 else 'FAIL: descripción muy corta o vacía')
"
```

**Criterio PASS:** descripción coherente con al menos 30 palabras.

---

### Tarea 4 — Verificar max_tokens en Open WebUI

Antes de abrir Open WebUI, verificar la configuración por defecto del servidor para max_tokens:

```bash
# Ver la config del servicio
cat /home/asalazar/start-huihui-vision.sh
# Verificar que NO tiene --max-tokens o que el valor sea >= 2048
```

Si el wrapper no tiene `--max-tokens` hardcodeado, Open WebUI puede enviarlo como parámetro en cada request — verificar en la UI en Settings > Model Parameters que el límite no está en 512.

---

### Tarea 5 — Prueba manual en Open WebUI

Abrir `http://10.1.0.105:3000` en el navegador.

**Test A — chat de texto:**
1. Abrir un chat nuevo
2. Verificar que el modelo activo es `huihui-vision` (o el alias configurado)
3. Enviar: "Hola, ¿puedes describir imágenes?"
4. Verificar respuesta coherente

**Test B — análisis de imagen:**
1. En el chat, subir cualquier imagen (JPG/PNG)
2. Preguntar: "Describe la composición, los colores y el mood de esta imagen"
3. Verificar que la respuesta analiza la imagen (no ignora el adjunto)

**Criterio PASS Open WebUI:** el modelo responde en ambos tests con contenido relevante.

---

### Tarea 6 — Reportar resultados

Al terminar, reportar:

```
STORY_024 RESULTADO:
- Health 8012: [OK/FAIL]
- Test chat simple: [PASS/FAIL] — content: [primeras 50 chars]
- Test visión API: [PASS/FAIL] — palabras: [N]
- Open WebUI chat: [PASS/FAIL]
- Open WebUI visión: [PASS/FAIL]
- max_tokens issue: [sí/no]
- Observaciones: [cualquier comportamiento inesperado]
```

---

## Criterios de aceptación

- [x] `llama-vision.service` arranca sin errores
- [x] Health OK en puerto 8012
- [x] Chat de texto responde con `content` no vacío
- [x] Análisis de imagen devuelve descripción ≥ 30 palabras
- [ ] Open WebUI puede chatear con el modelo
- [ ] Open WebUI puede analizar una imagen adjunta

---

## Al finalizar

Actualizar este archivo con los resultados y marcar estado en `context/stories/INDEX.md`.

Si Open WebUI funciona correctamente con visión, el rol de análisis de referencias visuales (STORY_005, STORY_006) queda desbloqueado con Huihui Vision como herramienta.

---

## Resultado de ejecución — 2026-05-02

```
STORY_024 RESULTADO:
- Health 8012: OK
- Test chat simple: PASS — content: **¡Hola!**
- Test visión API: PASS — palabras: 347
- Open WebUI chat: FAIL
- Open WebUI visión: FAIL
- max_tokens issue: no
- Observaciones: Se ejecutó todo por SSH. `~/switch-model.sh vision` reportó `vision activo`, aunque mostró errores de sudo no interactivo al intentar detener/iniciar servicios. El health quedó OK. Los tests API usaron `chat_template_kwargs.enable_thinking=true` por decisión del usuario y `max_tokens=2048`. El wrapper `/home/asalazar/start-huihui-vision.sh` no tiene `--max-tokens`, `--n-predict` ni `max_tokens` hardcodeado. Open WebUI responde HTTP 200 y el contenedor `open-webui` está activo; `OPENAI_API_BASE_URL=http://127.0.0.1:8012/v1`, y desde el contenedor el health de 8012 responde OK. La prueba manual/API de Open WebUI quedó bloqueada porque `auth=true`, `enable_api_keys=false`, y `/api/models`, `/ollama/api/tags` y `/openai/models` devuelven `401 Not authenticated` sin sesión de usuario.
```

### Bloqueo (superado)

La story quedó bloqueada por auth de Open WebUI con Huihui Vision. Sin embargo, **STORY_027 resolvió el problema de raíz**: Huihui Vision fue reemplazado por `supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf` en `llama-vision.service`, y ese modelo pasó UAT de visión (D83). Huihui Vision fue eliminado del servidor junto con sus GGUFs. La validación de Open WebUI con el modelo de visión actual corre por cuenta de STORY_027 ✅.

**Marcada como completada en sesión 25 — 2026-05-02. Objetivo cubierto por STORY_027.**
