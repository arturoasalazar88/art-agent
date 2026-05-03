---
id: STORY_012
title: Estructura base Unity — escena inicial, player controller
status: pending
priority: medium
created: 2026-04-28
updated: 2026-05-02
depends_on: STORY_004
---

# STORY_012 — Estructura Base Unity

Crear el proyecto Unity base del juego con la escena inicial, el player controller y la configuración mínima necesaria para empezar a recibir assets del pipeline.

---

## Objetivo

Proyecto Unity funcional en el servidor o en la máquina de desarrollo con: una escena base vacía, un player controller de survival horror (primera/tercera persona, movimiento sigiloso), y la configuración de Unity MCP para que el Ingeniero pueda operar el editor.

---

## Componentes

### Escena inicial
- Escena vacía con iluminación base (luz ambiental oscura, una fuente de luz puntual)
- Terrain o cubo placeholder como suelo
- Camera rig básico

### Player Controller
- Movimiento en primera o tercera persona (definir con Arturo)
- Velocidad de caminar / agacharse / correr
- Input System nuevo (no el legacy)
- Sin stamina ni mecánicas avanzadas en esta story — solo movimiento base

### Configuración Unity MCP
- Unity MCP instalado y configurado en el proyecto (ver STORY_004 para instrucciones)
- Servidor MCP Unity corriendo y accesible desde Claude Code o el agente

---

## Criterios de aceptación

- [ ] Proyecto Unity creado (versión: a definir con Arturo — LTS recomendado)
- [ ] Escena base `MainScene` funcional (sin errores en consola)
- [ ] Player se mueve en la escena con WASD/joystick
- [ ] Unity MCP instalado y servidor corriendo (test con una herramienta básica)
- [ ] Proyecto en repositorio git o accesible desde el servidor Debian

---

## Preguntas para Arturo antes de implementar

- ¿Primera o tercera persona?
- ¿Versión de Unity? (recomendar LTS 2022.3 o 6000.x)
- ¿El proyecto vive en el servidor Debian o en la máquina local de desarrollo?
- ¿Hay assets de Unity (packages) ya descargados que se quieran incluir?

---

## Notas

- Depende de STORY_004 para conocer las capacidades exactas de Unity MCP antes de configurarlo
- El player controller puede basarse en el Starter Asset - Third Person Controller del Unity Asset Store (gratuito)
