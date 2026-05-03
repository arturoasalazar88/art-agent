# STORY_028 — Huihui Claude 4.7 Upgrade: Validar sucesor directo de Huihui Texto

> Estado: ✅ Completada
> Área: Infraestructura / Modelos
> Desarrollada por: El Ingeniero (sesión 24, 2026-05-02)
> Sesión de creación: 21 (2026-05-01)
> Depende de: STORY_025 ✅

---

## Objetivo

Validar `Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated` como reemplazo de **dos modelos**:

1. **Huihui 4.6** (eliminado en D85) — modelo de razonamiento conversacional. Misma suite UAT de STORY_025.
2. **Qwen3.6-35B-A3B base** (puerto 8013, activo) — modelo de ingeniería/codegen. El base puro es censurado; Huihui 4.7 es abliterated sobre la misma base Qwen3.6. **Goal del reemplazo: mismo performance de ingeniería + misma ventana de contexto (ctx=40,960) pero sin censura.** Si mantiene la calidad en los tests de ingeniería a ctx largo, consolida ambos roles.

**Resultado esperado si PASS completo:** un solo modelo uncensored cubre razonamiento conversacional + ingeniería + codegen a ctx=40,960. Se elimina el servicio `llama-qwen3` (puerto 8013) y se libera ~20GB de disco.

---

## Por qué este modelo

| Atributo | Actual (Claude 4.6) | Objetivo (Claude 4.7) |
|---|---|---|
| Base | Qwen3.5-35B-A3B | Qwen3.6-35B-A3B |
| Destilado de | Claude 4.6 Opus | Claude 4.7 Opus |
| Abliterado por | huihui-ai | huihui-ai |
| Arquitectura | qwen35moe | qwen36moe (misma familia) |
| GGUF uploader | cesarsal1nas | whoya |
| Cuantización | Q4_K_M | Q5_K_M disponible |
| Hardware requerido | igual | igual |

El único cambio es la fuente de destilación (4.6 → 4.7) y la base (Qwen3.5 → Qwen3.6).
Mismo hardware, mismos parámetros de arranque, misma suite de validación.

---

## Modelo objetivo

| Campo | Valor |
|---|---|
| Nombre | Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated |
| GGUF repo | `whoya/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M-GGUF` |
| Abliterado por | huihui-ai |
| Cuantización disponible | Q5_K_M (~27 GB) |
| Arquitectura | qwen36moe (familia Qwen3 MoE) |
| Params totales / activos | 35B / ~3B activos por token |
| llama.cpp compatible | ✅ misma familia arquitectural |
| `--n-cpu-moe` | ✅ mismo flag que el modelo actual |

> **Nota sobre cuantización:** Solo Q5_K_M confirmado en el repo de whoya. Si existe
> Q4_K_M del mismo modelo en otro uploader (bartowski, mradermacher), preferirlo para
> ahorrar ~7 GB. Verificar en HuggingFace antes de descargar.

---

## Rutas en servidor

| Recurso | Ruta |
|---|---|
| Directorio destino | `/home/asalazar/models/huihui47/` |
| GGUF objetivo | `/home/asalazar/models/huihui47/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M.gguf` |
| GGUF modelo actual | `/home/asalazar/models/huihui/Huihui-Qwen3.5-35B-A3B-Claude-4.6-Opus-abliterated-Q4_K_M.gguf` |
| Wrapper texto actual | `/home/asalazar/start-huihui-vision.sh` |
| Servicio vision | `/etc/systemd/system/llama-vision.service` |
| Script switch | `/home/asalazar/switch-model.sh` |

---

## Tareas

### Tarea 0 — Verificar espacio y descargar

#### 0.1 Verificar espacio disponible

```bash
df -h /home/asalazar/
# Necesario: ~28 GB para Q5_K_M (~27 GB + margen)
# Si solo hay espacio para Q4_K_M, buscar variante Q4_K_M primero
```

#### 0.2 Verificar disponibilidad de cuantizaciones en HuggingFace

Antes de descargar, verificar si existe Q4_K_M de algún uploader:

```bash
# Buscar en HuggingFace (manual o via API):
# - bartowski/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-GGUF
# - mradermacher/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-GGUF
# Si existe Q4_K_M (~20 GB), preferirlo sobre Q5_K_M
```

#### 0.3 Crear directorio y descargar

```bash
mkdir -p /home/asalazar/models/huihui47/

# Q5_K_M desde whoya (ajustar nombre de archivo según HuggingFace)
wget -c "https://huggingface.co/whoya/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M-GGUF/resolve/main/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M.gguf" \
  -O /home/asalazar/models/huihui47/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M.gguf
```

> IMPORTANTE: Verificar el nombre exacto del archivo en HuggingFace antes de ejecutar.
> Usar `-c` para reanudar descargas interrumpidas.

#### 0.4 Verificar integridad

```bash
ls -lh /home/asalazar/models/huihui47/
# Q5_K_M debe ser ~27 GB
# Si es 0 bytes o notoriamente más pequeño, descarga fallida
```

---

### Tarea 1 — Verificar compatibilidad de arquitectura

```bash
# Detener cualquier modelo activo en 8012
sudo systemctl stop llama-vision 2>/dev/null
sleep 5

# Arranque mínimo — verificar que qwen36moe carga en el build actual
/home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui47/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M.gguf \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --port 8014 \
  --ctx-size 4096 \
  --jinja 2>&1 | head -50
```

**Interpretar output:**
- ✅ CONTINUAR si: `model loaded`, `server is listening`, o carga de tensores visible
- ❌ DETENER si: `unknown model architecture`, `unsupported model type`

Si falla por arquitectura: el build actual no soporta qwen36moe — reportar y cerrar.
La solución sería actualizar llama.cpp, pero no compilar en esta story.

```bash
# Matar proceso de prueba
pkill -f "llama-server.*huihui47" 2>/dev/null
sleep 5
```

---

### Tarea 2 — Suite de validación (espejo de STORY_025 UAT)

Arrancar en modo texto (sin mmproj), mismos parámetros que el modelo actual.

#### 2.1 Arrancar servidor

```bash
nohup /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui47/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M.gguf \
  --alias huihui47-text \
  --host 0.0.0.0 \
  --port 8014 \
  --ctx-size 32768 \
  --n-gpu-layers 99 \
  --n-cpu-moe 99 \
  --flash-attn on \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --jinja \
  --threads 6 \
  --threads-batch 6 \
  --threads-http 4 \
  > /home/asalazar/huihui47-text.log 2>&1 &

sleep 90
curl -s http://localhost:8014/health
```

#### 2.2 T1 — Lógica (espejo UAT-1 de STORY_025)

```bash
curl -s http://localhost:8014/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui47-text",
    "messages": [
      {
        "role": "system",
        "content": "Eres un asistente experto. Responde siempre en español."
      },
      {
        "role": "user",
        "content": "Hay tres cajas. Una contiene solo manzanas, otra solo naranjas, y otra contiene ambas. Las tres etiquetas están mal puestas. Solo puedes sacar una fruta de una caja sin ver su interior. ¿De qué caja sacas la fruta y cómo determinas el contenido de las tres cajas?"
      }
    ],
    "max_tokens": 2048,
    "temperature": 0.3,
    "chat_template_kwargs": {"enable_thinking": true}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content']
words = len(content.split())
print(f'--- T1 LÓGICA ({words} palabras) ---')
print(content[:1500])
print('--- RESULTADO ---')
print('PASS' if words >= 80 else 'FAIL: respuesta muy corta')
"
```

**Criterio PASS T1:** razonamiento correcto, respuesta en español, 80+ palabras.

#### 2.3 T2 — Arquitectura de sistema (espejo UAT-2 de STORY_025)

```bash
curl -s http://localhost:8014/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui47-text",
    "messages": [
      {
        "role": "system",
        "content": "Eres un arquitecto de software senior. Responde siempre en español."
      },
      {
        "role": "user",
        "content": "Diseña un sistema de inventario para un videojuego con: items apilables y no apilables, equipamiento con slots, combinación de items, serialización para guardado, y manejo de edge cases como stacks corruptos o dependencias circulares. Dame la arquitectura completa con interfaces TypeScript."
      }
    ],
    "max_tokens": 4096,
    "temperature": 0.3,
    "chat_template_kwargs": {"enable_thinking": true}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content']
words = len(content.split())
has_ts = 'interface' in content.lower() or 'type ' in content.lower() or 'class ' in content.lower()
print(f'--- T2 ARQUITECTURA ({words} palabras) ---')
print(content[:2000])
print('--- RESULTADO ---')
print('PASS' if words >= 300 and has_ts else f'FAIL: words={words}, typescript={has_ts}')
"
```

**Criterio PASS T2:** diseño con TypeScript, 300+ palabras, cubre al menos 4 de los 6 requisitos.

#### 2.4 T3 — Multi-turn con estado (espejo UAT-3 de STORY_025)

```bash
# Turno 1
RESPONSE1=$(curl -s http://localhost:8014/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui47-text",
    "messages": [
      {"role": "system", "content": "Responde siempre en español."},
      {"role": "user", "content": "Estoy pensando en un número entre 1 y 100. Adivínalo haciendo preguntas de sí/no. Primera pregunta."}
    ],
    "max_tokens": 512,
    "temperature": 0.3,
    "chat_template_kwargs": {"enable_thinking": true}
  }')

echo "--- TURNO 1 ---"
echo $RESPONSE1 | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['choices'][0]['message']['content'])"

# Turno 2 — responder a la pregunta del modelo
RESPONSE2=$(curl -s http://localhost:8014/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui47-text",
    "messages": [
      {"role": "system", "content": "Responde siempre en español."},
      {"role": "user", "content": "Estoy pensando en un número entre 1 y 100. Adivínalo haciendo preguntas de sí/no. Primera pregunta."},
      {"role": "assistant", "content": "¿El número es mayor que 50?"},
      {"role": "user", "content": "Sí, es mayor que 50."}
    ],
    "max_tokens": 512,
    "temperature": 0.3,
    "chat_template_kwargs": {"enable_thinking": true}
  }')

echo "--- TURNO 2 ---"
echo $RESPONSE2 | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['choices'][0]['message']['content'])"

# Turno 3 — verificar que mantiene el rango correcto (51-100)
RESPONSE3=$(curl -s http://localhost:8014/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui47-text",
    "messages": [
      {"role": "system", "content": "Responde siempre en español."},
      {"role": "user", "content": "Estoy pensando en un número entre 1 y 100. Adivínalo haciendo preguntas de sí/no. Primera pregunta."},
      {"role": "assistant", "content": "¿El número es mayor que 50?"},
      {"role": "user", "content": "Sí, es mayor que 50."},
      {"role": "assistant", "content": "¿El número es mayor que 75?"},
      {"role": "user", "content": "No, no es mayor que 75."}
    ],
    "max_tokens": 512,
    "temperature": 0.3,
    "chat_template_kwargs": {"enable_thinking": true}
  }')

echo "--- TURNO 3 ---"
echo $RESPONSE3 | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content']
print(content)
# Verificar que el modelo acotó correctamente el rango a 51-75
correct_range = '51' in content and '75' in content
print('PASS: rango 51-75 preservado' if correct_range else 'WARN: verificar manualmente si el rango es correcto')
"
```

**Criterio PASS T3:** el modelo mantiene búsqueda binaria óptima y preserva el rango correcto entre turnos.

#### 2.5 T4 — Extracción JSON estructurado (espejo T1 de STORY_021)

```bash
curl -s http://localhost:8014/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui47-text",
    "messages": [
      {
        "role": "system",
        "content": "Eres un extractor de datos. Responde SOLO con JSON válido, sin texto adicional."
      },
      {
        "role": "user",
        "content": "Extrae los datos de este texto y devuelve un JSON con los campos: nombre, edad, ciudad, profesion.\n\nTexto: María González tiene 34 años, trabaja como ingeniera de software y vive en Ciudad de México desde hace 5 años."
      }
    ],
    "max_tokens": 512,
    "temperature": 0.1,
    "chat_template_kwargs": {"enable_thinking": false}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content'].strip()
print('--- T4 JSON EXTRACTION ---')
print(content)
try:
    parsed = json.loads(content)
    has_fields = all(k in parsed for k in ['nombre','edad','ciudad','profesion'])
    print('PASS' if has_fields else 'FAIL: faltan campos')
except:
    print('FAIL: JSON inválido')
"
```

**Criterio PASS T4:** JSON válido con los 4 campos correctos, sin texto extra.

#### 2.6 T5 — Codegen (espejo T3 de STORY_021)

```bash
curl -s http://localhost:8014/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "huihui47-text",
    "messages": [
      {
        "role": "system",
        "content": "Eres un experto en TypeScript. Responde solo con código, sin explicaciones."
      },
      {
        "role": "user",
        "content": "Implementa una función TypeScript `debounce<T extends (...args: any[]) => any>(fn: T, delay: number): T` que retrase la ejecución hasta que pasen `delay` ms sin llamadas. Incluye el tipo de retorno correcto y manejo del timer."
      }
    ],
    "max_tokens": 1024,
    "temperature": 0.2,
    "chat_template_kwargs": {"enable_thinking": true}
  }' | python3 -c "
import sys, json
r = json.load(sys.stdin)
content = r['choices'][0]['message']['content']
words = len(content.split())
has_ts = 'function debounce' in content or 'const debounce' in content
has_timer = 'setTimeout' in content and 'clearTimeout' in content
print(f'--- T5 CODEGEN ({words} palabras) ---')
print(content[:1500])
print('--- RESULTADO ---')
print('PASS' if has_ts and has_timer else f'FAIL: debounce={has_ts}, timer={has_timer}')
"
```

**Criterio PASS T5:** implementación correcta con `setTimeout`/`clearTimeout`, tipos TypeScript.

#### 2.7 T4 y T5 a ctx largo — validar ventana de contexto (crítico para reemplazo de Qwen3)

Los tests T4 y T5 se corren a ctx=4096 (baseline) y luego a ctx=32768 con un bloque de relleno de ~28k tokens antes del prompt real. El modelo debe mantener el mismo resultado independientemente del contexto acumulado — esto es lo que valida que puede reemplazar a Qwen3 en tareas de ingeniería con contexto largo.

```bash
# Generar relleno de ~28k tokens para el test needle-in-haystack
PADDING=$(python3 -c "print('La siguiente información es contexto de relleno. ' * 700)")

# Repetir T4 y T5 con el padding insertado como primer mensaje de usuario antes del prompt real
# (misma estructura curl, agregar {"role":"user","content":"$PADDING"},{"role":"assistant","content":"Entendido."} antes del prompt)
```

#### 2.8 Registrar resultados

| Test | Rol validado | ctx baseline | ctx 32k | Notas |
|---|---|---|---|---|
| T1 Lógica | Conversacional | | — | |
| T2 Arquitectura | Conversacional + Ingeniería | | — | |
| T3 Multi-turn | Conversacional | | — | |
| T4 JSON Extraction | Ingeniería (Qwen3) | | ✓ requerido | |
| T5 Codegen TypeScript | Ingeniería (Qwen3) | | ✓ requerido | |

---

### Tarea 3 — Configuración de producción (solo si T1+T2+T3 PASS)

#### 3.1 Crear wrapper

```bash
cat > /home/asalazar/start-huihui47-text.sh << 'EOF'
#!/bin/bash
exec /home/asalazar/llama.cpp/build/bin/llama-server \
  --model /home/asalazar/models/huihui47/Huihui-Qwen3.6-35B-A3B-Claude-4.7-Opus-abliterated-Q5_K_M.gguf \
  --alias huihui47-text \
  --host 0.0.0.0 \
  --port 8012 \
  --ctx-size 32768 \
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
  --threads-batch 6 \
  --threads-http 4
EOF

chmod +x /home/asalazar/start-huihui47-text.sh
```

#### 3.2 Agregar modo huihui47 a switch-model.sh

```bash
# Backup antes de modificar
cp /home/asalazar/switch-model.sh /home/asalazar/switch-model.sh.bak-story028

# Ver estructura actual del switch para identificar dónde insertar
grep -n "vision\|qwen3\|ornstein\|case\|esac" /home/asalazar/switch-model.sh | head -40
```

Agregar modo `huihui47` al switch siguiendo el estilo existente. El modo arranca el nuevo
modelo en puerto 8012 (reemplaza vision/texto). El modo `vision` existente sigue apuntando
a `llama-vision.service` (Qwen2.5-VL tras STORY_027).

```
# Fragmento a insertar (adaptar al estilo del script):
# "huihui47")
#   echo "Arrancando Huihui Claude 4.7 texto en puerto 8012..."
#   sudo systemctl stop llama-vision llama-ornstein llama-supergemma llama-trevorjs 2>/dev/null
#   sleep 5
#   nohup /home/asalazar/start-huihui47-text.sh > /home/asalazar/huihui47.log 2>&1 &
#   echo "Servidor huihui47 en http://10.1.0.105:8012"
#   ;;
```

---

### Tarea 4 — UAT manual por el usuario

**Esta tarea la ejecuta el usuario, no Codex.**

1. Correr `~/switch-model.sh huihui47`
2. En Open WebUI: usar el modelo en puerto 8012
3. Hacer una conversación de razonamiento complejo o diseño de sistema
4. Comparar con el Huihui 4.6 actual
5. Si la calidad es igual o mejor: confirmar como nuevo modelo de razonamiento conversacional

---

## Criterios de aceptación

- [x] Tarea 0: GGUF descargado — Q4_K_M mradermacher (21.3 GB, 20GB en disco)
- [x] Tarea 1: arquitectura qwen35moe carga correctamente en llama.cpp b8998
- [x] Tarea 2: T1 Lógica PASS — 248 palabras, español, razonamiento completo
- [x] Tarea 2: T2 Arquitectura PASS — 2551 palabras, TypeScript completo con interfaces. max_tokens=8192 requerido (thinking consume ~3k tokens)
- [x] Tarea 2: T3 Multi-turn PASS — búsqueda binaria óptima, rango 51-75 preservado correctamente
- [x] Tarea 2: T4 JSON Extraction PASS a ctx baseline y ctx=32k — JSON válido con 4 campos, thinking OFF respetado
- [x] Tarea 2: T5 Codegen PASS a ctx baseline y ctx=32k — debounce TypeScript con setTimeout/clearTimeout + .cancel() bonus
- [x] Tarea 3: wrapper `start-huihui47-text.sh` creado
- [x] Tarea 3: modo `sage` agregado a `switch-model.sh` (nombre final: sage — razonador potente sin censura)
- [x] Tarea 3: servicio `llama-huihui47.service` creado y operativo en puerto 8012
- [ ] Tarea 3 (pendiente usuario): `llama-qwen3.service` detenido y deshabilitado, modelos Qwen3 eliminados (~20GB liberados)
- [ ] Tarea 4: UAT manual aprobado por el usuario

---

## Al finalizar: actualizar memoria del proyecto

Registrar en `context/conversation_memory.md`:
- Decisión: Huihui Claude 4.7 adoptado (o rechazado) como modelo de razonamiento conversacional
- Contexto: sucesor directo del 4.6, misma arquitectura MoE, distilación actualizada
- Impacto: si adoptado, actualizar tabla de modelos en `project_state.md`

Actualizar `context/stories/INDEX.md` y `context/artifacts_registry.md`.
