#!/usr/bin/env python3
"""Validador de contraste WCAG 2.1 e APCA-W3 (0.0.98G-4g) da skill Design Aura.

Aceita arquivos tokens.css, tokens.json ou pares avulsos --pair "#fg:#bg:label".
Em modo --strict, retorna codigo de saida 1 se houver qualquer violacao BLOCK.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

REQUIRED_LIGHT_DARK_PAIRS = [
    ("text-strong", "surface-z1", "body", "text-strong sobre surface-z1"),
    ("text-strong", "surface-z2", "body", "text-strong sobre surface-z2"),
    ("text-body", "surface-z1", "body", "text-body sobre surface-z1"),
    ("text-body", "surface-z2", "body", "text-body sobre surface-z2"),
    ("text-muted", "surface-z1", "body", "text-muted sobre surface-z1"),
    ("text-muted", "surface-z2", "body", "text-muted sobre surface-z2"),
    ("text-strong", "surface-z0", "body", "text-strong sobre surface-z0"),
    ("on-primary", "primary", "body", "on-primary sobre primary"),
    ("on-accent", "accent", "body", "on-accent sobre accent"),
    ("on-success", "success", "body", "on-success sobre success"),
    ("on-warning", "warning", "body", "on-warning sobre warning"),
    ("on-danger", "danger", "body", "on-danger sobre danger"),
    ("on-info", "info", "body", "on-info sobre info"),
    ("accent", "surface-z2", "ui", "accent sobre surface-z2 (UI/link/icone)"),
    ("primary", "surface-z2", "ui", "primary sobre surface-z2 (UI/titulo)"),
]


def parse_hex(color: str) -> tuple[int, int, int] | None:
    c = color.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c)
    if not m:
        return None
    h = m.group(1)
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def normalize_hex(color: str) -> str:
    rgb = parse_hex(color)
    if not rgb:
        return color.strip().lower()
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _alpha(token: str | None) -> float:
    if token is None or str(token).strip() == "":
        return 1.0
    raw = str(token).strip()
    try:
        if raw.endswith("%"):
            return max(0.0, min(1.0, float(raw[:-1]) / 100.0))
        return max(0.0, min(1.0, float(raw)))
    except ValueError:
        return 1.0


def _channel255(token: str) -> float | None:
    raw = token.strip()
    try:
        if raw.endswith("%"):
            return max(0.0, min(255.0, float(raw[:-1]) / 100.0 * 255.0))
        return float(raw)
    except ValueError:
        return None


def _split_color_args(inner: str) -> tuple[list[str], str | None]:
    body = inner.strip()
    alpha = None
    if "/" in body:
        body, alpha = body.split("/", 1)
        alpha = alpha.strip()
    if "," in body:
        parts = [p.strip() for p in body.split(",") if p.strip()]
    else:
        parts = [p for p in body.split() if p]
    return parts, alpha


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    h = h % 360.0
    s = max(0.0, min(1.0, s))
    l = max(0.0, min(1.0, l))
    c = (1.0 - abs(2.0 * l - 1.0)) * s
    hp = h / 60.0
    x = c * (1.0 - abs(hp % 2.0 - 1.0))
    m = l - c / 2.0
    if hp < 1:
        r, g, b = c, x, 0.0
    elif hp < 2:
        r, g, b = x, c, 0.0
    elif hp < 3:
        r, g, b = 0.0, c, x
    elif hp < 4:
        r, g, b = 0.0, x, c
    elif hp < 5:
        r, g, b = x, 0.0, c
    else:
        r, g, b = c, 0.0, x
    return (
        int(round((r + m) * 255)),
        int(round((g + m) * 255)),
        int(round((b + m) * 255)),
    )


def _oklch_to_rgb(lightness: float, chroma: float, hue: float) -> tuple[int, int, int]:
    if lightness > 1.0:
        lightness = lightness / 100.0
    lightness = max(0.0, min(1.0, lightness))
    rad = math.radians(hue)
    a = chroma * math.cos(rad)
    b = chroma * math.sin(rad)
    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b
    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3
    r_lin = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def encode(channel: float) -> int:
        channel = max(0.0, min(1.0, channel))
        if channel <= 0.0031308:
            curved = 12.92 * channel
        else:
            curved = 1.055 * (channel ** (1.0 / 2.4)) - 0.055
        return int(round(max(0.0, min(1.0, curved)) * 255))

    return encode(r_lin), encode(g_lin), encode(b_lin)


def resolve_vars(value: str, token_map: dict | None = None, seen: set[str] | None = None) -> str:
    """Resolve uma cadeia var(--token), com fallback CSS e protecao contra ciclo."""
    token_map = token_map or {}
    seen = set(seen or ())
    text = str(value).strip()
    match = re.fullmatch(r"var\(\s*--([A-Za-z0-9_-]+)\s*(?:,\s*([^)]*))?\)", text, re.I)
    if not match:
        return text
    name = match.group(1)
    if name in seen:
        fallback = (match.group(2) or "").strip()
        return resolve_vars(fallback, token_map, seen) if fallback else text
    seen.add(name)
    target = token_map.get(name)
    if target is None:
        target = token_map.get(f"--{name}")
    if target is None:
        fallback = (match.group(2) or "").strip()
        return resolve_vars(fallback, token_map, seen) if fallback else text
    return resolve_vars(str(target), token_map, seen)


def parse_color(value: str) -> tuple[int, int, int, float] | None:
    """Converte #hex, rgb/rgba, hsl/hsla ou oklch em RGBA 8-bit + alpha 0..1."""
    raw = str(value).strip().lower()
    if raw == "transparent":
        return (0, 0, 0, 0.0)
    if raw == "black":
        return (0, 0, 0, 1.0)
    if raw == "white":
        return (255, 255, 255, 1.0)

    hex_match = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})", raw)
    if hex_match:
        h = hex_match.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) == 6:
            h += "ff"
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255.0

    fn = re.fullmatch(r"(oklch|hsl|hsla|rgb|rgba)\(\s*([^)]+)\)", raw)
    if not fn:
        return None
    kind, inner = fn.group(1), fn.group(2)
    parts, alpha_tok = _split_color_args(inner)
    alpha = _alpha(alpha_tok)
    if alpha_tok is None and len(parts) >= 4 and kind in ("rgb", "rgba", "hsl", "hsla"):
        alpha = _alpha(parts[3])
        parts = parts[:3]
    if kind in ("rgb", "rgba") and len(parts) >= 3:
        channels = [_channel255(p) for p in parts[:3]]
        if any(c is None for c in channels):
            return None
        return int(round(channels[0])), int(round(channels[1])), int(round(channels[2])), alpha
    if kind in ("hsl", "hsla") and len(parts) >= 3:
        try:
            hue = float(parts[0].strip().removesuffix("deg"))
        except ValueError:
            return None
        s_raw, l_raw = parts[1].strip(), parts[2].strip()
        try:
            sat = float(s_raw[:-1]) / 100.0 if s_raw.endswith("%") else float(s_raw)
            lig = float(l_raw[:-1]) / 100.0 if l_raw.endswith("%") else float(l_raw)
        except ValueError:
            return None
        if not s_raw.endswith("%") and sat > 1:
            sat /= 100.0
        if not l_raw.endswith("%") and lig > 1:
            lig /= 100.0
        r, g, b = _hsl_to_rgb(hue, sat, lig)
        return r, g, b, alpha
    if kind == "oklch" and len(parts) >= 3:
        l_raw = parts[0].strip()
        try:
            lightness = float(l_raw[:-1]) / 100.0 if l_raw.endswith("%") else float(l_raw)
            chroma_raw = parts[1].strip()
            chroma = float(chroma_raw[:-1]) if chroma_raw.endswith("%") else float(chroma_raw)
            if chroma_raw.endswith("%"):
                chroma = chroma / 100.0 * 0.4
            hue = float(parts[2].strip().removesuffix("deg"))
        except ValueError:
            return None
        if not l_raw.endswith("%") and lightness > 1:
            lightness /= 100.0
        r, g, b = _oklch_to_rgb(lightness, chroma, hue)
        return r, g, b, alpha
    return None


def composite(fg: tuple[int, int, int, float], bg: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b, alpha = fg
    if alpha >= 0.999:
        return r, g, b
    br, bgc, bb = bg
    return (
        int(round(r * alpha + br * (1.0 - alpha))),
        int(round(g * alpha + bgc * (1.0 - alpha))),
        int(round(b * alpha + bb * (1.0 - alpha))),
    )


def backdrop_for(theme: str) -> tuple[int, int, int]:
    if theme == "dark":
        return (13, 21, 32)
    return (255, 255, 255)


def color_to_opaque_rgb(
    value: str,
    token_map: dict | None = None,
    backdrop: tuple[int, int, int] = (255, 255, 255),
) -> tuple[int, int, int] | None:
    resolved = resolve_vars(value, token_map)
    parsed = parse_color(resolved)
    if parsed is None:
        return None
    return composite(parsed, backdrop)


def color_to_hex(value: str, token_map: dict | None = None) -> str | None:
    rgb = color_to_opaque_rgb(value, token_map)
    if rgb is None:
        return None
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def srgb_to_linear(channel_255: int) -> float:
    c = channel_255 / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (srgb_to_linear(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def wcag_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def apca_lc(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """Calcula contraste perceptual APCA-W3 (0.0.98G-4g)."""
    def ys(rgb: tuple[int, int, int]) -> float:
        r = (rgb[0] / 255.0) ** 2.4
        g = (rgb[1] / 255.0) ** 2.4
        b = (rgb[2] / 255.0) ** 2.4
        y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        if y < 0.022:
            y += (0.022 - y) ** 1.414
        return y

    y_txt = ys(fg)
    y_bg = ys(bg)
    if abs(y_bg - y_txt) < 0.0005:
        return 0.0

    if y_bg > y_txt:
        sapc = (y_bg ** 0.56 - y_txt ** 0.57) * 1.14
        return 0.0 if sapc < 0.1 else (sapc - 0.027) * 100.0
    else:
        sapc = (y_bg ** 0.65 - y_txt ** 0.62) * 1.14
        return 0.0 if sapc > -0.1 else (sapc + 0.027) * 100.0


def evaluate_pair(
    fg_hex: str,
    bg_hex: str,
    kind: str,
    label: str,
    theme: str = "custom",
    token_map: dict | None = None,
) -> dict:
    token_map = token_map or {}
    bg_rgb = color_to_opaque_rgb(bg_hex, token_map, backdrop_for(theme))
    fg_rgb = color_to_opaque_rgb(fg_hex, token_map, bg_rgb or backdrop_for(theme))
    if fg_rgb is None or bg_rgb is None:
        return {
            "theme": theme,
            "label": label,
            "fg": fg_hex,
            "bg": bg_hex,
            "kind": kind,
            "wcag": 0.0,
            "apca_lc": 0.0,
            "severity": "BLOCK",
            "status": "FAIL",
            "reason": "Cor nao resolvida (hex, rgb, hsl, oklch ou var(--token))",
        }

    ratio = round(wcag_ratio(fg_rgb, bg_rgb), 2)
    lc = round(apca_lc(fg_rgb, bg_rgb), 1)
    abs_lc = abs(lc)

    n_fg = f"#{fg_rgb[0]:02x}{fg_rgb[1]:02x}{fg_rgb[2]:02x}"
    n_bg = f"#{bg_rgb[0]:02x}{bg_rgb[1]:02x}{bg_rgb[2]:02x}"

    min_wcag = 4.5 if kind == "body" else 3.0
    min_apca = 60.0 if kind == "body" else 45.0

    reasons = []
    severity = "PASS"

    if (n_fg == "#000000" and n_bg == "#ffffff") or (n_fg == "#ffffff" and n_bg == "#000000"):
        severity = "BLOCK"
        reasons.append("Uso cru de #000000 sobre #FFFFFF sem elevacao controlada (Bloco 3)")

    if ratio < min_wcag:
        severity = "BLOCK"
        hint = ""
        if "on-accent" in label or "on-warning" in label or "on-success" in label:
            if relative_luminance(fg_rgb) > 0.8 and relative_luminance(bg_rgb) > 0.16:
                hint = " (Dica DA-B3-04: use texto escuro #101822 sobre a cor viva em vez de apagar a marca para marrom/oliva morto)"
        reasons.append(f"WCAG {ratio}:1 abaixo do minimo {min_wcag}:1{hint}")

    if abs_lc < min_apca:
        if severity != "BLOCK":
            severity = "HIGH" if abs_lc < (min_apca - 10) else "MEDIUM"
        reasons.append(f"APCA |Lc|={abs_lc} abaixo do alvo {min_apca}")

    return {
        "theme": theme,
        "label": label,
        "fg": n_fg,
        "bg": n_bg,
        "kind": kind,
        "wcag": ratio,
        "apca_lc": lc,
        "severity": severity,
        "status": "PASS" if severity == "PASS" else "FAIL",
        "reason": "; ".join(reasons) if reasons else "OK",
    }


def resolve_token_map(raw_map: dict, primitives: dict) -> dict[str, str]:
    resolved = {}
    for key, val in raw_map.items():
        if not isinstance(val, str):
            continue
        m = re.fullmatch(r"\{primitive\.([a-zA-Z0-9_-]+)\}", val.strip())
        if m:
            pkey = m.group(1)
            resolved[key] = primitives.get(pkey, val)
        else:
            resolved[key] = val.strip()
    return resolved


def parse_css_themes(css_text: str) -> dict[str, dict[str, str]]:
    themes: dict[str, dict[str, str]] = {"root": {}, "light": {}, "dark": {}}

    # Remove comentarios /* ... */
    clean = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)

    for m in re.finditer(r"([^{}]+)\{([^{}]+)\}", clean):
        selector = m.group(1).strip()
        body = m.group(2)
        vars_found = {}
        for vm in re.finditer(r"--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);", body):
            vars_found[vm.group(1)] = vm.group(2).strip()

        if not vars_found:
            continue

        if ":root" in selector and "data-theme" not in selector:
            themes["root"].update(vars_found)
        if 'data-theme="light"' in selector or "data-theme='light'" in selector:
            themes["light"].update(vars_found)
        if 'data-theme="dark"' in selector or "data-theme='dark'" in selector:
            themes["dark"].update(vars_found)

    result = {}
    for tname in ("light", "dark"):
        merged = dict(themes["root"])
        merged.update(themes[tname])
        if merged:
            result[tname] = merged
    if not result and themes["root"]:
        result["root"] = themes["root"]
    return result


TOKEN_ALIASES = {
    "surface-z0": ["surface-z0", "da-surface-z0", "bg-well", "well"],
    "surface-z1": ["surface-z1", "da-surface-z1", "bg-canvas", "canvas", "bg"],
    "surface-z2": ["surface-z2", "da-surface-z2", "bg-card", "card", "surface"],
    "text-strong": ["text-strong", "da-text-strong", "ink-strong", "fg-strong", "text"],
    "text-body": ["text-body", "da-text-body", "ink", "fg", "text-primary", "text"],
    "text-muted": ["text-muted", "da-text-muted", "ink-muted", "muted"],
}


def _resolve_token_key(tmap: dict[str, str], key: str) -> str | None:
    for cand in TOKEN_ALIASES.get(key, [key, f"da-{key}"]):
        if cand in tmap:
            return tmap[cand]
    return tmap.get(key) or tmap.get(f"da-{key}")


def _rgb_to_hls_deg(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    import colorsys
    h, l, s = colorsys.rgb_to_hls(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
    return h * 360.0, l, s


def _hue_dist(h1: float, h2: float) -> float:
    d = abs(h1 - h2) % 360.0
    return min(d, 360.0 - d)


OPTIONAL_SEMANTIC_SURFACE_PAIRS = [
    ("primary-text", "primary-surface", "ui", "primary-text sobre primary-surface (badge/aba)"),
    ("success-text", "success-surface", "ui", "success-text sobre success-surface (badge sucesso)"),
    ("warning-text", "warning-surface", "ui", "warning-text sobre warning-surface (badge alerta)"),
    ("danger-text", "danger-surface", "ui", "danger-text sobre danger-surface (badge erro)"),
    ("info-text", "info-surface", "ui", "info-text sobre info-surface (badge info)"),
]


def _evaluate_theme_pairs(tname: str, tmap: dict[str, str]) -> list[dict]:
    out: list[dict] = []
    for fg_k, bg_k, kind, label in REQUIRED_LIGHT_DARK_PAIRS:
        actual_fg_k = fg_k
        actual_label = label
        if fg_k in ("primary", "accent") and bg_k == "surface-z2":
            text_cand = _resolve_token_key(tmap, f"{fg_k}-text")
            if text_cand:
                actual_fg_k = f"{fg_k}-text"
                actual_label = f"{fg_k}-text sobre surface-z2 (UI/link/icone)"
        fg_val = _resolve_token_key(tmap, actual_fg_k)
        bg_val = _resolve_token_key(tmap, bg_k)
        if fg_val and bg_val:
            out.append(evaluate_pair(fg_val, bg_val, kind, actual_label, theme=tname, token_map=tmap))

    for fg_k, bg_k, kind, label in OPTIONAL_SEMANTIC_SURFACE_PAIRS:
        fg_val = _resolve_token_key(tmap, fg_k)
        bg_val = _resolve_token_key(tmap, bg_k)
        if fg_val and bg_val:
            out.append(evaluate_pair(fg_val, bg_val, kind, label, theme=tname, token_map=tmap))
    return out


def audit_semantic_hue_parity(themes_map: dict[str, dict[str, str]]) -> list[dict]:
    """Garante paridade de matiz semantico entre Light e Dark (v2.4.0): erro e vermelho nos dois modos, nunca rosa pastel."""
    findings: list[dict] = []
    light_map = themes_map.get("light") or {}
    dark_map = themes_map.get("dark") or {}

    # 1. Bloqueia vermelho-erro virando rosa pastel no Dark Mode (ex.: #FDA4AF / #F472B6)
    for key in ("danger", "danger-text"):
        d_val = _resolve_token_key(dark_map, key) if dark_map else None
        if not d_val:
            continue
        d_rgb = color_to_opaque_rgb(d_val, dark_map, backdrop_for("dark"))
        if not d_rgb:
            continue
        hd, ld, sd = _rgb_to_hls_deg(d_rgb)
        if sd >= 0.30 and ld > 0.72 and (318.0 <= hd <= 357.0):
            d_hex = f"#{d_rgb[0]:02x}{d_rgb[1]:02x}{d_rgb[2]:02x}"
            findings.append({
                "theme": "dark",
                "label": f"DA-SEMANTIC-HUE-PARITY ({key} rosa pastel no Dark)",
                "fg": d_hex,
                "bg": "#17202e",
                "kind": "ui",
                "wcag": round(wcag_ratio(d_rgb, (23, 32, 46)), 2),
                "apca_lc": round(apca_lc(d_rgb, (23, 32, 46)), 1),
                "severity": "BLOCK",
                "status": "FAIL",
                "reason": (
                    f"DA-SEMANTIC-HUE-PARITY: '{key}' no Dark Mode ({d_hex}, H={int(round(hd))}°, L={int(round(ld*100))}%) "
                    "virou rosa pastel em vez de vermelho real. Use vermelho verdadeiro em solidos (ex.: #DC2626 c/ #FFFFFF) "
                    "e vermelho vivo em texto/icone (--danger-text: #FF6E6E, H=0°)."
                ),
            })

    # 2. Alerta se 'success' fugir do verde esmeralda para ciano/turquesa neon (hue > 168°)
    for tname, tmap in (("light", light_map), ("dark", dark_map)):
        s_val = _resolve_token_key(tmap, "success") if tmap else None
        if not s_val:
            continue
        s_rgb = color_to_opaque_rgb(s_val, tmap, backdrop_for(tname))
        if not s_rgb:
            continue
        hs, ls, ss = _rgb_to_hls_deg(s_rgb)
        if ss >= 0.25 and (hs > 168.0 or hs < 105.0):
            s_hex = f"#{s_rgb[0]:02x}{s_rgb[1]:02x}{s_rgb[2]:02x}"
            findings.append({
                "theme": tname,
                "label": f"DA-SEMANTIC-HUE-PARITY (success fora do verde esmeralda)",
                "fg": s_hex,
                "bg": "#17202e" if tname == "dark" else "#ffffff",
                "kind": "ui",
                "wcag": 0.0,
                "apca_lc": 0.0,
                "severity": "HIGH",
                "status": "FAIL",
                "reason": (
                    f"DA-SEMANTIC-HUE-PARITY: 'success' em {tname} ({s_hex}, H={int(round(hs))}°) "
                    "escapou da familia verde esmeralda (120°-165°). Mantenha verde real (ex.: #15803D solid / #4ADE80 text)."
                ),
            })

    # 3. Divergencia de matiz > 38° entre Light e Dark para o mesmo papel semantico
    if light_map and dark_map:
        for role in ("danger", "success", "warning", "primary"):
            lv = _resolve_token_key(light_map, role)
            dv = _resolve_token_key(dark_map, role)
            if not (lv and dv):
                continue
            l_rgb = color_to_opaque_rgb(lv, light_map, backdrop_for("light"))
            d_rgb = color_to_opaque_rgb(dv, dark_map, backdrop_for("dark"))
            if not (l_rgb and d_rgb):
                continue
            hl, _, sl = _rgb_to_hls_deg(l_rgb)
            hd, _, sd = _rgb_to_hls_deg(d_rgb)
            dist = _hue_dist(hl, hd)
            if sl >= 0.25 and sd >= 0.25 and dist > 38.0:
                l_hex = f"#{l_rgb[0]:02x}{l_rgb[1]:02x}{l_rgb[2]:02x}"
                d_hex = f"#{d_rgb[0]:02x}{d_rgb[1]:02x}{d_rgb[2]:02x}"
                findings.append({
                    "theme": "parity",
                    "label": f"DA-SEMANTIC-HUE-PARITY ({role} Light vs Dark)",
                    "fg": d_hex,
                    "bg": l_hex,
                    "kind": "ui",
                    "wcag": round(wcag_ratio(d_rgb, l_rgb), 2),
                    "apca_lc": 0.0,
                    "severity": "HIGH",
                    "status": "FAIL",
                    "reason": (
                        f"DA-SEMANTIC-HUE-PARITY: '{role}' divergiu {int(round(dist))}° entre Light ({l_hex}, H={int(round(hl))}°) "
                        f"e Dark ({d_hex}, H={int(round(hd))}°). Mantenha a mesma familia de cor nos dois temas."
                    ),
                })

    return findings


def audit_theme_harmony(theme: str, tmap: dict[str, str]) -> list[dict]:
    """Verifica equilibrio cromatico 65/20/10/5, profundidade real no Dark (anti-monobloco) e nitidez no Light."""
    findings: list[dict] = []
    z1_val = _resolve_token_key(tmap, "surface-z1")
    z2_val = _resolve_token_key(tmap, "surface-z2")
    b_sub_val = _resolve_token_key(tmap, "border-subtle")
    prim_val = _resolve_token_key(tmap, "primary")
    if not (z1_val and z2_val and b_sub_val and prim_val):
        return findings

    z1_rgb = color_to_opaque_rgb(z1_val, tmap, backdrop_for(theme))
    z2_rgb = color_to_opaque_rgb(z2_val, tmap, backdrop_for(theme))
    b_rgb = color_to_opaque_rgb(b_sub_val, tmap, z2_rgb or backdrop_for(theme))
    p_rgb = color_to_opaque_rgb(prim_val, tmap, z1_rgb or backdrop_for(theme))
    if not (z1_rgb and z2_rgb and b_rgb and p_rgb):
        return findings

    if theme == "dark":
        h1, l1, s1 = _rgb_to_hls_deg(z1_rgb)
        h2, l2, s2 = _rgb_to_hls_deg(z2_rgb)
        hp, _, sp = _rgb_to_hls_deg(p_rgb)
        if s1 > 0.36 and s2 > 0.36 and sp > 0.35 and _hue_dist(h1, hp) <= 28 and _hue_dist(h2, hp) <= 28:
            findings.append({
                "theme": "dark",
                "label": "DA-DARK-MONOCHROME (surface-z1/z2 vs primary)",
                "fg": f"#{z2_rgb[0]:02x}{z2_rgb[1]:02x}{z2_rgb[2]:02x}",
                "bg": f"#{z1_rgb[0]:02x}{z1_rgb[1]:02x}{z1_rgb[2]:02x}",
                "kind": "ui",
                "wcag": round(wcag_ratio(z2_rgb, z1_rgb), 2),
                "apca_lc": round(apca_lc(z2_rgb, z1_rgb), 1),
                "severity": "MEDIUM",
                "status": "FAIL",
                "reason": (
                    f"DA-DARK-MONOCHROME: Superficies Dark saturadas demais (S={int(round(s1*100))}%/{int(round(s2*100))}%) "
                    "no mesmo matiz da cor primaria (massa monocromatica pesada). Calibre Z0-Z3 para ardosia com subtom (S=24-35%) "
                    "e puxe os tons fortes de azul/marca em --surface-brand-header, .card-brand-hero e controles .is-active."
                ),
            })

        z2_vs_z1 = round(wcag_ratio(z2_rgb, z1_rgb), 2)
        border_vs_z2 = round(wcag_ratio(b_rgb, z2_rgb), 2)
        if z2_vs_z1 < 1.08 or border_vs_z2 < 1.25:
            findings.append({
                "theme": "dark",
                "label": "DA-DARK-FLAT-MONOLITH (Z1->Z2 / border-subtle sem profundidade)",
                "fg": f"#{b_rgb[0]:02x}{b_rgb[1]:02x}{b_rgb[2]:02x}",
                "bg": f"#{z2_rgb[0]:02x}{z2_rgb[1]:02x}{z2_rgb[2]:02x}",
                "kind": "ui",
                "wcag": min(z2_vs_z1, border_vs_z2),
                "apca_lc": round(apca_lc(b_rgb, z2_rgb), 1),
                "severity": "HIGH",
                "status": "FAIL",
                "reason": (
                    f"DA-DARK-FLAT-MONOLITH: Monobloco escuro sem divisao clara (Z2/Z1={z2_vs_z1}:1 < 1.08:1 ou "
                    f"border-subtle/Z2={border_vs_z2}:1 < 1.25:1). Separe os planos Z0->Z4 com degrau nitido, borda >= 1.35:1 "
                    "e cabecalhos/destaques no tom da marca (--surface-brand-header / --rim-highlight)."
                ),
            })

    if theme == "light":
        border_vs_z2 = round(wcag_ratio(b_rgb, z2_rgb), 2)
        z1_vs_z2 = round(wcag_ratio(z1_rgb, z2_rgb), 2)
        if border_vs_z2 < 1.85:
            findings.append({
                "theme": "light",
                "label": "DA-LIGHT-WASHED-OUT (border-subtle sobre surface-z2)",
                "fg": f"#{b_rgb[0]:02x}{b_rgb[1]:02x}{b_rgb[2]:02x}",
                "bg": f"#{z2_rgb[0]:02x}{z2_rgb[1]:02x}{z2_rgb[2]:02x}",
                "kind": "ui",
                "wcag": border_vs_z2,
                "apca_lc": round(apca_lc(b_rgb, z2_rgb), 1),
                "severity": "HIGH",
                "status": "FAIL",
                "reason": (
                    f"DA-LIGHT-WASHED-OUT: Borda sutil clara demais no Light Mode ({border_vs_z2}:1 < 1.85:1 contra Z2), "
                    "apagando contornos de cards e divisoes. Use border-subtle nitida (ideal 2.0-2.4:1, ex.: #93ABC7) "
                    "com Z1 aterrado (#D9E5F3) e variacoes azul-claro/marinho da marca."
                ),
            })
        elif relative_luminance(z2_rgb) > 0.94 and z1_vs_z2 < 1.18:
            findings.append({
                "theme": "light",
                "label": "DA-LIGHT-WASHED-OUT (surface-z1 colada em surface-z2)",
                "fg": f"#{z1_rgb[0]:02x}{z1_rgb[1]:02x}{z1_rgb[2]:02x}",
                "bg": f"#{z2_rgb[0]:02x}{z2_rgb[1]:02x}{z2_rgb[2]:02x}",
                "kind": "ui",
                "wcag": z1_vs_z2,
                "apca_lc": round(apca_lc(z1_rgb, z2_rgb), 1),
                "severity": "HIGH",
                "status": "FAIL",
                "reason": (
                    f"DA-LIGHT-WASHED-OUT: Canvas Z1 claro demais frente aos cards brancos Z2 ({z1_vs_z2}:1 < 1.18:1), "
                    "deixando a tela 'tudo branco'. Aterre surface-z1 (ex.: #D9E5F3) e surface-z0 (#C6D6EA) para profundidade real."
                ),
            })
    return findings


def audit_file(path: Path) -> list[dict]:
    results = []
    themes_map: dict[str, dict[str, str]] = {}
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        primitives = data.get("primitive", {})
        semantic = data.get("semantic", {})
        for tname in ("light", "dark"):
            tmap = resolve_token_map(semantic.get(tname, {}), primitives)
            if not tmap:
                continue
            themes_map[tname] = tmap
            results.extend(_evaluate_theme_pairs(tname, tmap))
            results.extend(audit_theme_harmony(tname, tmap))
    else:
        css_text = path.read_text(encoding="utf-8")
        themes = parse_css_themes(css_text)
        for tname, tmap in themes.items():
            themes_map[tname] = tmap
            results.extend(_evaluate_theme_pairs(tname, tmap))
            results.extend(audit_theme_harmony(tname, tmap))
    results.extend(audit_semantic_hue_parity(themes_map))
    return results


def format_markdown(results: list[dict]) -> str:
    blocks = sum(1 for r in results if r["severity"] == "BLOCK")
    highs = sum(1 for r in results if r["severity"] == "HIGH")
    meds = sum(1 for r in results if r["severity"] == "MEDIUM")
    lines = [
        "# Auditoria de Contraste Design Aura (WCAG 2.1 + APCA-W3)",
        f"- **Pares avaliados:** {len(results)} · **BLOCK:** {blocks} · **HIGH:** {highs} · **MEDIUM:** {meds}",
        "",
        "| Tema | Par | Foreground | Background | WCAG | APCA Lc | Status | Detalhe |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for r in results:
        lines.append(
            f"| `{r['theme']}` | {r['label']} | `{r['fg']}` | `{r['bg']}` | {r['wcag']}:1 | {r['apca_lc']} | **{r['severity']}** | {r['reason']} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validador WCAG 2.1 + APCA-W3 da Design Aura.")
    parser.add_argument("target", nargs="?", help="Caminho para tokens.css ou tokens.json")
    parser.add_argument(
        "--pair",
        action="append",
        default=[],
        help="Par avulso no formato '#fg:#bg:label[:body|ui]'",
    )
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"], help="Formato da saida")
    parser.add_argument("--strict", action="store_true", help="Retorna exit 1 se houver BLOCK")
    args = parser.parse_args()

    if not args.target and not args.pair:
        parser.error("Informe um arquivo tokens.css/tokens.json ou pelo menos um --pair")

    results: list[dict] = []
    if args.target:
        p = Path(args.target)
        if not p.exists():
            print(f"Arquivo nao encontrado: {p}", file=sys.stderr)
            sys.exit(1)
        results.extend(audit_file(p))

    for raw_pair in args.pair:
        parts = raw_pair.split(":")
        if len(parts) < 2:
            print(f"Formato invalido em --pair: {raw_pair}", file=sys.stderr)
            sys.exit(1)
        fg = parts[0]
        bg = parts[1]
        label = parts[2] if len(parts) >= 3 else f"{fg} sobre {bg}"
        kind = parts[3] if len(parts) >= 4 and parts[3] in ("body", "ui") else "body"
        results.append(evaluate_pair(fg, bg, kind, label, theme="pair"))

    if not results:
        print("Nenhum par semantico encontrado para auditar.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(results))

    if args.strict and any(r["severity"] == "BLOCK" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
