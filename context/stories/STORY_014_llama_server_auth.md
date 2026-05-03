---
id: STORY_014
title: Autenticación --api-key en llama-server
status: pending
priority: low
created: 2026-04-29
updated: 2026-05-02
depends_on: —
---

# STORY_014 — Autenticación API Key en llama-server

Los servicios llama-server actuales están expuestos sin autenticación en la red local. Esta story agrega autenticación via `--api-key` para proteger los endpoints de inferencia.

---

## Objetivo

Configurar `--api-key` en todos los servicios llama-server activos y actualizar los clientes (Open WebUI, scripts de validación, pipeline) para usar la key.

---

## Servicios a proteger

| Servicio | Puerto | Archivo de servicio |
|---|---|---|
| llama-ornstein | 8012 | `/etc/systemd/system/llama-ornstein.service` |
| llama-supergemma | 8012 | `/etc/systemd/system/llama-supergemma.service` |
| llama-trevorjs | 8012 | `/etc/systemd/system/llama-trevorjs.service` |
| llama-vision | 8012 | `/etc/systemd/system/llama-vision.service` |
| llama-huihui47 (Sage) | 8012 | `/etc/systemd/system/llama-huihui47.service` |
| llama-qwen3 | 8013 | `/etc/systemd/system/llama-qwen3.service` |

---

## Implementación

1. Generar una API key segura: `openssl rand -hex 32`
2. Agregar `--api-key <key>` a los wrappers de arranque (`start-ornstein.sh`, `start-supergemma4-vision.sh`, etc.)
3. Guardar la key en `/home/asalazar/.llama_api_key` con permisos 600
4. Actualizar Open WebUI: Admin → Connections → API Key
5. Actualizar scripts de validación (runners, pipeline) para incluir `Authorization: Bearer <key>`
6. Actualizar `switch-model.sh` si hace health checks

---

## Criterios de aceptación

- [ ] Todos los servicios arrancados con `--api-key`
- [ ] Request sin key devuelve 401
- [ ] Open WebUI conecta correctamente con la key configurada
- [ ] Runners de validación (`orn_runner.py`, `qwen3_runner.py`, etc.) actualizados
- [ ] Key almacenada de forma segura (no en texto plano en los archivos de servicio)

---

## Notas

- Prioridad baja porque el servidor está en red local privada (`10.1.0.x`) sin exposición a internet
- Si en el futuro se expone el servidor via tunnel/proxy, esta story se vuelve crítica
- La key puede ser la misma para todos los servicios (simplifica la gestión) o diferente por servicio
