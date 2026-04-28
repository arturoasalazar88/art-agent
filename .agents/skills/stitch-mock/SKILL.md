---
name: stitch-mock
description: Genera prompts ultra-detallados para Google Stitch que producen mockups pixel-perfect de cualquier pantalla de cualquier aplicacion. Cada string, color, tamano y layout queda especificado explicitamente sin dejar nada a interpretacion de Stitch.
compatibility: opencode
---

# Stitch Mock — Generador de Prompts para Mockups

## Proposito

Generar un prompt completo y auto-contenido listo para pegar en Google Stitch.
El prompt no deja ningun elemento a interpretacion: cada texto, color, tamano
y layout queda definido con precision para que Stitch no invente nada.

## Regla de ejecucion

Reunir informacion faltante **una sola pregunta a la vez**.
Nunca presentar listas de preguntas. Esperar respuesta antes de continuar.

---

## Proceso

### Paso 1 — Sistema de diseno

Si el proyecto tiene un archivo de diseno (DESIGN.md, tokens, guia de estilo),
leerlo antes de preguntar. Si no existe, preguntar uno por uno:

- nombre de la aplicacion
- paleta de colores (fondos, superficies, texto primario, texto secundario, acento)
- tipografia (familia, escala de tamanos, pesos)
- elementos que se repiten en todas las pantallas (top bar, sidebar, status bar)
- estructura de layout (columnas fijas, areas flexibles, border-radius de la ventana)

### Paso 2 — Pantalla especifica

- que pantalla vamos a generar
- que item de navegacion queda activo
- que modelo o contexto esta activo en esa pantalla

### Paso 3 — Contenido de la pantalla

Preguntar por cada seccion unica: columna central, area principal,
cards, tablas, formularios. Obtener textos exactos, datos de ejemplo,
estados de cada elemento.

### Paso 4 — Generar el prompt

---

## Estructura del prompt generado

```
[ENCABEZADO DE REGLAS CRITICAS]

[DESCRIPCION DE VENTANA Y CHROME]

════════════════════
[BLOQUE: BARRA SUPERIOR]
════════════════════

════════════════════
[BLOQUE: SIDEBAR / NAVEGACION]
════════════════════

════════════════════
[BLOQUE: COLUMNA CENTRAL] (si aplica)
════════════════════

════════════════════
[BLOQUE: CONTENIDO PRINCIPAL]
════════════════════

════════════════════
[BLOQUE: BARRA DE ESTADO INFERIOR] (si aplica)
════════════════════
```

---

## Encabezado obligatorio en todo prompt generado

```
REGLAS CRITICAS — LEER ANTES DE GENERAR:
1. USA EXACTAMENTE el texto especificado entre comillas dobles.
   NO lo traduzcas, NO lo parafrasees, NO lo reemplaces.
2. TODO el texto visible en la UI debe estar en el idioma especificado.
3. NO inventes descripciones, etiquetas ni texto alternativo.
4. NO generes placeholders propios. Usa los textos exactos de este prompt.
5. Si un texto aparece entre comillas dobles, debe aparecer
   palabra por palabra en el diseno final.
6. Si un elemento no esta especificado en este prompt, no lo incluyas.
```

---

## Convencion de especificacion de elementos

```
Nombre del elemento (dimensiones, fondo, borde, layout):
  - Propiedad: valor
  - Texto EXACTO "string literal" — Inter 13px medium, color #xxxxxx
  - Icono: descripcion, tamano px, color hex
  - Estado: descripcion visual del estado activo / inactivo
```

Reglas:
- Colores siempre en hex (#rrggbb) o rgba()
- Tamanos siempre en px
- Textos entre comillas dobles precedidos de la palabra EXACTO
- Layout con flex o grid + propiedades completas
- Bordes: Npx solid color o rgba()

---

## Bloques canonicos

Los bloques que se repiten en todas las pantallas se especifican una vez
y se reutilizan indicando solo lo que cambia entre pantallas
(item activo del sidebar, modelo en la barra de estado, titulo de la pagina).

Elementos tipicamente canonicos:
- barra superior con nombre de la app e iconos de accion
- sidebar de navegacion con secciones e items
- barra de estado inferior con metricas del sistema
- chrome de ventana macOS (semaforos, border-radius, sombra exterior)

---

## Criterio de calidad

El prompt es correcto cuando:
- cualquier disenador puede reproducir el mockup exactamente sin tomar decisiones propias
- cada string visible esta especificado literalmente entre comillas
- cada color tiene su hex exacto
- cada elemento tiene su tamano en px
- no hay ninguna ambiguedad de layout
