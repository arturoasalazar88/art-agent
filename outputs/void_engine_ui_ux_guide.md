# VOID_ENGINE — UI/UX Guide

> Estado: activo
> Fecha: 2026-05-01
> Uso: guía de diseño visual, interacción y contenido para la plataforma VOID_ENGINE.

---

## Principio Central

VOID_ENGINE es una herramienta operacional para orquestar agentes, memoria, workflows y outputs técnicos. Debe sentirse como un workspace de producción: denso, claro, estable y rápido de escanear.

No es una landing page. No es una pieza editorial. No debe depender de mocks generativos para decisiones finales de copy o layout.

---

## Stack UI

| Capa | Decisión |
|---|---|
| Framework app | AdonisJS 7.x |
| Interacción parcial | HTMX |
| Estado ligero cliente | Alpine.js |
| CSS | Tailwind CSS |
| Componentes | DaisyUI |
| Tema | dark-only custom theme |

Los componentes deben ser HTML-first y compatibles con HTMX. Evitar dependencias que requieran React/Vue/Svelte para el MVP.

---

## Paleta

Tema dark-only con fondos charcoal sólidos y un acento principal.

| Token | Hex | Uso |
|---|---|---|
| `base-100` | `#0b0d14` | fondo global |
| `base-200` | `#111522` | superficies principales |
| `base-300` | `#141824` | superficies elevadas/hover |
| `border` | `#1f2535` | divisores y bordes |
| `primary` | `#5b7cff` | activo principal |
| `success` | `#56d38a` | online/success |
| `warning` | `#d9a441` | warning |
| `text-primary` | `#f4f7ff` | texto principal |
| `text-muted` | `#8b9ec0` | texto secundario |

Reglas:
- No usar gradientes como base visual.
- No usar glassmorphism para el MVP.
- No introducir un segundo acento fuerte sin decisión explícita.
- Evitar estética cyberpunk/neon.

---

## Tipografía

Objetivo: lectura técnica compacta.

Recomendación:
- UI general: Inter, system-ui o equivalente.
- Código/IDs: JetBrains Mono, ui-monospace o equivalente.

Escala:

| Uso | Tamaño | Peso |
|---|---:|---:|
| Labels densos | 11px–12px | 500 |
| Texto UI normal | 13px–14px | 400/500 |
| Secciones | 12px | 700, uppercase |
| Código | 12px–13px | 400 |
| Botones compactos | 12px–13px | 600 |

Reglas:
- No usar display type grande dentro del workspace.
- No usar letter spacing negativo.
- Usar uppercase solo en headers de sección cortos.

---

## Componentes

### Buttons

Usar botones compactos para acciones de sesión.

Estados mínimos:
- default
- hover
- active/current
- disabled
- danger/destructive solo cuando aplique

Reglas:
- Icon buttons para acciones globales cuando el icono sea familiar.
- Text buttons para comandos explícitos como `Checkpoint`, `Cerrar sesión`.
- No usar botones grandes tipo marketing.

### Pills / Badges

Usos:
- workflow activo
- modelo activo
- estado de story
- entidades activas

Reglas:
- Badges deben ser cortos.
- No meter frases largas.
- El estado activo usa `primary`; online usa `success`.

### Lists

Usos:
- workflows
- outputs
- memoria cargada
- entidades

Reglas:
- Item activo claramente resaltado.
- Filas compactas.
- Texto exacto controlado desde código.
- Si el texto no cabe, truncar con tooltip o usar columna más ancha en pantalla específica.

### Chat Operacional

El chat es una herramienta de trabajo, no una conversación social.

Reglas:
- Mensajes técnicos.
- Burbujas sobrias.
- Código en bloques monoespaciados.
- Metadata mínima y explícita.
- No mostrar speaker labels si el contexto visual ya distingue dirección.

### Status Bar

Debe comunicar estado operativo:
- modelo/servicio online
- uso de contexto
- workflow activo
- story activa

Reglas:
- Una sola línea.
- Sin versión/build text salvo pantallas de diagnóstico.
- El progreso CTX debe ser compacto y legible.

---

## UX Por Tipo De Tarea

### Orquestación De Workflow

El usuario debe ver:
- workflow activo
- paso actual
- modelo activo
- outputs generados
- estado de memoria/canon relevante

Acciones cercanas:
- checkpoint
- guardar decisión
- cerrar sesión
- limpiar chat

### Revisión De Outputs

Cuando el centro muestra archivos o JSON:
- priorizar legibilidad del contenido
- usar diff/preview si aplica
- mantener outputs relacionados en right column
- no ocultar estado de contexto

### Diagnóstico Técnico

Pantallas de diagnóstico pueden romper la regla de bottom bar minimalista para mostrar:
- versión
- logs
- servicios
- puertos
- latencia

Esto debe ser pantalla específica, no el shell general.

---

## Reglas De Copy

El copy de VOID_ENGINE es operacional y exacto.

Reglas:
- Usar nombres reales de workflows desde código.
- No permitir que herramientas generativas renombren workflows.
- No traducir dinámicamente labels técnicos.
- IDs como `STORY_017`, `WF-02`, `ctx_used` deben conservarse.
- El copy final vive en templates/componentes, no en mocks generativos.

---

## Política Sobre Gemini/Stitch

Gemini/Stitch queda clasificado como herramienta exploratoria visual de baja confianza.

Uso permitido:
- moodboard aproximado
- explorar densidad
- explorar composición general
- inspiración visual no vinculante

No usar como fuente de verdad para:
- nombres de workflows
- copy exacto
- estructura final de layout
- jerarquía de información
- componentes finales
- diseño de interacciones

Si un mock de Stitch contradice esta guía, gana esta guía.

---

## Criterios De Aprobación UI

Una pantalla de VOID_ENGINE está lista para implementación cuando:

- respeta el shell base o documenta por qué lo cambia,
- mantiene densidad operacional,
- no inventa secciones,
- todos los textos críticos vienen de datos controlados,
- los estados activos son obvios,
- el usuario puede identificar workflow, modelo, story y outputs sin buscar,
- no depende de interpretación visual de una herramienta generativa.

---

## Flujo De Diseño On Demand

Para cada pantalla nueva:

1. Definir objetivo operacional.
2. Definir datos visibles.
3. Elegir si usa shell base completo o variante.
4. Dibujar layout textual simple.
5. Implementar en HTML/Tailwind/DaisyUI.
6. Validar con captura real de browser.
7. Ajustar diseño en código.

Los mocks externos son opcionales y no bloquean implementación.
