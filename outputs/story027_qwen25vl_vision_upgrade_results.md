# STORY_027 — Qwen2.5-VL Vision Upgrade Results

> Fecha: 2026-05-02
> Estado: Tareas 0-3 completadas. Tarea 4 / UAT UI ejecutada y rechazada por latencia.
> Servidor: `asalazar@10.1.0.105`

---

## Resumen

Qwen2.5-VL-32B-Instruct-abliterated fue descargado, cargado exitosamente con la
arquitectura `qwen2vl`, calibrado en RTX 3060 12 GB, validado vía API con dos
tests de visión y configurado como backend de `llama-vision.service` en puerto
8012.

Tarea 4 fue ejecutada manualmente por el usuario en Open WebUI. Resultado: FAIL por latencia.
El modelo funciona técnicamente y la calidad descriptiva es muy buena, pero no es viable para
producción en el hardware actual.

---

## Tarea 0 — Descarga e integridad básica

### Filenames verificados en HuggingFace

Repo: `mradermacher/Qwen2.5-VL-32B-Instruct-abliterated-GGUF`

Archivos exactos usados:

| Recurso | Filename remoto | Ruta local |
|---|---|---|
| Modelo Q4_K_M | `Qwen2.5-VL-32B-Instruct-abliterated.Q4_K_M.gguf` | `/home/asalazar/models/qwen25vl/Qwen2.5-VL-32B-Instruct-abliterated-Q4_K_M.gguf` |
| mmproj Q8_0 | `Qwen2.5-VL-32B-Instruct-abliterated.mmproj-Q8_0.gguf` | `/home/asalazar/models/qwen25vl/mmproj-Q8_0.gguf` |

### Tamaños finales

| Archivo | Tamaño humano | Bytes |
|---|---:|---:|
| GGUF Q4_K_M | 19G | 19851336736 |
| mmproj Q8_0 | 701M | 734862560 |

Espacio libre final en `/home/asalazar`: 23G.

Resultado: PASS.

---

## Tarea 1 — Compatibilidad y calibración

### Compatibilidad de arquitectura

El build actual de llama.cpp reconoció correctamente el modelo.

Evidencia del log:

```text
build_info: b8998-2098fd616
general.architecture = qwen2vl
arch = qwen2vl
model type = 32B
model params = 32.76 B
model loaded
server is listening on http://127.0.0.1:8012
```

Resultado: PASS.

### Calibración de `--n-gpu-layers`

Pruebas ejecutadas con `--ctx-size 8192`, `--override-tensor ".*=CPU"` y
mmproj Q8_0.

| n-gpu-layers | Resultado | VRAM usada aprox. | VRAM libre aprox. |
|---:|---|---:|---:|
| 30 | PASS | 3418 MiB | 8623 MiB |
| 40 | PASS | 3748 MiB | 8293 MiB |
| 50 | PASS | 4074 MiB | 7967 MiB |
| 60 | PASS | 4404 MiB | 7637 MiB |
| 64 | PASS | 4534 MiB | 7507 MiB |

Valor calibrado final: `--n-gpu-layers 64`.

Resultado: PASS.

---

## Tarea 2 — Validación de visión por API

Servidor arrancado para validación:

```text
alias: qwen25vl-vision
host: 0.0.0.0
port: 8012
ctx-size: 16384
n-gpu-layers: 64
override-tensor: ".*=CPU"
flash-attn: on
```

Health:

```json
{"status":"ok"}
```

Imagen de prueba: `/tmp/story027_test.jpg`

Propiedades:

```text
JPEG, 1200x900, 183K
```

### V1 — Smoke test visual

Prompt: descripción detallada de composición, paleta, iluminación, texturas y mood.

Resultado:

| Métrica | Valor |
|---|---:|
| Palabras | 609 |
| Criterio mínimo | 100+ palabras y 3+ categorías visuales |
| Estado | PASS |

Excerpt:

```text
This image is a stunning aerial view of a coastal landscape, showcasing a
harmonious blend of natural elements. Here is a detailed description of its
composition, color palette, lighting, textures, and emotional mood...
```

Timing reportado por llama.cpp:

```text
prompt eval time = 16919.96 ms / 1417 tokens (83.75 tokens per second)
eval time = 538962.66 ms / 789 tokens (1.46 tokens per second)
total time = 555882.61 ms / 2206 tokens
```

### V2 — Análisis art director

Prompt: análisis como director de arte para videojuego survival horror, cubriendo
6 puntos: composición, paleta con hex, iluminación, texturas, atmósfera y assets.

Resultado:

| Métrica | Valor |
|---|---:|
| Palabras | 569 |
| Criterio mínimo | 200+ palabras y cobertura de los 6 puntos |
| Estado | PASS |

Excerpt:

```text
The composition of the image is dynamic and draws the viewer's eye in a natural
flow. The rule of thirds is effectively utilized...
```

Resultado Tarea 2: PASS.

---

## Tarea 3 — Configuración de producción

### Wrapper creado

Archivo:

```text
/home/asalazar/start-qwen25vl-vision.sh
```

Parámetros clave:

```text
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
```

`bash -n` PASS.

### systemd actualizado

Archivo:

```text
/etc/systemd/system/llama-vision.service
```

Backup:

```text
/etc/systemd/system/llama-vision.service.bak-story027
```

Estado actual:

```text
Active: active (running)
ExecStart=/home/asalazar/start-qwen25vl-vision.sh
Health: {"status":"ok"}
```

VRAM con servicio final activo:

```text
6550 MiB used, 5491 MiB free
```

### switch-model.sh actualizado

Archivo:

```text
/home/asalazar/switch-model.sh
```

Backup:

```text
/home/asalazar/switch-model.sh.bak-story027
```

Nuevo modo:

```text
vision-test
```

Puerto:

```text
8015
```

`bash -n` PASS.

Resultado Tarea 3: PASS.

---

## Estado actual

`llama-vision.service` ya apunta a Qwen2.5-VL-32B en puerto 8012.

```text
http://10.1.0.105:8012/v1
model alias: qwen25vl-vision
```

Modo temporal disponible para UI/UAT:

```bash
~/switch-model.sh vision-test
```

Esto arranca Qwen2.5-VL en:

```text
http://10.1.0.105:8015/v1
model alias: qwen25vl-vision-test
log: /home/asalazar/qwen25vl-test.log
```

---

## Tarea 4 — UAT UI

Ejecutado manualmente por el usuario en Open WebUI el 2026-05-02.

### Resultado

FAIL.

### Motivo

La respuesta visual funciona y la calidad es muy buena, pero la latencia percibida es excesiva
para uso de producción. El usuario determinó que la experiencia UI no es viable.

### Evidencia relevante

- API V1 generó 609 palabras, pero a ~1.46 tok/s.
- API V1 tardó ~555.9s para 789 tokens generados.
- En UI, la respuesta comenzó correctamente pero la velocidad fue demasiado lenta para el flujo esperado.
- El cuello de botella es generación textual del modelo denso 32B, no el procesamiento de imagen.

### Criterio actualizado

El próximo candidato de visión debe ser al menos 2x más rápido en velocidad percibida.
Objetivo técnico provisional: >=3 tok/s o reducir la latencia de una descripción visual típica
al menos 50% frente a Qwen2.5-VL-32B en RTX 3060 12 GB.

### Conclusión

Qwen2.5-VL-32B queda documentado como técnicamente funcional y de alta calidad descriptiva, pero
rechazado para producción por velocidad. Buscar alternativa más rápida antes de adoptarlo como
backend definitivo.

---

## Observaciones operativas

- Qwen2.5-VL funciona correctamente con el build actual; no requiere recompilar.
- El modelo es denso 32B y genera demasiado lento para prod: V1 midió ~1.46 tok/s.
- La etapa de visión/image processing fue rápida: imagen procesada en ~9.6s en V1.
- El cuello principal es generación textual, no encoding visual.
- `--n-gpu-layers 64` no produjo OOM y deja margen amplio de VRAM.
- UAT UI rechazó el modelo por latencia, no por calidad; no promover como solución final de visión.
