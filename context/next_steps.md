# Foco de Sesión

> Última actualización: 2026-04-29
> Nota: Las listas de tareas y trabajo pendiente están en `context/stories/INDEX.md`.
> Este archivo contiene solo el contexto de sesión: qué acaba de pasar y restricciones técnicas críticas.

---

## Fase Actual

**Pre-producción** — Infraestructura validada, pipeline diseñado, agente auditado. Diseñando arquitectura de agentes especializados y sistema de memoria atómica.

---

## Completado en Última Sesión (2026-04-29)

- [x] Sistema de índice de stories creado — `context/stories/INDEX.md` + 18 stories organizadas por área
- [x] CLAUDE.md actualizado — stories/INDEX.md integrado en /memory.load y /docs.policy
- [x] Skill /context-start actualizado — carga y muestra INDEX.md
- [x] Decisión: Blueprint Compiler como script determinístico, no LLM (elimina riesgo censura en El Ingeniero)
- [x] Decisión: El Ingeniero = Unity assembler en modo ejecución con memoria técnica mínima
- [x] Investigación de memoria: Obsidian + context engineering validado como patrón — bloques fijos + compiler

---

## Contexto Técnico Crítico

- **ctx-size actual:** 8,192 tokens con Q4_K_M — NO subir sin validar Q3_K_M o KV cuantizado primero
- **STORY_001 bloqueante:** la validación de contexto expandido define presupuestos de tokens para todos los agentes
- **Servidor:** `asalazar@10.1.0.105` — verificar estado al inicio de cada sesión
- **MCP server (8189):** pendiente de implementación — specs en `inputs/mcp-specs-survival-horror.md`
- **ComfyUI y llama-server:** nunca simultáneos — usar `~/switch-model.sh`

---

## Preguntas para el Usuario al Inicio de Sesión

- ¿Hubo cambios en el servidor desde la última sesión?
- ¿Tienes los resultados de Perplexity para el set de pruebas de capacidad agéntica?
- ¿Empezamos con STORY_001 (validación de modelos) o con el diseño de la plataforma?
