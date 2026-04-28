---
name: session-lifecycle
description: Aplica el flujo completo de sesion del proyecto: context-start al inicio, context-save durante el trabajo, context-checkpoint cuando convenga y context-close al final. Usalo para recordar y reforzar la disciplina operativa entre agentes.
compatibility: opencode
---

# Session Lifecycle

Este skill resume el flujo operativo completo del sistema de memoria.

## Flujo obligatorio

1. Ejecutar `context-start` al inicio.
2. Trabajar la tarea tecnica.
3. Usar `context-save` para decisiones o descubrimientos que deban persistir antes del cierre.
4. Usar `context-checkpoint` antes de operaciones largas, si el hilo se vuelve denso, o cada ~30 mensajes.
5. Ejecutar `context-close` al final sin excepcion.

## Objetivo

Mantener la misma disciplina de memoria entre Claude Code, OpenCode y cualquier otro runtime que use este repo.
