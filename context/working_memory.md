# Working Memory — Checkpoint
> Generado: 2026-04-28T~sesión-7
> Sesión: 2026-04-28
> Contexto aproximado consumido: ~60%

## Qué estábamos haciendo

Creamos `outputs/workflow_map.md` — documentación detallada de todos los workflows creativos y de generación de assets con todos los actores del sistema. El objetivo declarado por Arturo es que este documento sea el insumo base para diseñar una **plataforma de orquestación** que automatice estos procesos. Los MCPs fueron explícitamente excluidos del scope por ahora.

## Hilo de conversación reciente

1. `/context-start` — carga normal, no había working_memory previo
2. Arturo pidió documentación detallada de workflows con todos los actores, registrada en contexto
3. Leímos `handoff-workflows-detallados-llms-orquestador.md`, `spec-workflow-creativo-orquestador-memoria.md`, `mcp-specs-survival-horror.md`
4. Consulta al advisor — recomendó enfocarse en los actores que los inputs NO cubrían (Arturo, El Ingeniero, ComfyUI, switch-model.sh, filesystem, Unity)
5. Arturo interrumpió para aclarar: **excluir MCP del scope** — este documento es un paso previo a un proyecto nuevo (la plataforma)
6. Escribimos `outputs/workflow_map.md` con 14 secciones, 9 workflows, matriz actor×workflow, 16 contratos, 10 gaps
7. Actualizamos `artifacts_registry.md`, `conversation_memory.md` (D40), `CLAUDE.md` (/docs.policy)
8. Arturo preguntó qué significa "paquete contextual mínimo" → explicamos que es el prompt manual que Arturo construye hoy en Open WebUI, y que la plataforma debería automatizarlo

## Decisiones tomadas en esta sesión (no formalizadas aún)

- **D40** — Ya formalizada en `conversation_memory.md`: creación de `workflow_map.md` como fuente de verdad para plataforma
- **Intención de plataforma** — Arturo confirmó que el próximo proyecto será una plataforma para organizar y orquestar todos los procesos del pipeline. Scope aún no definido. No formalizado como decisión aún porque el alcance no está discutido.

## Trabajo en vuelo

- Archivo: `outputs/workflow_map.md` — estado: ✅ completo, entregado, validado por Arturo
- Archivo: `context/artifacts_registry.md` — estado: ✅ actualizado
- Archivo: `context/conversation_memory.md` — estado: ✅ D40 registrado
- Archivo: `CLAUDE.md` — estado: ✅ `workflow_map.md` agregado a /docs.policy

## Contexto técnico inmediato

- Servidor Debian: `asalazar@10.1.0.105` — estado desconocido (no se verificó en esta sesión)
- `outputs/workflow_map.md` tiene 14 secciones, ~700 líneas
- La sección 13 (Gaps) tiene 10 puntos de fricción — será el input principal para la plataforma
- MCP server (puerto 8189) sigue pendiente de implementación — excluido del scope de esta sesión

## Próximo paso exacto

Arturo debe decidir: ¿arrancamos la discusión de arquitectura de la plataforma, o hay algo en `workflow_map.md` que requiere ajuste primero?

## Preguntas abiertas

- ¿Qué forma tomará la plataforma? (app web, CLI, agente, combinación)
- ¿La plataforma reemplaza o envuelve los MCPs eventuales?
- ¿Cuál es el primer gap que la plataforma debe resolver? (candidato obvio: ensamblaje automático del paquete contextual)
- ¿Hay workflows en `workflow_map.md` que estén incompletos o mal entendidos?
