#!/usr/bin/env python3
"""
darkercornner_font.png → DArkkercornner.otf
Pipeline: PIL threshold → row/col projection → potrace SVG → fonttools OTF (CFF)
OTF usa curvas cúbicas — formato nativo de potrace, sin conversión.
"""
import os, sys, re, subprocess, shutil, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

# ── Config ──────────────────────────────────────────────────────────────────
REPO      = Path(__file__).parent.parent
IMG_PATH  = REPO / "assets/logo/darkercornner_font.png"
OUT_DIR   = REPO / "assets/fonts"
POTRACE   = shutil.which("potrace")

FONT_NAME    = "DArkkercornner"
FONT_FAMILY  = "DArkkercornner"
UNITS_PER_EM = 1000
ASCENDER     = 750
DESCENDER    = -250

# Background pixel count per row en el panel (ruido constante del patrón)
BG_ROW_NOISE = 80   # filas con <= esto son fondo
MIN_BAND_H   = 30   # altura mínima de banda para ser considerada fila de letras
MIN_BAND_W   = 20   # ancho mínimo de glifo

UPPERCASE = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LOWERCASE = list("abcdefghijklmnopqrstuvwxyz")

# ── Preprocessing ────────────────────────────────────────────────────────────
def to_binary(img: Image.Image, threshold=80) -> np.ndarray:
    gray = np.array(img.convert("L"))
    return (gray > threshold).astype(np.uint8)

def split_panels(img: Image.Image):
    w, h = img.size
    return img.crop((0, 0, w//2, h)), img.crop((w//2, 0, w, h))

# ── Band detection with absolute threshold ───────────────────────────────────
def find_bands_absolute(proj: np.ndarray, threshold: int, min_size: int, padding=5):
    """Bands where projection > threshold (pixels above bg noise)."""
    bands = []
    in_band = False
    start = 0
    for i, v in enumerate(proj):
        if v > threshold and not in_band:
            start = i; in_band = True
        elif v <= threshold and in_band:
            if i - start >= min_size:
                bands.append((max(0, start - padding), min(len(proj)-1, i + padding)))
            in_band = False
    if in_band and len(proj) - start >= min_size:
        bands.append((max(0, start - padding), len(proj)-1))
    return bands

def segment_panel(img_panel: Image.Image, expected: int, label: str):
    binary = to_binary(img_panel)
    h, w   = binary.shape

    # Row bands — skip title (top 10%)
    content_start = int(h * 0.10)
    row_proj = binary[content_start:, :].sum(axis=1)
    row_bands_rel = find_bands_absolute(row_proj, threshold=BG_ROW_NOISE, min_size=MIN_BAND_H)
    row_bands = [(r0 + content_start, r1 + content_start) for r0, r1 in row_bands_rel]

    # Filter: keep only bands tall enough to be letter rows (>30px), skip tiny sparkles
    letter_bands = [(r0, r1) for r0, r1 in row_bands if (r1 - r0) > MIN_BAND_H * 1.5]

    glyphs = []
    for r0, r1 in letter_bands:
        row_region = binary[r0:r1, :]
        col_proj   = row_region.sum(axis=0)
        col_bands  = find_bands_absolute(col_proj, threshold=max(2, (r1-r0)*0.03),
                                          min_size=MIN_BAND_W, padding=3)
        for c0, c1 in col_bands:
            glyphs.append((c0, r0, c1, r1))

    glyphs.sort(key=lambda g: (g[1], g[0]))
    n = len(glyphs)
    print(f"  [{label}] {n} glyphs found (expected {expected})")
    if n != expected:
        print(f"    ⚠ mismatch — mapping first {min(n, expected)} characters")
    return glyphs

# ── Glyph → potrace → SVG paths ──────────────────────────────────────────────
def glyph_to_binary_pil(img_panel: Image.Image, bbox, pad=15) -> tuple[Image.Image, int, int]:
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(img_panel.width, x1 + pad)
    y1 = min(img_panel.height, y1 + pad)
    crop = img_panel.crop((x0, y0, x1, y1)).convert("L")
    # Threshold → black on white for potrace (potrace traces dark areas)
    bw = crop.point(lambda p: 0 if p > 80 else 255, "L")
    return bw, x1 - x0, y1 - y0

def run_potrace(pil_img: Image.Image) -> str | None:
    bmp = Path(tempfile.mktemp(suffix=".bmp"))
    svg = bmp.with_suffix(".svg")
    pil_img.save(str(bmp))
    result = subprocess.run(
        [POTRACE, "-s", "--flat", str(bmp), "-o", str(svg)],
        capture_output=True, text=True
    )
    bmp.unlink(missing_ok=True)
    if result.returncode != 0 or not svg.exists():
        return None
    content = svg.read_text()
    svg.unlink()
    return content

def extract_svg_paths(svg: str) -> list[str]:
    return re.findall(r'd="([^"]+)"', svg)

# ── SVG path → fonttools pen calls ───────────────────────────────────────────
def draw_svg_path(pen, d: str, scale_x: float, scale_y: float, ascender: int):
    """
    Convert SVG cubic path to fonttools pen calls.
    Flips Y axis: font Y grows upward, SVG Y grows downward.
    """
    def pt(x, y):
        return (x * scale_x, ascender - y * scale_y)

    tokens = re.findall(r'[MmLlCcZz]|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', d)
    i = 0
    cur = (0.0, 0.0)

    while i < len(tokens):
        cmd = tokens[i]; i += 1
        try:
            if cmd == 'M':
                x, y = float(tokens[i]), float(tokens[i+1]); i += 2
                cur = (x, y)
                pen.moveTo(pt(x, y))
            elif cmd == 'm':
                dx, dy = float(tokens[i]), float(tokens[i+1]); i += 2
                cur = (cur[0]+dx, cur[1]+dy)
                pen.moveTo(pt(*cur))
            elif cmd == 'L':
                x, y = float(tokens[i]), float(tokens[i+1]); i += 2
                cur = (x, y)
                pen.lineTo(pt(x, y))
            elif cmd == 'l':
                dx, dy = float(tokens[i]), float(tokens[i+1]); i += 2
                cur = (cur[0]+dx, cur[1]+dy)
                pen.lineTo(pt(*cur))
            elif cmd == 'C':
                p1 = pt(float(tokens[i]),   float(tokens[i+1])); i += 2
                p2 = pt(float(tokens[i]),   float(tokens[i+1])); i += 2
                p3 = pt(float(tokens[i]),   float(tokens[i+1])); i += 2
                cur = (float(tokens[i-2]), float(tokens[i-1]))
                pen.curveTo(p1, p2, p3)
            elif cmd == 'c':
                rx1,ry1 = float(tokens[i]),float(tokens[i+1]); i+=2
                rx2,ry2 = float(tokens[i]),float(tokens[i+1]); i+=2
                rx3,ry3 = float(tokens[i]),float(tokens[i+1]); i+=2
                p1 = pt(cur[0]+rx1, cur[1]+ry1)
                p2 = pt(cur[0]+rx2, cur[1]+ry2)
                p3 = pt(cur[0]+rx3, cur[1]+ry3)
                cur = (cur[0]+rx3, cur[1]+ry3)
                pen.curveTo(p1, p2, p3)
            elif cmd in ('Z', 'z'):
                pen.closePath()
        except (IndexError, ValueError):
            break

# ── Font builder (OTF/CFF) ───────────────────────────────────────────────────
def build_otf(glyph_data: dict):
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.t2CharStringPen import T2CharStringPen

    char_map = {ord(' '): 'space'}
    char_map.update({ord(ch): ch for ch in glyph_data})

    glyph_order = [".notdef", "space"] + list(glyph_data.keys())

    fb = FontBuilder(UNITS_PER_EM, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(char_map)

    # Metrics: (width, lsb)
    metrics = {".notdef": (500, 0), "space": (280, 0)}
    metrics.update({ch: (int(adv), 0) for ch, (_, adv) in glyph_data.items()})
    fb.setupHorizontalMetrics(metrics)

    # Draw glyphs with T2CharStringPen
    charstrings = {}

    # .notdef — simple rectangle
    pen = T2CharStringPen(500, None)
    pen.moveTo((60, 0)); pen.lineTo((440, 0))
    pen.lineTo((440, 700)); pen.lineTo((60, 700)); pen.closePath()
    charstrings[".notdef"] = pen.getCharString()

    # space — empty
    pen = T2CharStringPen(280, None)
    charstrings["space"] = pen.getCharString()

    for ch, (draw_fn, adv) in glyph_data.items():
        pen = T2CharStringPen(int(adv), None)
        try:
            draw_fn(pen)
        except Exception as e:
            print(f"  ⚠ '{ch}' draw error: {e}")
        charstrings[ch] = pen.getCharString()

    fb.setupCFF(
        psName=FONT_NAME,
        fontInfo={"version": "1.0", "FullName": FONT_NAME, "FamilyName": FONT_FAMILY},
        charStringsDict=charstrings,
        privateDict={},
    )

    fb.setupHorizontalHeader(ascent=ASCENDER, descent=DESCENDER)
    fb.setupNameTable({
        "familyName": FONT_FAMILY,
        "styleName": "Regular",
    })
    fb.setupOS2(
        sTypoAscender=ASCENDER, sTypoDescender=DESCENDER,
        usWinAscent=ASCENDER, usWinDescent=abs(DESCENDER),
        fsType=0, achVendID="DKCS"
    )
    fb.setupPost()
    fb.setupHead(unitsPerEm=UNITS_PER_EM)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{FONT_NAME}.otf"
    fb.font.save(str(out))
    return out

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not POTRACE:
        sys.exit("❌ potrace not found — brew install potrace")

    print(f"📂 Loading {IMG_PATH} ...")
    img = Image.open(IMG_PATH)
    print(f"   Size: {img.size[0]}×{img.size[1]}")

    left_img, right_img = split_panels(img)

    print("\n🔠 Segmenting panels ...")
    up_bboxes = segment_panel(left_img,  26, "UPPERCASE")
    lo_bboxes = segment_panel(right_img, 26, "lowercase")

    glyph_data = {}

    def process(img_panel, bboxes, chars):
        for char, bbox in zip(chars, bboxes):
            bw, gw, gh = glyph_to_binary_pil(img_panel, bbox)
            svg = run_potrace(bw)
            if not svg:
                print(f"  '{char}': potrace failed"); continue

            paths = extract_svg_paths(svg)
            if not paths:
                print(f"  '{char}': no paths"); continue

            # Scale: map pixel height → font units
            scale = (ASCENDER - DESCENDER) / gh
            scale_x = scale
            scale_y = scale
            advance = int(gw * scale_x) + 40

            def make_draw(paths=paths, sx=scale_x, sy=scale_y, asc=ASCENDER):
                def draw(pen):
                    for d in paths:
                        draw_svg_path(pen, d, sx, sy, asc)
                return draw

            glyph_data[char] = (make_draw(), advance)
            print(f"  '{char}': {len(paths)} contour(s)  adv={advance}")

    print("\n✏️  Processing glyphs ...")
    process(left_img,  up_bboxes, UPPERCASE)
    process(right_img, lo_bboxes, LOWERCASE)

    if not glyph_data:
        sys.exit("❌ No glyphs extracted.")

    print(f"\n🔧 Building OTF ({len(glyph_data)}/52 glyphs) ...")
    out = build_otf(glyph_data)
    print(f"\n✅ Font saved → {out}")
    print(f"   Install: double-click {out} en Mac o Windows")

if __name__ == "__main__":
    main()
