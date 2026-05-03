# STORY_024 — Huihui Vision + Open WebUI Results

> Fecha: 2026-05-02
> Servidor: `asalazar@10.1.0.105`
> Modelo: `huihui-vision`
> Servicio: `llama-vision.service`
> Puerto: `8012`

---

## Resultado Oficial

```
STORY_024 RESULTADO:
- Health 8012: OK
- Test chat simple: PASS — content: **¡Hola!** This is the most common and versatile
- Test visión API: PASS — palabras: 347
- Open WebUI chat: FAIL
- Open WebUI visión: FAIL
- max_tokens issue: no
- Observaciones: Ejecutado por SSH. API de Huihui Vision funciona con always thinking y max_tokens=2048. Open WebUI responde HTTP 200 y apunta a http://127.0.0.1:8012/v1, pero la prueba UI quedó bloqueada porque auth=true, enable_api_keys=false, y los endpoints protegidos devuelven 401 Not authenticated sin sesión.
```

---

## Evidencia Técnica

### Health

`curl -s http://localhost:8012/health`

Resultado:

```json
{"status":"ok"}
```

### Chat Simple

Parámetros efectivos:

- `max_tokens=2048`
- `temperature=0.3`
- `chat_template_kwargs.enable_thinking=true`

Resultado:

- `content` no vacío
- `reasoning_content` presente
- PASS

Primer contenido:

```text
**¡Hola!**
```

### Visión API

Imagen de prueba usada:

```text
/home/asalazar/.cache/gnome-software/icons/93d4d0d4c7e2f702cbaac5908efd1ea970cb5ff9-gnome-logs_org.gnome.Logs.png
```

Resultado:

- Descripción coherente
- 347 palabras
- PASS

### Wrapper

Archivo revisado:

```text
/home/asalazar/start-huihui-vision.sh
```

Hallazgo:

- No contiene `--max-tokens`
- No contiene `--n-predict`
- No contiene `max_tokens`

Conclusión: el límite de salida lo controla el cliente/request. Para Huihui Vision usar `max_tokens >= 2048`.

### Open WebUI

Portal:

```text
http://10.1.0.105:3000
```

Estado:

- HTTP 200 en `/`
- Contenedor Docker activo: `open-webui`
- `OPENAI_API_BASE_URL=http://127.0.0.1:8012/v1`
- Desde el contenedor, `http://127.0.0.1:8012/health` responde OK

Bloqueo:

- `auth=true`
- `enable_api_keys=false`
- `/api/models`, `/ollama/api/tags` y `/openai/models` devuelven `401 Not authenticated`

Conclusión: Open WebUI está vivo y conectado al puerto correcto, pero la validación manual de chat/visión requiere una sesión autenticada en el navegador.

---

## Resultado de Codegen con Huihui Vision

Se probó un prompt de generación de código para evaluar capacidades de desarrollador con una función Python `build_asset_manifest(records)` y tests `unittest`.

Resultado observado:

- El modelo empezó con una respuesta extensa y verbosa.
- Produjo código parcial.
- La respuesta falló antes de terminar con:

```text
Context size has been exceeded.
```

Conclusión:

- `huihui-vision` no es buen candidato para evaluar codegen largo.
- Para tareas de ingeniería/codegen usar `llama-qwen3` en puerto `8013`.
- Para Huihui Vision, mantenerlo como backend de análisis visual.
- Si se evalúa código con Huihui de todos modos, usar prompt compacto, salida estricta, `always thinking`, `temperature=0.2` y `max_tokens` alto (`4096` o `6000`).

Prompt compacto recomendado para futuras pruebas:

```text
Implementa en Python 3.11 la función build_asset_manifest(records).

Entrada: list[dict]. Cada record puede tener:
id str obligatorio
type str obligatorio: texture|model|audio|script
path str obligatorio
size_bytes int opcional
tags list[str] opcional
dependencies list[str] opcional
metadata dict opcional

Salida JSON-serializable:
{
  "assets": [...],
  "by_type": {...},
  "dependency_graph": {...},
  "warnings": [...]
}

Reglas:
- Ignora records inválidos y agrega warning si falta id/type/path o type no es válido.
- Duplicados: conserva el primer id válido, warning para los siguientes.
- tags: lowercase, únicos, ordenados.
- path: reemplaza "\" por "/".
- dependency_graph: solo dependencias que apunten a ids válidos; warning para inexistentes.
- by_type: cuenta assets válidos.
- assets: ordenados por type y luego id.
- No mutar records originales.
- Incluye unittest con: válido normal, inválidos, duplicados, dependencia inexistente, normalización.

Responde SOLO con:
1. Código completo en un bloque Python.
2. Después, máximo 5 bullets: decisiones y complejidad.
No escribas introducción.
```

---

## Estado Final

STORY_024 queda bloqueada, no completada:

- API Huihui Vision: validada.
- Open WebUI manual: pendiente por autenticación de usuario.

Para desbloquear:

1. Abrir `http://10.1.0.105:3000`.
2. Iniciar sesión.
3. Crear chat con `huihui-vision`.
4. Enviar chat simple.
5. Adjuntar imagen JPG/PNG y pedir análisis visual.
6. Confirmar que el límite de salida no esté en 512.

---

## Cierre — 2026-05-02 (sesión 25)

✅ **Story cerrada como superada por STORY_027.**

Huihui Vision fue eliminado del servidor (D85). `llama-vision.service` ahora corre `supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf` — UAT PASS (D83). El objetivo original de tener un modelo de visión funcional en Open WebUI queda cubierto con el modelo de reemplazo.
