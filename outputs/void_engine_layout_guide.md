# VOID_ENGINE — Layout Guide

> Estado: activo
> Fecha: 2026-05-01
> Uso: fuente de verdad para construir pantallas de VOID_ENGINE sin depender de mocks generales en Stitch/Gemini.

---

## Propósito

Esta guía define la estructura de layout para la plataforma VOID_ENGINE. Su objetivo es que cada pantalla pueda implementarse directamente en HTML/Tailwind/DaisyUI con dimensiones, zonas y comportamiento consistentes.

Los mocks visuales externos son opcionales y exploratorios. El layout final se decide aquí y se implementa en código.

---

## Modelo Base De Pantalla

VOID_ENGINE usa un workspace técnico de tres columnas:

```text
┌────────────────────────────────────────────────────────────┐
│ Top bar                                                    │ 44px
├──────────────┬──────────────────────────────┬──────────────┤
│ Left context │ Center workspace             │ Right studio │
│ 260px fixed  │ flex-1                       │ 260px fixed  │
├──────────────┴──────────────────────────────┴──────────────┤
│ Bottom status bar                                          │ 28px
└────────────────────────────────────────────────────────────┘
```

### Dimensiones Desktop

| Elemento | Dimensión |
|---|---:|
| Viewport objetivo | 1440px ancho |
| Top bar | 44px alto |
| Bottom status bar | 28px alto |
| Left column | 260px ancho fijo |
| Right column | 260px ancho fijo |
| Center column | `minmax(0, 1fr)` |
| Separadores | 1px |
| Gap entre columnas | 0px |

La altura de la zona principal es:

```css
height: calc(100vh - 44px - 28px);
```

---

## Shell Global

El shell global debe ser estable entre pantallas. Cambia el contenido interno, no la arquitectura.

### Top Bar

Contenido fijo:
- Logo compacto `V_`
- Nombre `VOID_ENGINE`
- Acciones globales alineadas a la derecha

Reglas:
- No usar top bar como navegación primaria.
- No meter títulos de pantalla largos.
- Mantener altura fija de 44px.
- Los icon buttons deben ser cuadrados y compactos.

### Left Column — Context

Uso:
- Contexto activo de sesión.
- Memoria cargada.
- Story activa.
- Entidades activas.
- Estado canónico mínimo.

Reglas:
- Ancho fijo de 260px.
- Solo información que explique el contexto cargado.
- Evitar navegación profunda.
- No usar cards flotantes; usar secciones separadas por líneas.

### Center Column — Workspace

Uso:
- Área principal de trabajo.
- Chat operacional.
- Editors, previews, diff viewers o formularios técnicos según pantalla.

Estructura recomendada:
```text
session actions bar
context/status bar
main work area
input/action bar
```

Reglas:
- El centro debe absorber el espacio flexible.
- Las barras superior e inferior del centro deben tener altura compacta y estable.
- El área principal puede hacer scroll interno.
- Evitar layouts hero o marketing.

### Right Column — Studio

Uso:
- Workflows.
- Outputs de sesión.
- Jobs activos.
- Inspector contextual.

Reglas:
- Ancho fijo de 260px.
- Listas visibles y escaneables.
- El item activo debe ser claro.
- No convertirlo en navegación global si la pantalla requiere inspector.

### Bottom Status Bar

Uso:
- Estado de modelo/servicio.
- CTX usage.
- Workflow activo.
- Story activa.

Reglas:
- Altura fija de 28px.
- Información breve, no editable.
- Sin versiones/build text salvo que la pantalla sea específicamente de diagnóstico.

---

## Breakpoints

VOID_ENGINE se diseña desktop-first. El primer objetivo real es 1440px.

| Rango | Comportamiento |
|---|---|
| `>= 1280px` | Shell completo de 3 columnas |
| `1024px–1279px` | Mantener left column; right column puede colapsar a drawer |
| `< 1024px` | Modo compacto futuro; no prioritario en MVP |

No optimizar prematuramente para móvil hasta que el workspace desktop sea estable.

---

## Reglas De Implementación

### Grid Base

```html
<div class="grid h-screen grid-rows-[44px_1fr_28px]">
  <header></header>
  <main class="grid min-h-0 grid-cols-[260px_minmax(0,1fr)_260px]">
    <aside></aside>
    <section></section>
    <aside></aside>
  </main>
  <footer></footer>
</div>
```

### Scroll

Usar `min-h-0` en contenedores grid/flex que contienen áreas scrollables.

Regla práctica:
- Shell global: no scroll.
- Columnas: scroll interno si el contenido excede.
- Chat/workspace central: scroll interno en el área principal.

### Densidad

La plataforma es una herramienta operacional. Priorizar:
- información escaneable
- controles cercanos al área de trabajo
- baja fricción para tareas repetidas
- jerarquía visual sobria

Evitar:
- hero sections
- cards decorativas grandes
- ilustraciones de relleno
- layouts tipo landing page

---

## Pantalla Base — Main Workspace

La pantalla base de referencia contiene:

Left:
- `CONTEXTO ACTIVO`
- `MEMORIA CARGADA`
- `STORY ACTIVA`
- `ENTIDADES ACTIVAS`
- `ESTADO CANÓNICO`

Center:
- acciones de sesión
- workflow/model context bar
- chat operacional
- input bar

Right:
- `STUDIO`
- workflows
- outputs de sesión

Bottom:
- modelo online
- CTX progress
- workflow/story activos

Esta pantalla es el patrón inicial para construir el MVP de VOID_ENGINE.

---

## Política De Mocks

No se crearán mocks generales por adelantado. Las pantallas se diseñan on demand a partir de:

1. esta guía de layout,
2. la guía UI/UX,
3. el flujo real que se va a implementar,
4. el estado/copy controlado por código.

Stitch/Gemini queda limitado a exploración visual aproximada. No es fuente de verdad para layout, copy ni nombres de workflows.
