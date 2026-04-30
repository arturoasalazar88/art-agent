---
id: STORY_019
title: Validación de Modelos Creativos — SuperGemma y TrevorJS
status: pending
priority: high
created: 2026-04-29
depends_on: STORY_001
blocks: STORY_007
---

# STORY_019 — Validación de Modelos Creativos

SuperGemma y TrevorJS tienen roles completamente distintos a Ornstein en el pipeline.
No hacen trabajo agéntico estructurado — producen materia prima creativa que Ornstein
después normaliza. Sus tests miden cosas distintas: riqueza de output para extracción,
seguimiento de instrucciones estructurales, y coherencia multi-turno narrativa.

**Los resultados de STORY_001 Bloques A y B (hardware/performance) transfieren directamente**
— misma arquitectura Gemma 4 26B-A4B Q4_K_M, mismo GPU. No repetir esos tests.

---

## Prerequisitos

- [ ] Re-descargar SuperGemma Q4_K_M (`supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf`)
- [ ] Re-descargar TrevorJS Q4_K_M (`gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf`)
- [ ] Recrear servicios systemd (configs en memoria del agente — backup en `project_server_systemd_backup.md`)
- [ ] Aplicar config validada: `--ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0`
- [ ] Script listo: `~/story019_suite.py`

---

## Qué NO probar aquí

- Schema compliance estricto — SuperGemma/TrevorJS no producen JSON
- ID whitelist fidelity — ese es el rol de Ornstein
- Latencias y tok/s — ya validados en STORY_001 (misma arquitectura)
- ctx-size ceiling — ya validado en STORY_001 (mismo hardware)

---

## Dimensiones de Evaluación

### 1. Riqueza de Output para Extracción (ROE)
Mide si el output contiene suficiente material estructurable para que Ornstein normalice.
Un output pobre (vago, sin entidades, sin ubicaciones) hace imposible la extracción.

Métricas automáticas:
- Entidades nombradas: personajes, ubicaciones, objetos con nombre propio
- Densidad de descriptores visuales: adjetivos concretos (colores, texturas, formas, dimensiones) por 100 palabras
- Eventos extractables: acciones con sujeto + verbo + objeto identificables

### 2. Seguimiento de Instrucciones Estructurales (SIS)
Mide si el modelo respeta constraints de formato impuestos desde el prompt.
Ornstein necesita que su input tenga estructura mínima para parsear.

### 3. Coherencia Multi-Turno (CMT)
Mide si el modelo mantiene el estado del mundo narrativo entre turnos.
Un modelo que "olvida" lo que pasó en el turno anterior rompe la continuidad.

### 4. Thinking Mode en Creación
Mide si el thinking mejora la calidad estructural del output creativo.
Distinto al caso agéntico — aquí el valor es en riqueza y coherencia, no en compliance.

---

## Batería de Tests — SuperGemma

### SG1 — Riqueza de output baseline
- **Prompt:** Escena de horror en hospital abandonado — personaje entrando a una sala
- **Mide:** Cantidad de entidades nombradas, descriptores visuales concretos, eventos con sujeto/verbo/objeto
- **Pass:** ≥ 3 entidades nombradas, ≥ 5 descriptores visuales concretos, ≥ 2 eventos extractables
- **Fail:** Output vago ("había algo extraño en la sala") sin entidades ni descriptores concretos

### SG2 — Seguimiento de instrucciones de sección
- **Prompt:** "Escribe la escena en 3 secciones separadas por '---': AMBIENTE / ACCIÓN / CONSECUENCIA. Cada sección máximo 80 palabras."
- **Mide:** ¿Respeta las 3 secciones? ¿Respeta el límite de palabras?
- **Pass:** 3 secciones presentes con delimitador exacto, ninguna supera 80 palabras ±10
- **Fail:** Una sola sección, delimitador distinto, o desbordamiento masivo de palabras

### SG3 — Coherencia multi-turno (3 turnos)
- **T1:** Presentar personaje en loc_north_wing con objeto específico (linterna)
- **T2:** El personaje entra a loc_basement — pedir continuar la escena
- **T3:** Pedir resumen de los dos turnos — ¿recuerda la linterna y el recorrido?
- **Pass:** T3 menciona la linterna y el recorrido north_wing → basement correctamente
- **Fail:** Olvida la linterna, invierte el recorrido, o introduce discontinuidad de estado

### SG4 — Instrucción de inclusión obligatoria
- **Prompt:** "Escribe la escena. OBLIGATORIO incluir: el nombre 'char_drex', la ubicación 'loc_basement', y el objeto 'obj_radio'. No omitas ninguno."
- **Mide:** ¿Aparecen los 3 elementos requeridos en el output?
- **Pass:** Los 3 presentes
- **Fail:** Cualquiera omitido

### SG5 — Thinking budget en creatividad
- **Método:** Misma tarea (SG1) con thinking ON vs OFF
- **Mide:** Tokens de thinking consumidos, diferencia en densidad de descriptores/entidades
- **Pass:** Thinking ≤ 2000 tokens; diferencia de calidad documentada
- **No hay fail:** Es métrica, no criterio binario

---

## Batería de Tests — TrevorJS

### TR1 — Especificidad visual baseline
- **Prompt:** Descripción de una criatura para uso en AssetSpec3D — foco en apariencia física
- **Mide:** Descriptores de color (hex o nombre específico), texturas (superficie, material), proporciones (medidas relativas), movimiento (tipo de locomoción)
- **Pass:** ≥ 2 colores específicos, ≥ 3 texturas de superficie, ≥ 1 descripción de proporción, ≥ 1 descripción de movimiento
- **Fail:** Output genérico ("criatura oscura y aterradora") sin especificidad técnica útil

### TR2 — Contenido traducible a spec técnica
- **Prompt:** Descripción de la criatura + "incluye: altura estimada, número de extremidades, si tiene pelo/escamas/piel, y descripción del modo de ataque"
- **Mide:** ¿El output contiene campos que Ornstein puede mapear a AssetSpec3D? (altura → scale_factor, extremidades → bone_count estimado, superficie → material_profile, ataque → anim_hook)
- **Pass:** ≥ 3 de los 4 campos presentes con valores concretos
- **Fail:** Campos ausentes o demasiado vagos para traducción técnica

### TR3 — Consistency visual multi-paso (2 turnos)
- **T1:** Descripción base de la criatura
- **T2:** "Agrega una variante elite: más grande, con bioluminiscencia en las extremidades. Mantén todo lo demás igual."
- **Mide:** ¿La variante preserva los atributos base y solo agrega los nuevos?
- **Pass:** Atributos base presentes + nuevos atributos añadidos sin contradicción
- **Fail:** Atributos base contradichos o ignorados

### TR4 — Thinking budget en descripción visual
- **Método:** Misma tarea (TR1) con thinking ON vs OFF
- **Mide:** Tokens de thinking, diferencia en especificidad técnica
- **No hay fail:** Es métrica

---

## Rúbrica de Scoring (adaptada para modelos creativos)

| Score | Criterio |
|---|---|
| 4 | Todos los elementos requeridos presentes, métricas de densidad superan umbral, sin contradicción |
| 3 | Un elemento menor faltante o densidad ligeramente bajo el umbral |
| 2 | Un elemento obligatorio faltante o contradicción menor |
| 1 | Múltiples elementos faltantes o contradicción que rompe la continuidad |
| 0 | Output completamente vago, sin entidades, sin descriptores concretos, o desbordamiento total de instrucciones |

**5 runs por test, temperature=0** — misma lógica pass@5 que STORY_001.

**Umbral de producción para modelos creativos:** avg ≥ 3.0 + pass@5 ≥ 60% en todos los tests de riqueza y coherencia.

> Umbral más bajo que Ornstein (3.5/80%) porque el output creativo tiene más variabilidad
> aceptable — lo que importa es que Ornstein pueda trabajar con él.

---

## Criterio de Decisión Final

| Resultado | Acción |
|---|---|
| Ambos modelos pasan el umbral | Proceder con STORY_007 (system prompts adaptados al workflow) |
| Un modelo falla | Ajustar system prompt del modelo y re-testear |
| Ambos fallan en SIS (instrucciones estructurales) | Rediseñar protocolo de handoff — Ornstein necesita prompt más robusto o formato más tolerante |
| TR1/TR2 fallan (TrevorJS sin especificidad técnica) | Evaluar si Vision puede compensar el gap de especificidad |

---

## Script de Test

- `~/story019_suite.py` — script principal, corre SuperGemma y TrevorJS por separado
- Resultados en `~/story019_results/`
- Diseñado para `nohup python3 ~/story019_suite.py > ~/story019.log 2>&1 &`
- **Nota:** El script evalúa métricas estructurales automáticas. La evaluación cualitativa del contenido creativo es decisión de Arturo.
