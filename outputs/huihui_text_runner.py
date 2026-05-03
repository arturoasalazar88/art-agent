#!/usr/bin/env python3
"""
STORY_025 - Huihui sin mmproj: suite T1-T4 x 5 ctx-sizes.

Uso:
  python3 huihui_text_runner.py <T1|T2|T3|T4> <4k|8k|16k|24k|32k> [thinking:true|false]
"""
from __future__ import annotations

import json
import sys
import time
from typing import Any

import requests


BASE_URL = "http://localhost:8014/v1/chat/completions"

CTX_SIZES = {
    "4k": 4096,
    "8k": 8192,
    "16k": 16384,
    "24k": 24576,
    "32k": 32768,
}

FILLER_BLOCKS = [
    """
Las criaturas del nivel subterráneo operan en ciclos de actividad estrictos. ENTITY_031
tiene hibernación cada 20 minutos. Su radio auditivo alcanza 40 metros en silencio total.
Los corredores del Sector B están infestados, solo repelibles con frecuencia 18kHz.
La temperatura óptima para su actividad es entre 12°C y 15°C. Por encima de 20°C
entran en estado latente. Su piel segrega una toxina paralizante de contacto.
""",
    """
El archivo SIGMA-7 documenta los experimentos del Dr. Voss entre 1987 y 1991.
Las 47 páginas describen modificaciones genéticas fallidas en sujetos voluntarios.
El laboratorio fue sellado tras el incidente del 14 de marzo de 1991.
Solo tres investigadores sobrevivieron. Ninguno habló públicamente sobre lo ocurrido.
Los registros originales fueron transferidos al Archivo Central bajo clasificación máxima.
""",
    """
El sistema de ventilación del complejo tiene tres niveles de filtrado. El nivel primario
elimina partículas mayores a 10 micrones. El secundario neutraliza agentes biológicos.
El terciario, instalado en 1994, fue diseñado para un patógeno específico no documentado.
Los sensores de presión en los ductos principales registran anomalías cada 72 horas.
El equipo de mantenimiento tiene prohibido acceder al nivel B-4 sin escolta armada.
""",
    """
La arquitectura del bunker sigue el patrón de construcción soviético de los años 60.
Paredes de hormigón reforzado de 80 cm. Puertas de acero de 12 toneladas en cada nivel.
El generador principal puede operar 6 meses sin reabastecimiento. El secundario, 3 semanas.
Los planos originales muestran una sala no documentada entre los niveles 3 y 4.
El acceso fue soldado en 1973 por razones que no aparecen en ningún registro oficial.
""",
]


def build_filler(target_tokens: int) -> str:
    target_words = int(target_tokens * 0.75)
    filler = ""
    i = 0
    while len(filler.split()) < target_words:
        filler += FILLER_BLOCKS[i % len(FILLER_BLOCKS)] + "\n"
        i += 1
    return filler


def inject_needle(filler: str, needle: str) -> str:
    words = filler.split()
    pos = int(len(words) * 0.85)
    words.insert(pos, f"\n[REGISTRO CLASIFICADO: {needle}]\n")
    return " ".join(words)


def call(
    messages: list[dict[str, Any]],
    max_tokens: int = 512,
    temperature: float = 0.0,
    thinking: bool = True,
    timeout: int = 300,
) -> tuple[str | None, str | None, float, str | None, dict[str, Any]]:
    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "chat_template_kwargs": {"enable_thinking": thinking},
    }
    t0 = time.time()
    response = requests.post(BASE_URL, json=payload, timeout=timeout)
    elapsed = round(time.time() - t0, 2)
    data = response.json()
    if "error" in data:
        return None, None, elapsed, str(data["error"]), data
    msg = data["choices"][0]["message"]
    return msg.get("content", ""), msg.get("reasoning_content", ""), elapsed, None, data


def print_usage(data: dict[str, Any]) -> None:
    usage = data.get("usage") or {}
    if usage:
        print(f"  Usage: {json.dumps(usage, ensure_ascii=False)}")


def check_thinking(reasoning: str | None, label: str) -> bool:
    if not reasoning:
        print(f"  FAIL {label}: reasoning_content AUSENTE")
        return False
    print(f"  OK {label}: reasoning presente ({len(reasoning.split())} palabras)")
    return True


def extract_json(content: str) -> Any:
    start = content.find("{")
    end = content.rfind("}") + 1
    if start < 0 or end <= start:
        raise ValueError("no JSON object found")
    return json.loads(content[start:end])


def run_t1(ctx_label: str, thinking: bool) -> bool:
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'=' * 60}\nT1 - Extracción JSON | ctx={ctx_label} | thinking={thinking}\n{'=' * 60}")
    needle = "asset_id: PROP_DOOR_RUSTED_042, material: oxidized_iron, height_m: 2.1, limb_count: 0"
    prompt = f"""Contexto del proyecto:
{inject_needle(build_filler(int(ctx * 0.80)), needle)}

Tarea: Extrae del contexto los datos del asset registrado y devuelve SOLO este JSON, sin explicación:
{{
  "asset_id": "...",
  "material": "...",
  "height_m": 0.0,
  "limb_count": 0
}}"""
    content, reasoning, elapsed, err, data = call([{"role": "user", "content": prompt}], thinking=thinking)
    if err:
        print(f"  ERROR: {err}")
        return False
    print(f"  Tiempo: {elapsed}s")
    print_usage(data)
    thinking_ok = check_thinking(reasoning, "T1")
    try:
        obj = extract_json(content or "")
        checks = [
            obj.get("asset_id") == "PROP_DOOR_RUSTED_042",
            obj.get("material") == "oxidized_iron",
            obj.get("height_m") == 2.1,
            obj.get("limb_count") == 0,
        ]
        passed = sum(checks)
        print("  JSON válido: OK")
        print(f"  Valores correctos: {passed}/4")
        ok = passed == 4 and thinking_ok
        print(f"  Resultado: {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as exc:
        print(f"  JSON inválido: {exc}")
        print(f"  Content: {(content or '')[:300]}")
        return False


def run_t2(ctx_label: str, thinking: bool) -> bool:
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'=' * 60}\nT2 - Tool call MCP | ctx={ctx_label} | thinking={thinking}\n{'=' * 60}")
    needle = "job_id: JOB_SCENE_019, action: place_object, prefab: prefab_altar_broken, position: [12.5, 0.0, -8.3]"
    prompt = f"""Eres un orquestador Unity MCP. Tienes acceso a la herramienta place_object(job_id, prefab, x, y, z).

Contexto del proyecto:
{inject_needle(build_filler(int(ctx * 0.80)), needle)}

Tarea: Ejecuta la acción registrada en el contexto. Devuelve SOLO este JSON con los parámetros exactos encontrados:
{{
  "tool": "place_object",
  "job_id": "...",
  "prefab": "...",
  "position": [0.0, 0.0, 0.0]
}}"""
    content, reasoning, elapsed, err, data = call([{"role": "user", "content": prompt}], thinking=thinking)
    if err:
        print(f"  ERROR: {err}")
        return False
    print(f"  Tiempo: {elapsed}s")
    print_usage(data)
    thinking_ok = check_thinking(reasoning, "T2")
    try:
        obj = extract_json(content or "")
        checks = [
            obj.get("tool") == "place_object",
            obj.get("job_id") == "JOB_SCENE_019",
            obj.get("prefab") == "prefab_altar_broken",
            obj.get("position") == [12.5, 0.0, -8.3],
        ]
        passed = sum(checks)
        print("  JSON válido: OK")
        print(f"  Valores correctos: {passed}/4")
        ok = passed == 4 and thinking_ok
        print(f"  Resultado: {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as exc:
        print(f"  JSON inválido: {exc}")
        print(f"  Content: {(content or '')[:300]}")
        return False


def run_t3(ctx_label: str, thinking: bool) -> bool:
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'=' * 60}\nT3 - Codegen | ctx={ctx_label} | thinking={thinking}\n{'=' * 60}")
    needle = "función requerida: build_asset_manifest(records), retorna dict con keys: assets, by_type, warnings"
    prompt = f"""Eres un ingeniero Python senior en un proyecto de videojuego.

Contexto del proyecto:
{inject_needle(build_filler(int(ctx * 0.80)), needle)}

Tarea: Implementa en Python 3.11 la función especificada en el contexto.
- Entrada: list[dict], cada record tiene: id (str), type (str: texture|model|audio|script), path (str)
- Salida: dict con keys assets (list), by_type (dict con conteos), warnings (list)
- Ignora records sin id/type/path y agrega warning
- No mutar records originales

Responde SOLO con el bloque de código Python, sin explicación."""
    content, reasoning, elapsed, err, data = call(
        [{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0.2,
        thinking=thinking,
        timeout=400,
    )
    if err:
        print(f"  ERROR: {err}")
        return False
    print(f"  Tiempo: {elapsed}s")
    print_usage(data)
    thinking_ok = check_thinking(reasoning, "T3")
    checks = [
        "def build_asset_manifest(" in (content or ""),
        '"assets"' in (content or "") or "'assets'" in (content or ""),
        '"by_type"' in (content or "") or "'by_type'" in (content or ""),
        '"warnings"' in (content or "") or "'warnings'" in (content or ""),
        "return" in (content or ""),
    ]
    passed = sum(checks)
    print(f"  Checks: {passed}/5")
    ok = passed >= 4 and thinking_ok
    print(f"  Resultado: {'PASS' if ok else 'FAIL'}")
    return ok


def run_t4(ctx_label: str, thinking: bool) -> bool:
    ctx = CTX_SIZES[ctx_label]
    print(f"\n{'=' * 60}\nT4 - Multi-turn estado | ctx={ctx_label} | thinking={thinking}\n{'=' * 60}")
    needle = "personaje: Elena Voss, tiene_radio: true, arma: cuchillo, ubicacion: Sector_C"
    context = inject_needle(build_filler(int(ctx * 0.75)), needle)
    t1_prompt = f"""Contexto del proyecto:
{context}

Extrae el estado del personaje registrado en el contexto. Devuelve SOLO este JSON:
{{
  "nombre": "...",
  "tiene_radio": true,
  "arma": "...",
  "ubicacion": "..."
}}"""
    content1, reasoning1, elapsed1, err, data1 = call([{"role": "user", "content": t1_prompt}], thinking=thinking)
    if err:
        print(f"  T4-T1 ERROR: {err}")
        return False
    print(f"  T4-Turno1 tiempo: {elapsed1}s")
    print_usage(data1)
    thinking1_ok = check_thinking(reasoning1, "T4-T1")
    try:
        state = extract_json(content1 or "")
        print(f"  Estado extraído: {state}")
        t1_ok = (
            state.get("nombre") == "Elena Voss"
            and state.get("tiene_radio") is True
            and state.get("arma") == "cuchillo"
        )
    except Exception as exc:
        print(f"  T4-T1 JSON inválido: {exc}")
        t1_ok = False
    print(f"  T4-T1: {'PASS' if t1_ok and thinking1_ok else 'FAIL'}")

    t2_prompt = "Elena cruza el Sector_D y pierde la radio al caer en una trampa. Actualiza su estado y devuelve el JSON completo con los mismos campos."
    content2, reasoning2, elapsed2, err, data2 = call(
        [
            {"role": "user", "content": t1_prompt},
            {"role": "assistant", "content": content1 or ""},
            {"role": "user", "content": t2_prompt},
        ],
        thinking=thinking,
    )
    if err:
        print(f"  T4-T2 ERROR: {err}")
        return False
    print(f"  T4-Turno2 tiempo: {elapsed2}s")
    print_usage(data2)
    thinking2_ok = check_thinking(reasoning2, "T4-T2")
    try:
        state2 = extract_json(content2 or "")
        print(f"  Estado T2: {state2}")
        t2_ok = (
            state2.get("tiene_radio") is False
            and state2.get("arma") == "cuchillo"
            and state2.get("ubicacion") == "Sector_D"
        )
    except Exception as exc:
        print(f"  T4-T2 JSON inválido: {exc}")
        t2_ok = False
    print(f"  T4-T2: {'PASS' if t2_ok and thinking2_ok else 'FAIL'}")
    ok = t1_ok and t2_ok and thinking1_ok and thinking2_ok
    print(f"  Resultado T4: {'PASS' if ok else 'FAIL'}")
    return ok


TESTS = {"T1": run_t1, "T2": run_t2, "T3": run_t3, "T4": run_t4}


def main() -> int:
    if len(sys.argv) < 3:
        print("Uso: python3 huihui_text_runner.py <T1|T2|T3|T4> <4k|8k|16k|24k|32k> [thinking:true|false]")
        return 1
    test_name = sys.argv[1].upper()
    ctx_label = sys.argv[2].lower()
    thinking_arg = sys.argv[3].lower() if len(sys.argv) > 3 else "thinking:true"
    thinking = "false" not in thinking_arg
    if test_name not in TESTS:
        print(f"Test desconocido: {test_name}. Opciones: T1 T2 T3 T4")
        return 1
    if ctx_label not in CTX_SIZES:
        print(f"ctx desconocido: {ctx_label}. Opciones: 4k 8k 16k 24k 32k")
        return 1
    return 0 if TESTS[test_name](ctx_label, thinking) else 1


if __name__ == "__main__":
    raise SystemExit(main())
