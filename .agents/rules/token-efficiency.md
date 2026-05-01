# Token Efficiency Rules

**Priority**: HIGH | Aplica a: todas las sesiones, todos los runtimes

> Estas reglas reducen tokens sin cambiar la calidad ni el funcionamiento del agente.
> En caso de conflicto con `no-assumptions.md`, la no-assumptions rule tiene prioridad.

---

## Lectura de archivos

- Antes de leer cualquier archivo >150 líneas, correr `grep -n "patron" archivo`
  para localizar la sección relevante. Luego leer solo ±30 líneas alrededor del offset.
- Si ya leíste un archivo en esta sesión, no lo releas. Edita desde memoria.
- Para discovery: `grep -r "symbol" src/ --include="*.py" -l` lista candidatos
  antes de abrir cualquier archivo.
- **EXCEPCIÓN obligatoria:** Los archivos de `context-start` se leen completos siempre —
  son la fuente de verdad de la sesión. No aplicar regla de fragmentos a:
  `project_state.md`, `artifacts_registry.md`, `conversation_memory.md`,
  `next_steps.md`, `stories/INDEX.md`, `working_memory.md`.

## Comandos SSH y shell

- Preferir un solo SSH con comandos encadenados (`&&`, `;`) sobre múltiples
  conexiones SSH para la misma verificación.
  - ✅ `ssh server 'cmd1 && echo "---" && cmd2 && cmd3'`
  - ❌ ssh cmd1 → ssh cmd2 → ssh cmd3
- Si una subtarea requiere >3 comandos SSH independientes, escribir un script
  en `/tmp/`, enviarlo con `scp` y ejecutar uno solo.
- No lanzar comandos de forma especulativa ("a ver si existe").
  Saber qué se necesita antes de llamar la herramienta.
- **EXCEPCIÓN:** Health checks y verificaciones de estado son siempre válidos —
  forman parte de la no-assumptions rule y no cuentan como gasto especulativo.

## Edición de archivos

- **Plan primero:** antes de cualquier edición, listar en una línea por cambio
  `(archivo, línea aproximada, qué cambia)`. Luego ejecutar todo de una vez.
- Después de editar: verificar con el comando relevante o tests,
  **no** releyendo el archivo editado.
- Usar `replace_file_content` o `multi_replace_file_content` en lugar de
  leer + reescribir el archivo completo.

## Razonamiento y respuestas

- Máximo 2 oraciones de enfoque antes de actuar. No narrar el contexto que ya
  está en memoria. No reexplicar la tarea al usuario antes de ejecutarla.
- No hacer "review pass" final a menos que el usuario lo pida explícitamente.
- Si los tests pasan y el output es correcto, detenerse. No agregar verificaciones extra.

## Límite de intentos por problema

- Si un fix falla **2 veces con el mismo approach**, detenerse.
  Aplicar no-assumptions rule desde cero: leer el error real, reformular hipótesis.
  No intentar variante #3 sin evidencia nueva que justifique el cambio de approach.

## Lo que NO aplica aquí

| Regla genérica del research | Razón por la que NO se adopta |
|---|---|
| "Do not re-read after editing" absoluto | Contradice no-assumptions — verificar con evidencia tiene prioridad |
| "Suppress extended thinking" | Los modelos locales ya tienen thinking OFF validado vía harness |
| "Route trivial tasks to smaller models" | Stack local: un solo modelo activo a la vez |

---

**Version**: 1.0 | **Creado**: 2026-05-01
**Fuente**: Empirical study SMU/Heidelberg 2026 + community AGENTS.md best practices
**Ahorro estimado**: 20-30% de tokens/sesión en sesiones de debugging activo
