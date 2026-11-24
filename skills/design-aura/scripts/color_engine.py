#!/usr/bin/env python3
"""Motor de cor da Design Aura (stdlib, OKLCH).

Gera um tokens.json completo a partir da cor da marca:
- escalas de 12 degraus (marca, acento e neutro) com funcao por degrau;
- neutros tingidos pela matiz da marca (coesao sem monobloco cinza);
- semanticas com familia de matiz fixa (vermelho, verde, ambar) e energia ajustada a marca;
- Dark derivado das mesmas escalas, com elevacao mais clara por plano;
- planos Z0-Z4 e bordas conforme o estilo de profundidade da direcao;
- paleta de graficos com luminosidade parecida e checagem de daltonismo.

O resultado passa pelo mesmo pipeline (generate_tokens.py -> tokens.css -> audit_contrast.py).
"""
from __future__ import annotations

import math
import re

# ------------------------------------------------------------------ conversoes


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02X}" for c in rgb)


def linear_rgb_to_oklab(r: float, g: float, b: float) -> tuple[float, float, float]:
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    r, g, b = (_srgb_to_linear(c) for c in hex_to_rgb(hex_color))
    L, a, bb = linear_rgb_to_oklab(r, g, b)
    C = math.hypot(a, bb)
    H = math.degrees(math.atan2(bb, a)) % 360
    return L, C, H


def _in_gamut(rgb: tuple[float, float, float]) -> bool:
    return all(-1e-4 <= c <= 1 + 1e-4 for c in rgb)


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """Converte para sRGB reduzindo croma ate caber no gamut (preserva L e H)."""
    L = max(0.0, min(1.0, L))
    lo, hi = 0.0, max(0.0, C)
    best = (L, 0.0)
    for _ in range(24):
        mid = hi if lo == hi else (lo + hi) / 2
        a, b = mid * math.cos(math.radians(H)), mid * math.sin(math.radians(H))
        lin = oklab_to_linear_rgb(L, a, b)
        if _in_gamut(lin):
            best = (L, mid)
            if mid >= C - 1e-6:
                break
            lo = mid
        else:
            hi = mid
    a, b = best[1] * math.cos(math.radians(H)), best[1] * math.sin(math.radians(H))
    lin = oklab_to_linear_rgb(best[0], a, b)
    return rgb_to_hex(tuple(_linear_to_srgb(max(0.0, min(1.0, c))) for c in lin))  # type: ignore[arg-type]


CSS_NAMED = {
    "aliceblue": "#F0F8FF",
    "antiquewhite": "#FAEBD7",
    "aqua": "#00FFFF",
    "aquamarine": "#7FFFD4",
    "azure": "#F0FFFF",
    "beige": "#F5F5DC",
    "bisque": "#FFE4C4",
    "black": "#000000",
    "blanchedalmond": "#FFEBCD",
    "blue": "#0000FF",
    "blueviolet": "#8A2BE2",
    "brown": "#A52A2A",
    "burlywood": "#DEB887",
    "cadetblue": "#5F9EA0",
    "chartreuse": "#7FFF00",
    "chocolate": "#D2691E",
    "coral": "#FF7F50",
    "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC",
    "crimson": "#DC143C",
    "cyan": "#00FFFF",
    "darkblue": "#00008B",
    "darkcyan": "#008B8B",
    "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9",
    "darkgreen": "#006400",
    "darkgrey": "#A9A9A9",
    "darkkhaki": "#BDB76B",
    "darkmagenta": "#8B008B",
    "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00",
    "darkorchid": "#9932CC",
    "darkred": "#8B0000",
    "darksalmon": "#E9967A",
    "darkseagreen": "#8FBC8F",
    "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F",
    "darkslategrey": "#2F4F4F",
    "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3",
    "deeppink": "#FF1493",
    "deepskyblue": "#00BFFF",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1E90FF",
    "firebrick": "#B22222",
    "floralwhite": "#FFFAF0",
    "forestgreen": "#228B22",
    "fuchsia": "#FF00FF",
    "gainsboro": "#DCDCDC",
    "ghostwhite": "#F8F8FF",
    "gold": "#FFD700",
    "goldenrod": "#DAA520",
    "gray": "#808080",
    "green": "#008000",
    "greenyellow": "#ADFF2F",
    "grey": "#808080",
    "honeydew": "#F0FFF0",
    "hotpink": "#FF69B4",
    "indianred": "#CD5C5C",
    "indigo": "#4B0082",
    "ivory": "#FFFFF0",
    "khaki": "#F0E68C",
    "lavender": "#E6E6FA",
    "lavenderblush": "#FFF0F5",
    "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD",
    "lightblue": "#ADD8E6",
    "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF",
    "lightgoldenrodyellow": "#FAFAD2",
    "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90",
    "lightgrey": "#D3D3D3",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightseagreen": "#20B2AA",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0",
    "lime": "#00FF00",
    "limegreen": "#32CD32",
    "linen": "#FAF0E6",
    "magenta": "#FF00FF",
    "maroon": "#800000",
    "mediumaquamarine": "#66CDAA",
    "mediumblue": "#0000CD",
    "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB",
    "mediumseagreen": "#3CB371",
    "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A",
    "mediumturquoise": "#48D1CC",
    "mediumvioletred": "#C71585",
    "midnightblue": "#191970",
    "mintcream": "#F5FFFA",
    "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "navy": "#000080",
    "oldlace": "#FDF5E6",
    "olive": "#808000",
    "olivedrab": "#6B8E23",
    "orange": "#FFA500",
    "orangered": "#FF4500",
    "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA",
    "palegreen": "#98FB98",
    "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093",
    "papayawhip": "#FFEFD5",
    "peachpuff": "#FFDAB9",
    "peru": "#CD853F",
    "pink": "#FFC0CB",
    "plum": "#DDA0DD",
    "powderblue": "#B0E0E6",
    "purple": "#800080",
    "rebeccapurple": "#663399",
    "red": "#FF0000",
    "rosybrown": "#BC8F8F",
    "royalblue": "#4169E1",
    "saddlebrown": "#8B4513",
    "salmon": "#FA8072",
    "sandybrown": "#F4A460",
    "seagreen": "#2E8B57",
    "seashell": "#FFF5EE",
    "sienna": "#A0522D",
    "silver": "#C0C0C0",
    "skyblue": "#87CEEB",
    "slateblue": "#6A5ACD",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#FFFAFA",
    "springgreen": "#00FF7F",
    "steelblue": "#4682B4",
    "tan": "#D2B48C",
    "teal": "#008080",
    "thistle": "#D8BFD8",
    "tomato": "#FF6347",
    "turquoise": "#40E0D0",
    "violet": "#EE82EE",
    "wheat": "#F5DEB3",
    "white": "#FFFFFF",
    "whitesmoke": "#F5F5F5",
    "yellow": "#FFFF00",
    "yellowgreen": "#9ACD32",
}


def _num(token: str, scale: float = 1.0) -> float:
    token = token.strip()
    if token.endswith("%"):
        return float(token[:-1]) / 100 * scale
    return float(token)


def parse_color(value: str) -> str:
    """Aceita #rgb, #rrggbb(aa), rgb()/rgba(), hsl(), oklch() e nomes CSS. Devolve #RRGGBB.

    Erro claro quando o formato nao e reconhecido, em vez de quebrar mais adiante."""
    raw = str(value or "").strip()
    low = raw.lower()
    if low in CSS_NAMED:
        return CSS_NAMED[low]
    m = re.fullmatch(r"#?([0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})", low)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h[:3])
        return "#" + h[:6].upper()
    m = re.fullmatch(r"(rgba?|hsla?|oklch)\(\s*([^)]*)\)", low)
    if m:
        fn, args = m.group(1), [a for a in re.split(r"[\s,/]+", m.group(2).strip()) if a]
        try:
            if fn.startswith("rgb") and len(args) >= 3:
                return rgb_to_hex(tuple(max(0.0, min(1.0, _num(a, 255) / 255 if a.endswith("%") else float(a) / 255)) for a in args[:3]))  # type: ignore[arg-type]
            if fn.startswith("hsl") and len(args) >= 3:
                h = float(args[0].replace("deg", "")) % 360
                sat, lig = _num(args[1] if args[1].endswith("%") else args[1] + "%"), _num(args[2] if args[2].endswith("%") else args[2] + "%")
                c = (1 - abs(2 * lig - 1)) * sat
                x = c * (1 - abs((h / 60) % 2 - 1))
                r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
                mm = lig - c / 2
                return rgb_to_hex((r + mm, g + mm, b + mm))
            if fn == "oklch" and len(args) >= 3:
                L = _num(args[0]) if args[0].endswith("%") else float(args[0])
                L = L / 100 if L > 1.0 else L
                C = _num(args[1], 0.4) if args[1].endswith("%") else float(args[1])
                return oklch_to_hex(L, C, float(args[2].replace("deg", "")))
        except ValueError:
            pass
    raise ValueError(f"Cor nao reconhecida: '{value}'. Use #RRGGBB, rgb(), hsl(), oklch(L C H) ou um nome CSS.")


# ------------------------------------------------------------------ contraste

def relative_luminance(hex_color: str) -> float:
    r, g, b = (_srgb_to_linear(c) for c in hex_to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag(fg: str, bg: str) -> float:
    a, b = relative_luminance(fg), relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def apca(fg: str, bg: str) -> float:
    """APCA-W3 (mesma formula do audit_contrast.py), em |Lc|."""
    def y(hex_color: str) -> float:
        r, g, b = (c ** 2.4 for c in hex_to_rgb(hex_color))
        v = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        return v if v > 0.022 else v + (0.022 - v) ** 1.414
    yt, yb = y(fg), y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        sapc = (yb ** 0.56 - yt ** 0.57) * 1.14
        lc = 0.0 if sapc < 0.1 else sapc - 0.027
    else:
        sapc = (yb ** 0.65 - yt ** 0.62) * 1.14
        lc = 0.0 if sapc > -0.1 else sapc + 0.027
    return abs(lc * 100)


def passes(fg: str, bg: str, wcag_min: float, apca_min: float) -> bool:
    return wcag(fg, bg) >= wcag_min and apca(fg, bg) >= apca_min


def ensure_contrast(L: float, C: float, H: float, bg: str, target: float, direction: int, apca_min: float = 60.0) -> str:
    """Move a luminosidade (direction -1 escurece, +1 clareia) ate atingir WCAG e APCA."""
    for _ in range(100):
        candidate = oklch_to_hex(L, C, H)
        if passes(candidate, bg, target, apca_min):
            return candidate
        L = max(0.0, min(1.0, L + 0.01 * direction))
    return oklch_to_hex(L, C, H)


LIGHT_ON = "#FFFFFF"
DARK_ON = "#101114"


def fit_solid(seed_hex: str, wcag_min: float = 4.5, apca_min: float = 60.0) -> tuple[str, str]:
    """Ajusta a luminosidade da cor solida o minimo possivel para o texto (branco ou escuro) passar WCAG e APCA.

    Preserva a identidade: escolhe a direcao (escurecer com texto branco ou clarear com texto escuro)
    que exige o menor deslocamento a partir da semente."""
    L0, C, H = hex_to_oklch(seed_hex)
    best = None
    for on, direction in ((LIGHT_ON, -1), (DARK_ON, +1)):
        L = L0
        for step in range(0, 60):
            cand = oklch_to_hex(L, C, H)
            if passes(on, cand, wcag_min, apca_min):
                if best is None or step < best[0]:
                    best = (step, cand, on)
                break
            L = max(0.0, min(1.0, L + 0.01 * direction))
    if best is None:
        return seed_hex.upper(), LIGHT_ON
    return best[1], best[2]


def best_on(color: str, light: str = LIGHT_ON, dark: str = DARK_ON) -> str:
    return light if apca(light, color) >= apca(dark, color) else dark


# ------------------------------------------------------------------ escalas

LIGHT_STEPS = [0.990, 0.975, 0.945, 0.915, 0.880, 0.835, 0.770, 0.690, None, None, 0.480, 0.260]
DARK_STEPS = [0.170, 0.200, 0.245, 0.280, 0.315, 0.360, 0.425, 0.520, None, None, 0.810, 0.945]
CHROMA_PROFILE = [0.10, 0.16, 0.28, 0.40, 0.52, 0.64, 0.78, 0.92, 1.0, 1.0, 0.82, 0.42]


def ramp(seed_hex: str, theme: str = "light", chroma_scale: float = 1.0) -> list[str]:
    """Escala de 12 degraus: 1-2 fundos, 3-5 elementos, 6-8 bordas, 9-10 solido, 11-12 texto."""
    L0, C0, H = hex_to_oklch(seed_hex)
    C0 = C0 * chroma_scale
    steps = LIGHT_STEPS if theme == "light" else DARK_STEPS
    out = []
    for i, lt in enumerate(steps):
        if i == 8:
            sL = L0 if theme == "light" else max(L0, 0.62)
            out.append(oklch_to_hex(sL, C0, H) if theme == "dark" or chroma_scale != 1.0 else seed_hex.upper())
            continue
        if i == 9:
            sL = (L0 - 0.05) if theme == "light" else max(L0, 0.62) + 0.05
            out.append(oklch_to_hex(sL, C0, H))
            continue
        out.append(oklch_to_hex(lt, C0 * CHROMA_PROFILE[i], H))
    return out


HARMONIES = {
    "complementar": 180, "complementary": 180,
    "analoga": 32, "analogous": 32,
    "dividida": 150, "split": 150,
    "triade": 120, "triad": 120,
    "mono": 0, "monochrome": 0,
}


def derive_accent(seed_hex: str, harmony: str) -> str:
    L, C, H = hex_to_oklch(seed_hex)
    if C < ACHROMATIC_C:
        return oklch_to_hex(0.64, 0.17, ACHROMATIC_ACCENT_HUE)
    shift = HARMONIES.get(harmony, 180)
    if shift == 0:
        return oklch_to_hex(min(0.72, L + 0.18), max(C, 0.16) * 1.15, H)
    return oklch_to_hex(0.66, max(0.14, min(0.20, C * 1.1)), (H + shift) % 360)


SEMANTIC_HUES = {"danger": 27.0, "success": 150.0, "warning": 72.0, "info": 245.0}
ACHROMATIC_C = 0.03          # abaixo disso a "matiz" da semente e ruido (preto, branco, cinza)
ACHROMATIC_ACCENT_HUE = 35.0  # acento padrao de marca monocromatica; a direcao deve informar o seu


def semantic_seed(role: str, brand_hex: str, theme: str) -> tuple[float, float, float]:
    _, bc, bh = hex_to_oklch(brand_hex)
    hue = SEMANTIC_HUES[role]
    if role == "info" and bc > ACHROMATIC_C and (200 <= bh <= 275):
        hue = bh  # marca azulada: info usa a propria marca
    # puxa a matiz ate 6 graus na direcao da marca, sem sair da familia (so se a marca tiver matiz)
    if bc > ACHROMATIC_C:
        delta = ((bh - hue + 540) % 360) - 180
        hue = (hue + max(-6.0, min(6.0, delta * 0.08))) % 360
    chroma = max(0.11, min(0.19, bc * 1.05 if bc > 0.04 else 0.15))
    if role == "warning":
        chroma = max(chroma, 0.14)
    L = {"light": 0.54, "dark": 0.68}[theme]
    if role == "warning":
        L = {"light": 0.58, "dark": 0.78}[theme]
    return L, chroma, hue


# ------------------------------------------------------------------ daltonismo

MACHADO = {
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
}


def _oklab_of(hex_color: str, matrix=None) -> tuple[float, float, float]:
    r, g, b = (_srgb_to_linear(c) for c in hex_to_rgb(hex_color))
    if matrix:
        r, g, b = (sum(m * v for m, v in zip(row, (r, g, b))) for row in matrix)
        r, g, b = (max(0.0, min(1.0, v)) for v in (r, g, b))
    return linear_rgb_to_oklab(r, g, b)


def min_distance(colors: list[str], vision: str | None = None) -> float:
    pts = [_oklab_of(c, MACHADO.get(vision) if vision else None) for c in colors]
    best = 9.0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            best = min(best, math.dist(pts[i], pts[j]))
    return round(best, 4)


def chart_palette(brand_hex: str, theme: str, n: int = 6) -> list[str]:
    _, bc, bh = hex_to_oklch(brand_hex)
    base_L = 0.60 if theme == "light" else 0.74
    chroma = max(0.11, min(0.16, bc if bc > 0.05 else 0.13))
    hues = [(bh + i * 360 / n) % 360 for i in range(n)]
    best_set, best_score = None, -1.0
    for offset in (0, 15, 30, 45):
        for zig in (0.0, 0.06, 0.1):
            cols = [oklch_to_hex(base_L + (zig if i % 2 else -zig / 2), chroma, (h + offset) % 360) for i, h in enumerate(hues)]
            cols[0] = oklch_to_hex(base_L, chroma, bh)
            score = min(min_distance(cols), min_distance(cols, "deuteranopia"), min_distance(cols, "protanopia"))
            if score > best_score:
                best_set, best_score = cols, score
    return best_set or []


# ------------------------------------------------------------------ planos por estilo de profundidade

SURFACES = {
    # (z0, z1, z2, z3, z4, border, border_strong) em L do OKLCH
    "tactile": {"light": (0.885, 0.925, 1.0, 0.958, 1.0, 0.715, 0.560), "dark": (0.150, 0.180, 0.225, 0.268, 0.310, 0.385, 0.490)},
    "hairline": {"light": (0.935, 0.975, 1.0, 0.985, 1.0, 0.890, 0.720), "dark": (0.150, 0.170, 0.200, 0.235, 0.265, 0.330, 0.450)},
    "soft": {"light": (0.940, 0.968, 1.0, 1.0, 1.0, 0.925, 0.780), "dark": (0.150, 0.175, 0.210, 0.245, 0.280, 0.300, 0.420)},
    "tonal": {"light": (0.930, 0.978, 0.952, 0.935, 0.920, 0.900, 0.760), "dark": (0.145, 0.175, 0.215, 0.250, 0.285, 0.290, 0.420)},
}


# Densidade muda a escala de espaco, a altura de controle e de linha e o texto base.
DENSITY = {
    "compact": {"space": ("4px", "6px", "8px", "12px", "16px", "20px", "24px", "32px", "40px", "48px"),
                "sizing": {"control-h": "32px", "row-h": "36px", "touch-min": "44px"}, "text-base": "15px"},
    "regular": {"space": ("4px", "8px", "12px", "16px", "20px", "24px", "32px", "40px", "48px", "64px"),
                "sizing": {"control-h": "38px", "row-h": "44px", "touch-min": "44px"}, "text-base": "16px"},
    "airy": {"space": ("4px", "8px", "12px", "16px", "24px", "32px", "40px", "48px", "64px", "96px"),
             "sizing": {"control-h": "44px", "row-h": "52px", "touch-min": "48px"}, "text-base": "17px"},
}


def _hardest_bg(a: str, b: str, theme: str) -> str:
    """O fundo mais exigente para um traco: no Light o traco e escuro, entao o fundo mais escuro;
    no Dark o traco e claro, entao o fundo mais claro."""
    la, lb = relative_luminance(a), relative_luminance(b)
    if theme == "light":
        return a if la <= lb else b
    return a if la >= lb else b


def build_tokens(seed: str, accent: str | None = None, harmony: str = "complementar", depth_style: str = "hairline",
                 neutral_tint: float = 0.012, brand: str = "Projeto", default_theme: str = "light",
                 fonts: dict | None = None, density: str = "regular") -> dict:
    seed = parse_color(seed)
    accent = parse_color(accent) if accent else derive_accent(seed, harmony)
    _, sc, sh = hex_to_oklch(seed)
    achromatic = sc < ACHROMATIC_C
    style = depth_style if depth_style in SURFACES else "hairline"

    semantic: dict[str, dict[str, str]] = {}
    report = {"seed": seed, "accent": accent, "harmony": harmony, "depth_style": style, "checks": {}, "notes": []}
    if achromatic:
        report["notes"].append("Semente acromática (preto, branco ou cinza): neutros sem tinta, primária em tinta "
                               "(quase preto no Light, quase branco no Dark). Defina o acento na direção.")
    chart_seed = accent if achromatic else seed
    for theme in ("light", "dark"):
        t: dict[str, str] = {}
        z = SURFACES[style][theme]
        tint = 0.0 if achromatic else (neutral_tint if theme == "light" else neutral_tint * 1.5)
        for i, key in enumerate(("surface-z0", "surface-z1", "surface-z2", "surface-z3", "surface-z4")):
            L = z[i]
            t[key] = "#FFFFFF" if L >= 0.999 else oklch_to_hex(L, tint, sh)
        canvas, card = t["surface-z1"], t["surface-z2"]
        t["border-subtle"] = oklch_to_hex(z[5], tint * 2.2, sh)
        t["border-strong"] = oklch_to_hex(z[6], tint * 2.4, sh)
        if theme == "light":
            t["text-strong"] = ensure_contrast(0.20, tint * 2, sh, card, 12.0, -1, 75.0)
            t["text-body"] = ensure_contrast(0.30, tint * 2, sh, canvas, 8.0, -1, 70.0)
            darkest = min((t[k] for k in ("surface-z0", "surface-z1", "surface-z3")), key=relative_luminance)
            t["text-muted"] = ensure_contrast(0.47, tint * 2.5, sh, darkest, 4.8, -1, 62.0)
        else:
            t["text-strong"] = ensure_contrast(0.955, tint, sh, card, 12.0, +1, 75.0)
            t["text-body"] = ensure_contrast(0.880, tint, sh, card, 8.0, +1, 70.0)
            muted_bg = t["surface-z3"]
            t["text-muted"] = ensure_contrast(0.740, tint * 1.5, sh, muted_bg, 4.8, +1, 62.0)

        brand_ramp = ramp(seed, theme)
        accent_ramp = ramp(accent, theme)
        if achromatic:
            # Marca monocromatica vira tinta: nunca #000000 cru nem um cinza medio apagado.
            primary = oklch_to_hex(0.24, 0.0, 0.0) if theme == "light" else oklch_to_hex(0.93, 0.0, 0.0)
            on_primary = best_on(primary)
        else:
            # Preserva a cor da marca como preenchimento (amarelo continua amarelo, com texto escuro).
            primary, on_primary = fit_solid(brand_ramp[8] if theme == "dark" else seed)
        t["primary"] = primary
        t["on-primary"] = on_primary
        # Traco, indicador ativo e icone sobre a tela usam primary-strong (>= 3:1 contra canvas e card).
        away = -1 if theme == "light" else +1
        t["primary-strong"] = ensure_contrast(*hex_to_oklch(primary), _hardest_bg(canvas, card, theme), 3.0, away, 0.0)
        t["primary-surface"] = brand_ramp[2]
        t["primary-border"] = brand_ramp[6]
        t["primary-text"] = ensure_contrast(*hex_to_oklch(brand_ramp[10]), card, 4.6, -1 if theme == "light" else +1)
        acc, on_acc = fit_solid(accent_ramp[8] if theme == "dark" else accent)
        t["accent"] = acc
        t["on-accent"] = on_acc
        t["focus-ring"] = ensure_contrast(*hex_to_oklch(acc), _hardest_bg(canvas, card, theme), 3.0, away, 0.0)
        t["accent-surface"] = accent_ramp[2]
        t["accent-border"] = accent_ramp[6]
        t["accent-text"] = ensure_contrast(*hex_to_oklch(accent_ramp[10]), card, 4.6, -1 if theme == "light" else +1)

        for role in ("success", "warning", "danger", "info"):
            L, C, H = semantic_seed(role, seed, theme)
            # Solidos semanticos com texto branco nos dois temas (vermelho real, verde real), salvo o ambar.
            solid, on = fit_solid(oklch_to_hex(L if role == "warning" else min(L, 0.56), C, H))
            t[role] = solid
            t[f"on-{role}"] = on
            if theme == "light":
                t[f"{role}-surface"] = oklch_to_hex(0.955, C * 0.28, H)
                t[f"{role}-border"] = oklch_to_hex(0.78, C * 0.75, H)
                t[f"{role}-text"] = ensure_contrast(0.46, C, H, t[f"{role}-surface"], 4.8, -1)
            else:
                t[f"{role}-surface"] = oklch_to_hex(0.26, C * 0.45, H)
                t[f"{role}-border"] = oklch_to_hex(0.48, C * 0.8, H)
                t[f"{role}-text"] = ensure_contrast(0.80, C * 0.9, H, t[f"{role}-surface"], 4.8, +1)

        # zonas da marca (uso decidido pela direcao; tokens existem para quem precisar)
        bc = 0.0 if achromatic else 1.0
        t["surface-brand-dark"] = oklch_to_hex(0.26 if theme == "light" else 0.24, bc * max(0.04, sc * 0.55), sh)
        t["surface-brand-dark-2"] = oklch_to_hex(0.32 if theme == "light" else 0.29, bc * max(0.05, sc * 0.6), sh)
        t["on-brand-dark"] = "#F8FAFC"
        t["on-brand-dark-muted"] = ensure_contrast(0.84, 0.03, sh, t["surface-brand-dark"], 4.6, +1)
        t["surface-brand-header"] = brand_ramp[1] if theme == "light" else oklch_to_hex(0.25, bc * max(0.03, sc * 0.35), sh)
        t["surface-brand-panel"] = brand_ramp[0] if theme == "light" else oklch_to_hex(0.22, bc * max(0.025, sc * 0.3), sh)
        t["surface-tint-soft"] = brand_ramp[1] if theme == "light" else brand_ramp[2]
        t["border-tint"] = brand_ramp[5]
        for i, col in enumerate(chart_palette(chart_seed, theme), 1):
            t[f"chart-{i}"] = col
        semantic[theme] = t
        charts = [t[f"chart-{i}"] for i in range(1, 7)]
        report["checks"][theme] = {
            "chart_min_distance": min_distance(charts),
            "chart_min_distance_deuteranopia": min_distance(charts, "deuteranopia"),
            "chart_min_distance_protanopia": min_distance(charts, "protanopia"),
            "text_muted_on_canvas": round(wcag(t["text-muted"], canvas), 2),
            "border_subtle_on_card": round(wcag(t["border-subtle"], card), 2),
            "canvas_vs_card": round(wcag(canvas, card), 2),
        }

    fonts = fonts or {}
    density = density if density in DENSITY else "regular"
    spacing = dict(zip(("1", "2", "3", "4", "5", "6", "8", "10", "12", "16"), DENSITY[density]["space"]))
    return {
        "$schema": "design-aura/tokens@3",
        "meta": {"brand": brand, "version": "1.0", "defaultTheme": default_theme, "depth_style": style,
                 "seed": seed, "accent": accent, "harmony": harmony, "density": density, "generated_by": "color_engine"},
        "primitive": {},
        "semantic": semantic,
        "typography": {
            "font-display": fonts.get("display", "system-ui, sans-serif"),
            "font-ui": fonts.get("ui", "system-ui, sans-serif"),
            "font-mono": fonts.get("mono", "ui-monospace, monospace"),
            "text-base": DENSITY[density]["text-base"],
            "measure-body": "68ch",
            "tracking-display": "-0.02em",
        },
        "spacing": spacing,
        "sizing": dict(DENSITY[density]["sizing"]),
        "radii": {"control-sm": "6px", "control-md": "8px", "card-sm": "10px", "card-md": "12px", "card-lg": "16px", "pill": "999px"},
        "motion": {"duration-fast": "120ms", "duration-enter": "220ms", "duration-exit": "140ms", "page-desktop": "200ms",
                   "page-ios": "350ms", "page-android": "250ms", "ease-out": "cubic-bezier(0.22, 1, 0.36, 1)", "press-scale": "0.97"},
        "report": report,
    }
