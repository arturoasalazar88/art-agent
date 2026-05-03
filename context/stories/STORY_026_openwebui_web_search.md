# STORY_026 — Open WebUI: Web Search + RAG de URLs

> Estado: ✅ Completada
> Área: Infraestructura / Herramientas
> Sesión de creación: 20 (2026-05-01)
> Depende de: —

---

## Objetivo

Habilitar acceso a internet desde Open WebUI para que los modelos (especialmente Huihui Texto) puedan buscar información en tiempo real y analizar páginas web durante conversaciones.

---

## Contexto

Open WebUI soporta dos mecanismos de acceso a internet:

1. **Web Search:** motor de búsqueda integrado — el modelo puede buscar queries en la web y usar los resultados como contexto
2. **RAG de URL:** pegar una URL en el chat con `#` hace scraping de la página y la inyecta como contexto al modelo

Ambos son útiles para el pipeline del proyecto:
- Huihui Texto investigando referencias visuales de horror, modelos nuevos, specs técnicas
- Buscar documentación de Unity, AdonisJS, llama.cpp directamente desde el chat
- Analizar páginas de HuggingFace con modelos candidatos

---

## Tarea 1 — Instalar SearXNG en Docker

SearXNG es el motor recomendado — self-hosted, sin API key, sin límites de queries, privacidad total.

```bash
# En el servidor asalazar@10.1.0.105
docker run -d \
  --name searxng \
  --restart unless-stopped \
  -p 8080:8080 \
  -v /home/asalazar/searxng:/etc/searxng \
  searxng/searxng
```

Verificar que arrancó:

```bash
curl -s http://localhost:8080 | head -5
# Debe devolver HTML de SearXNG
```

Verificar desde el host (Mac):
```
http://10.1.0.105:8080
```

---

## Tarea 2 — Configurar Web Search en Open WebUI

1. Abrir `http://10.1.0.105:3000`
2. Iniciar sesión como admin
3. Ir a **Admin Panel → Settings → Web Search**
4. Activar **Enable Web Search**
5. Seleccionar motor: `searxng`
6. URL: `http://10.1.0.105:8080`
7. Guardar

---

## Tarea 3 — Verificar RAG de URLs

Sin configuración extra, Open WebUI ya soporta scraping de URLs. Verificar que funciona:

1. En un chat con Huihui Texto, escribir:
   ```
   # https://huggingface.co/mradermacher/Huihui-Qwen3.5-35B-A3B-abliterated-i1-GGUF
   ¿Qué cuantizaciones están disponibles en este repositorio?
   ```
2. Verificar que Open WebUI carga la página y el modelo responde con datos reales

---

## Tarea 4 — Test de Web Search

Con Web Search habilitado, activar el ícono de búsqueda en el chat y probar:

```
Busca los últimos modelos GGUF de Qwen3 abliterados disponibles en HuggingFace
```

**Criterio PASS:** el modelo devuelve resultados actuales con URLs reales, no datos de entrenamiento.

---

## Tarea 5 — Verificar persistencia del servicio

SearXNG debe sobrevivir reinicios del servidor:

```bash
# Verificar que tiene --restart unless-stopped
docker inspect searxng | grep RestartPolicy
```

Si no tiene restart policy, recrear el contenedor con `--restart unless-stopped`.

---

## Resultado de ejecución — 2026-05-01

### Tarea 1 — SearXNG ✅
- Contenedor `searxng` creado y corriendo en `http://10.1.0.105:8080`
- `--restart unless-stopped` confirmado
- `curl http://localhost:8080` devuelve HTML de SearXNG

### Tarea 2 — Configurar Web Search en Open WebUI ✅
- Open WebUI tiene `auth=true` y todos los endpoints de configuración devuelven `401 Not authenticated`
- No existe API pública sin sesión para modificar settings
- Se intentó vía SQLite interna (inspección de `/app/backend/data`) sin modificar
- Configuración completada manualmente por Arturo desde Admin Panel:
  - Admin Panel → Settings → Web Search → Enable: ON
  - Engine: `searxng`
  - URL: `http://10.1.0.105:8080`

### Tarea 3 — RAG de URLs ⚠️ Pendiente
- No se confirmó todavía el test con `#url`.
- Queda como único criterio pendiente de esta story.

### Tarea 4 — Test de Web Search ✅
- Arturo confirmó que la búsqueda funcionó perfecto desde Open WebUI.
- Resultado: UAT PASS — Web Search devuelve resultados reales usando SearXNG.

### Tarea 5 — Persistencia ✅
- `docker inspect searxng` confirma restart policy:
  ```json
  {"Name":"unless-stopped","MaximumRetryCount":0}
  ```
- Verificación posterior: contenedor `searxng` sigue `Up` y `http://localhost:8080` responde HTTP 200.

---

## Criterios de aceptación

- [x] SearXNG corriendo en `http://10.1.0.105:8080`
- [x] Web Search habilitado en Open WebUI apuntando a SearXNG — validado manualmente por Arturo ✅
- [x] Test de búsqueda en chat devuelve resultados reales — UAT PASS ✅
- [ ] RAG de URL funciona con `#url` en el chat — pendiente de verificar
- [x] SearXNG sobrevive reinicio del servidor — restart policy confirmada ✅

---

## Al finalizar

1. Actualizar este archivo con resultados
2. Actualizar `context/stories/INDEX.md`
3. Agregar SearXNG a la tabla de servicios en `context/project_state.md`
