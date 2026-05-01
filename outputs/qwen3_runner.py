#!/usr/bin/env python3
"""
Qwen3.6-35B-A3B — Context Window Validation Suite
Tests: T1 (JSON exacto), T2 (MCP tool call), T3 (codegen + constraints), T4 (multi-turn)
Ctx variants: 4k / 8k / 16k / 24k / 32k

Usage:
  python3 qwen3_runner.py <T1|T2|T3|T4> <4k|8k|16k|24k|32k> [model] [thinking:true|false]

Examples:
  python3 qwen3_runner.py T1 4k
  python3 qwen3_runner.py T2 24k qwen3-coder false
  python3 qwen3_runner.py T4 16k qwen3-coder true

Output: one JSON line per run with keys:
  test_id, ctx_size, json_valid, schema_valid, values_correct, latency_ms,
  completion_tokens, thinking, pass
"""

import json
import sys
import time
import pathlib
import tempfile
import subprocess
import re
from urllib import request as urlrequest

API_URL = "http://localhost:8013/v1/chat/completions"
DEFAULT_MODEL = "qwen3-coder"

# ---------------------------------------------------------------------------
# Context size targets (input tokens approx)
# ---------------------------------------------------------------------------
CTX_TARGETS = {
    "4k":  1000,
    "8k":  6000,
    "16k": 14000,
    "24k": 22000,
    "32k": 30000,
}

# ---------------------------------------------------------------------------
# Filler blocks (thematic, no correct answers buried here)
# ---------------------------------------------------------------------------
BLOCK_A = """DOCUMENTO A // SANATORIO DE SANTA BRUMA

El sanatorio fue ampliado en tres fases y ninguna comparte el mismo sistema de señalización.
El pabellón norte conserva placas de esmalte azul, el pabellón central utiliza pintura blanca
sin reflectante y el subsuelo técnico mezcla marcas antiguas con rotulación temporal escrita
a mano. Para evitar lecturas erróneas durante pruebas nocturnas, todas las rutas internas de
mantenimiento se describen por nombre y por función: "pasillo de calderas", "archivo de dietas",
"galería de cisternas" y "corredor de observación". Los diseñadores de nivel deben tratar estos
nombres como ambientación persistente, no como identificadores canónicos de scripting.

Durante el turno de madrugada, el personal ficticio del juego registra ruidos de tubería cada
once minutos en la galería de cisternas. Ese patrón no activa ningún evento por sí mismo, pero
sí modifica la percepción del jugador: los sonidos metálicos se mezclan con respiraciones lejanas
y con el zumbido de lámparas defectuosas. En los documentos internos se aclara que la presión
sonora debe sugerir deterioro físico del edificio, no presencia inmediata de criatura. Esto
permite que un área sea intensa sin requerir combate, algo importante para economizar spawns y
mantener el ritmo de survival horror.

En términos de narrativa sistémica, Santa Bruma evita pistas demasiado obvias. Los memorandos
del pabellón central incluyen horarios, nombres incompletos y referencias cruzadas a llaves,
botiquines y ascensores inutilizados. Ninguna de esas menciones debe convertirse automáticamente
en objetivo. El propósito del material es densificar el contexto y dar al modelo suficiente ruido
temático para obligarlo a localizar instrucciones realmente críticas cuando aparezcan en anexos
o apéndices posteriores."""

BLOCK_B = """DOCUMENTO B // REGLAS DE ESCENA Y ATMÓSFERA

Las escenas del prototipo usan una taxonomía de tensión dividida en "calma tensa", "alerta",
"pánico breve" y "fatiga". Cada estado afecta tres capas: iluminación, sonido y frecuencia de
interacción. En calma tensa, la iluminación debe fluctuar poco y el jugador sólo encuentra señales
ambiguas; en alerta, aparecen indicadores parciales de amenaza, como puertas entornadas, arrastre
de muebles o radios con estática; en pánico breve, se permite un estímulo fuerte y corto; en
fatiga, el entorno vuelve a bajar pulsaciones, pero deja consecuencias visibles del episodio
anterior.

Las entidades ambientales se clasifican en pasivas, reactivas y hostiles. Una entidad pasiva nunca
inicia contacto; una reactiva responde a proximidad, luz o ruido; una hostil puede iniciar
persecución si el jugador incumple una regla local. Los diseñadores deben recordar que muchas notas
de escena describen estas categorías como parte del mundo ficcional. Eso significa que no todas las
menciones a luces, puertas o camillas implican una tool call. Algunas sólo existen para formar un
fondo coherente que haga más difícil distinguir el dato verdaderamente operativo cuando aparezca.

Los textos de ambientación también reiteran restricciones de consistencia. Las zonas médicas usan
superficies húmedas, ruedas chirriantes, fluorescentes inestables y olores químicos insinuados por
descripción. Las zonas residenciales prefieren polvo, tela vieja, madera hinchada y silencio
interrumpido por cañerías. Si el modelo mantiene este contexto en ventanas largas, no debería
confundir un informe de ambientación con un protocolo de scripting. Ese contraste ayuda a medir
si el ctx largo sigue siendo fiable."""

BLOCK_C = """DOCUMENTO C // ESPECIFICACIÓN DE SISTEMAS INTERNOS

El juego distingue entre eventos de ambiente y eventos de control. Los eventos de ambiente alteran
audio, luces o partículas y suelen aceptar payloads pequeños; los de control pueden cambiar estados
persistentes y suelen requerir nombres de objeto exactos. Aun así, esta distinción aparece repetida
en varios documentos sólo para crear contexto técnico coherente. No debe asumirse que cualquier
cadena con forma de identificador representa una instrucción vigente. En varias pruebas anteriores,
mezclar documentación técnica con narrativa resultó útil para detectar cuándo un modelo ya no estaba
leyendo con precisión.

En la herramienta de escenas, las transformaciones espaciales siguen el orden posición, rotación y
escala. Las notas de diseño insisten en eso porque algunos generadores tienden a invertir los campos
cuando están bajo presión de contexto largo. Sin embargo, este bloque no autoriza ninguna acción
concreta. Su propósito es describir el comportamiento esperado del runtime y servir de relleno técnico
que se parece a documentación real: suficientemente detallado para ser plausible, pero irrelevante
para el resultado correcto de los tests.

Otro detalle importante es que los objetos marcadores se usan como puntos de referencia semánticos,
no necesariamente visuales. Un marcador puede existir aunque el jugador nunca lo vea. El contenido
de este bloque intenta parecer importante sin contener la respuesta exacta. Si el modelo empieza a
responder usando nombres o reglas de aquí en vez de las del anexo crítico, la ventana de contexto
ya no está siendo usada de forma fiable para recuperación precisa."""

BLOCK_D = """DOCUMENTO D // BITÁCORA OPERATIVA Y LORE FUNCIONAL

Las brigadas ficticias del subsuelo dejaron registros con estilo casi burocrático: fecha incompleta,
firma ilegible, observación breve y cierre abrupto. Muchos hablan de humedad, cajas médicas vencidas,
ascensores inmóviles y ruido detrás de muros de azulejo. La intención no es resolver un rompecabezas,
sino sostener la ilusión de un edificio intervenido demasiadas veces por equipos distintos. Este tipo
de prosa debe ocupar espacio útil dentro del contexto y competir por atención con documentos técnicos
más explícitos.

En las pruebas de jugabilidad, los jugadores recuerdan mejor los nombres de pasillos que los códigos
numéricos, así que el lore repite zonas con ligeras variaciones: archivo de sueros, corredor de
bañeras, sala de rayos, cuarto de electroterapia, escalera de lavandería. Ninguno de estos nombres
sirve como clave de scripting en esta suite. Se incluyen precisamente para verificar que el modelo no
sustituya valores exactos por aproximaciones verosímiles cuando el anexo correcto está enterrado más
adelante.

Los supervisores del proyecto describen este enfoque como "densidad honesta": suficiente detalle para
parecer un documento real de survival horror, pero con separación clara entre ambientación y datos
operativos. Si la recuperación sigue siendo perfecta a 24k o 32k, el modelo todavía discrimina bien
entre ruido temático e instrucción verdadera. Si empieza a contestar con nombres de este bloque, el
fallo ya no es de formato sino de atención efectiva sobre contexto largo."""

FILLERS = [BLOCK_A, BLOCK_B, BLOCK_C, BLOCK_D]

# ---------------------------------------------------------------------------
# Needle documents (buried at ~85% of input — correct answers live only here)
# ---------------------------------------------------------------------------
NEEDLE_T1 = """ANEXO CRÍTICO K-12

Durante la auditoría del subsuelo se corrigieron identificadores inconsistentes del ala húmeda.
La sala de control secundaria ya no debe citarse con su alias antiguo; su nombre operativo correcto
es "Morgue Relay". La puerta sellada que aísla el corredor de conservación se registra como "DR-19".
El código de anulación del relé de niebla no usa guiones bajos ni espacios: el literal correcto
es "KASTOR-441".

En la bitácora térmica se fijó un umbral estricto: si el depósito azul supera 17.5 C, el sistema
no abre compuertas sino que publica un aviso en el bus "BELL_7". Ninguno de estos valores debe
inferirse a partir del lore general; sólo son válidos los identificadores de este anexo. Una copia
previa mencionaba otros nombres, pero quedaron anulados al cierre del incidente."""

NEEDLE_T2 = """PROTOCOLO DE ESCENA // WARD EAST B2

La escena activa es "ward_east_b2". En esta versión de la secuencia, el porcentaje de oxígeno ya
fue medido y no debe volver a consultarse: oxygen_percent=24. El ancla de fusible sí existe:
FuseAnchor_exists=true. Cuando oxygen_percent < 30 y FuseAnchor_exists=true, el primer paso
autorizado NO es consultar ni transformar nada, sino crear un objeto vacío hijo para marcar el
punto de reparación.

La llamada correcta y única para iniciar el protocolo es:
scene="ward_east_b2"
type="empty"
name="FuseAnchor_child"
parent="FuseAnchor"

La posición se hereda o corrige después; no forma parte de esta primera llamada."""

NEEDLE_T3 = """ESPECIFICACIÓN TÉCNICA // MANIFIESTO DE SPAWN

Constraint C-03: usar sólo stdlib de Python: json, csv, argparse, pathlib y typing.
Constraint C-07: el tamaño máximo de lote debe fijarse como MAX_BATCH = 32.
Constraint C-11: toda salida normalizada debe usar exactamente las claves zone_id, enemy_type
y spawn_weight.
Constraint C-14: no se permiten dependencias externas ni import dinámico.

La utilidad debe exponer una función build_manifest(records) y un entrypoint CLI. El runner
validará que el archivo compile, que MAX_BATCH exista con valor 32, que build_manifest exista
y que no aparezca la cadena "import pandas"."""

NEEDLE_T4 = """PROTOCOLO DE RESTABLECIMIENTO // HOSPITAL BASEMENT 03

La escena activa es "hospital_basement_03". El objeto crítico se llama "RelayTheta". El
procedimiento correcto tiene dos pasos:
Paso 1: consultar el estado actual de RelayTheta.
Paso 2: si el resultado indica status="offline", disparar el evento "prime_relay" sobre
RelayTheta con payload {"amp":7,"source":"aux_line_B"}.

No se debe usar otro amp. No se debe consultar un objeto distinto. No se debe disparar el
evento si RelayTheta ya está online."""

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------
SYS_T1 = (
    "Lee todo el contexto antes de responder. Devuelve SOLO JSON válido. "
    "No uses markdown. No expliques nada.\n"
    'Schema exacto:\n'
    '{"control_room":"string","sealed_door":"string","failsafe_code":"string",'
    '"coolant_limit_c":0,"event_bus":"string"}'
)

SYS_T2 = (
    "Devuelve SOLO JSON válido. No uses markdown. No expliques nada.\n"
    'Schema exacto:\n{"tool":"string","arguments":{}}'
)

SYS_T3 = (
    "Devuelve SOLO JSON válido. No uses markdown. No expliques nada.\n"
    'Schema exacto:\n{"files":[{"path":"string","content":"string"}],"notes":["string"]}'
)

SYS_T4 = (
    "Devuelve SOLO JSON válido. No uses markdown. No expliques nada.\n"
    'Schema exacto:\n{"tool":"string","arguments":{}}'
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def build_context(needle: str, target_tokens: int) -> str:
    """Build filler context with needle buried at ~85% of total input."""
    prefix_blocks = []
    suffix_blocks = []
    idx = 0
    while True:
        current = estimate_tokens(
            "\n\n".join(prefix_blocks + [needle] + suffix_blocks)
        )
        if current >= target_tokens:
            break
        block = FILLERS[idx % len(FILLERS)]
        needle_pos = estimate_tokens("\n\n".join(prefix_blocks + [needle]))
        total_so_far = estimate_tokens("\n\n".join(prefix_blocks + [needle] + suffix_blocks))
        ratio = needle_pos / max(total_so_far, 1)
        if ratio > 0.85:
            suffix_blocks.append(block)
        else:
            prefix_blocks.append(block)
        idx += 1
        if idx > 600:
            break
    return "\n\n".join(prefix_blocks + [needle] + suffix_blocks)


def parse_json_safe(text: str):
    """Parse JSON, stripping ```json fences if present."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        text = match.group(1).strip()
    try:
        return True, json.loads(text)
    except Exception:
        return False, None


def post_chat(model, messages, temperature, max_tokens, thinking, preserve_thinking=False):
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": 0.95 if thinking else 0.80,
        "top_k": 20,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {
            "enable_thinking": thinking,
            "preserve_thinking": preserve_thinking,
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urlrequest.Request(
        API_URL, data=data, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urlrequest.urlopen(req, timeout=1800) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    latency_ms = int((time.time() - t0) * 1000)
    content = raw["choices"][0]["message"].get("content", "")
    usage = raw.get("usage", {})
    return content, usage, latency_ms


def exact_match(obj: dict, expected: dict) -> tuple[int, int]:
    """Recursively count exact field matches."""
    hits, total = 0, 0
    for k, v in expected.items():
        total += 1
        if isinstance(v, dict):
            sub = obj.get(k, {}) or {}
            sub_hits, sub_total = exact_match(sub, v)
            hits += sub_hits
            total += sub_total - 1  # already counted k above
        else:
            if obj.get(k) == v:
                hits += 1
    return hits, total


def eval_t3(obj: dict) -> tuple[int, int, bool]:
    """Evaluate T3 gates. Returns (hits, total, compile_ok)."""
    total = 6
    hits = 0
    compile_ok = False

    if obj.get("notes") == ["C-03", "C-07", "C-11", "C-14"]:
        hits += 1

    files = obj.get("files", [])
    if len(files) == 1 and files[0].get("path") == "tools/build_spawn_manifest.py":
        hits += 1
        code = files[0].get("content", "")

        if "def build_manifest(" in code:
            hits += 1
        if "MAX_BATCH = 32" in code:
            hits += 1
        if all(x in code for x in ["zone_id", "enemy_type", "spawn_weight"]):
            hits += 1
        if "import pandas" not in code:
            hits += 1

        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "tools"
            p.mkdir(parents=True, exist_ok=True)
            f = p / "build_spawn_manifest.py"
            f.write_text(code, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(f)],
                capture_output=True,
            )
            compile_ok = result.returncode == 0

    return hits, total, compile_ok


def print_result(test_id, ctx_tokens, json_valid, schema_valid,
                 values_correct, total_values, latency_ms,
                 completion_tokens, thinking):
    passed = json_valid and values_correct == total_values
    row = {
        "test_id": test_id,
        "ctx_size_tokens": ctx_tokens,
        "json_valid": json_valid,
        "schema_valid": schema_valid,
        "values_correct": f"{values_correct}/{total_values}",
        "latency_ms": latency_ms,
        "completion_tokens": completion_tokens,
        "thinking": thinking,
        "pass": passed,
    }
    print(json.dumps(row, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Test runners
# ---------------------------------------------------------------------------

def run_t1(model, ctx_label, thinking):
    context = build_context(NEEDLE_T1, CTX_TARGETS[ctx_label])
    user = (
        "CONTEXT START\n"
        f"{context}\n"
        "CONTEXT END\n\n"
        "Extrae exclusivamente los 5 valores del anexo crítico. "
        "Devuelve SOLO JSON válido con el schema indicado. No inventes campos."
    )
    messages = [
        {"role": "system", "content": SYS_T1},
        {"role": "user", "content": user},
    ]
    content, usage, latency_ms = post_chat(
        model, messages,
        temperature=0.2, max_tokens=2048,
        thinking=thinking, preserve_thinking=False,
    )
    json_valid, obj = parse_json_safe(content)
    expected = {
        "control_room": "Morgue Relay",
        "sealed_door": "DR-19",
        "failsafe_code": "KASTOR-441",
        "coolant_limit_c": 17.5,
        "event_bus": "BELL_7",
    }
    values_correct, total_values = exact_match(obj or {}, expected)
    ctx_tokens = usage.get("prompt_tokens", estimate_tokens(user + SYS_T1))
    completion_tokens = usage.get("completion_tokens", estimate_tokens(content))
    print_result("T1", ctx_tokens, json_valid, json_valid,
                 values_correct, total_values, latency_ms, completion_tokens, thinking)


def run_t2(model, ctx_label, thinking):
    context = build_context(NEEDLE_T2, CTX_TARGETS[ctx_label])
    user = (
        "Herramientas disponibles:\n"
        '1) query_scene {"scene":"string","name":"string"}\n'
        '2) create_object {"scene":"string","type":"point_light|mesh|empty","name":"string","parent":"string|null"}\n'
        '3) set_transform {"scene":"string","name":"string","position":[number,number,number],'
        '"rotation":[number,number,number],"scale":[number,number,number]}\n\n'
        "CONTEXT START\n"
        f"{context}\n"
        "CONTEXT END\n\n"
        "Devuelve la única tool call correcta para iniciar el protocolo actual."
    )
    messages = [
        {"role": "system", "content": SYS_T2},
        {"role": "user", "content": user},
    ]
    content, usage, latency_ms = post_chat(
        model, messages,
        temperature=0.1, max_tokens=2048,
        thinking=thinking, preserve_thinking=False,
    )
    json_valid, obj = parse_json_safe(content)
    expected = {
        "tool": "create_object",
        "arguments": {
            "scene": "ward_east_b2",
            "type": "empty",
            "name": "FuseAnchor_child",
            "parent": "FuseAnchor",
        },
    }
    values_correct, total_values = exact_match(obj or {}, expected)
    ctx_tokens = usage.get("prompt_tokens", estimate_tokens(user + SYS_T2))
    completion_tokens = usage.get("completion_tokens", estimate_tokens(content))
    print_result("T2", ctx_tokens, json_valid, json_valid,
                 values_correct, total_values, latency_ms, completion_tokens, thinking)


def run_t3(model, ctx_label, thinking):
    context = build_context(NEEDLE_T3, CTX_TARGETS[ctx_label])
    user = (
        "CONTEXT START\n"
        f"{context}\n"
        "CONTEXT END\n\n"
        "Genera un único archivo Python y devuelve SOLO JSON válido.\n\n"
        "Requisitos:\n"
        "- path exacto: tools/build_spawn_manifest.py\n"
        "- incluir función build_manifest(records)\n"
        "- incluir MAX_BATCH = 32\n"
        "- usar sólo stdlib\n"
        '- notes debe listar exactamente los constraint IDs usados y en ese orden: '
        '["C-03","C-07","C-11","C-14"]'
    )
    messages = [
        {"role": "system", "content": SYS_T3},
        {"role": "user", "content": user},
    ]
    content, usage, latency_ms = post_chat(
        model, messages,
        temperature=0.3, max_tokens=5000,
        thinking=thinking, preserve_thinking=False,
    )
    json_valid, obj = parse_json_safe(content)
    values_correct, total_values, compile_ok = eval_t3(obj or {})
    schema_valid = json_valid and compile_ok
    ctx_tokens = usage.get("prompt_tokens", estimate_tokens(user + SYS_T3))
    completion_tokens = usage.get("completion_tokens", estimate_tokens(content))
    print_result("T3", ctx_tokens, json_valid, schema_valid,
                 values_correct, total_values, latency_ms, completion_tokens, thinking)


def run_t4(model, ctx_label, thinking):
    context = build_context(NEEDLE_T4, CTX_TARGETS[ctx_label])

    # Turn 1
    user1 = (
        "Herramientas disponibles:\n"
        '1) query_scene {"scene":"string","name":"string"}\n'
        '2) fire_event {"scene":"string","target":"string","event":"string","payload":{}}\n\n'
        "CONTEXT START\n"
        f"{context}\n"
        "CONTEXT END\n\n"
        "Devuelve la primera tool call correcta del protocolo."
    )
    messages = [
        {"role": "system", "content": SYS_T4},
        {"role": "user", "content": user1},
    ]
    content1, usage1, latency1 = post_chat(
        model, messages,
        temperature=0.2, max_tokens=2048,
        thinking=thinking, preserve_thinking=thinking,
    )
    j1, o1 = parse_json_safe(content1)
    exp1 = {
        "tool": "query_scene",
        "arguments": {
            "scene": "hospital_basement_03",
            "name": "RelayTheta",
        },
    }
    v1, t1 = exact_match(o1 or {}, exp1)

    # Turn 2
    messages2 = messages + [
        {"role": "assistant", "content": content1},
        {
            "role": "user",
            "content": (
                'TOOL RESULT:\n'
                '{"scene":"hospital_basement_03","name":"RelayTheta","status":"offline"}\n\n'
                "Con el mismo protocolo y el resultado anterior, devuelve la siguiente tool call correcta."
            ),
        },
    ]
    content2, usage2, latency2 = post_chat(
        model, messages2,
        temperature=0.2, max_tokens=2048,
        thinking=thinking, preserve_thinking=thinking,
    )
    j2, o2 = parse_json_safe(content2)

    args2 = (o2 or {}).get("arguments", {})
    hits2, total2 = 0, 5
    if (o2 or {}).get("tool") == "fire_event":
        hits2 += 1
    if args2.get("scene") == "hospital_basement_03":
        hits2 += 1
    if args2.get("target") == "RelayTheta":
        hits2 += 1
    if args2.get("event") == "prime_relay":
        hits2 += 1
    if args2.get("payload") == {"amp": 7, "source": "aux_line_B"}:
        hits2 += 1

    json_valid = j1 and j2
    values_correct = v1 + hits2
    total_values = t1 + total2
    ctx_tokens = usage2.get("prompt_tokens", estimate_tokens(user1 + SYS_T4))
    completion_tokens = (
        usage1.get("completion_tokens", 0) + usage2.get("completion_tokens", 0)
    )
    print_result("T4", ctx_tokens, json_valid, json_valid,
                 values_correct, total_values, latency1 + latency2,
                 completion_tokens, thinking)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

RUNNERS = {"T1": run_t1, "T2": run_t2, "T3": run_t3, "T4": run_t4}

def main():
    if len(sys.argv) < 3:
        print("uso: python3 qwen3_runner.py <T1|T2|T3|T4> <4k|8k|16k|24k|32k> [model] [thinking:true|false]")
        print("tests disponibles: T1 T2 T3 T4")
        print("ctx disponibles:   4k 8k 16k 24k 32k")
        sys.exit(1)

    test_id = sys.argv[1].upper()
    ctx_label = sys.argv[2].lower()
    model = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_MODEL
    thinking_arg = sys.argv[4].lower() if len(sys.argv) > 4 else "true"
    thinking = thinking_arg not in ("false", "0", "off")

    if test_id not in RUNNERS:
        print(f"test desconocido: {test_id}. Disponibles: {list(RUNNERS)}")
        sys.exit(1)
    if ctx_label not in CTX_TARGETS:
        print(f"ctx desconocido: {ctx_label}. Disponibles: {list(CTX_TARGETS)}")
        sys.exit(1)

    RUNNERS[test_id](model, ctx_label, thinking)


if __name__ == "__main__":
    main()
