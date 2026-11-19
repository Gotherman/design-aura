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
        reasons.append(f"WCAG {ratio}:1 abaixo do minimo {min_wcag}:1")

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


def audit_file(path: Path) -> list[dict]:
    results = []
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        primitives = data.get("primitive", {})
        semantic = data.get("semantic", {})
        for tname in ("light", "dark"):
            tmap = resolve_token_map(semantic.get(tname, {}), primitives)
            if not tmap:
                continue
            for fg_k, bg_k, kind, label in REQUIRED_LIGHT_DARK_PAIRS:
                if fg_k in tmap and bg_k in tmap:
                    results.append(evaluate_pair(tmap[fg_k], tmap[bg_k], kind, label, theme=tname, token_map=tmap))
    else:
        css_text = path.read_text(encoding="utf-8")
        themes = parse_css_themes(css_text)
        for tname, tmap in themes.items():
            for fg_k, bg_k, kind, label in REQUIRED_LIGHT_DARK_PAIRS:
                # Suporte a prefixo --da- ou nome direto --
                fg_val = tmap.get(fg_k) or tmap.get(f"da-{fg_k}")
                bg_val = tmap.get(bg_k) or tmap.get(f"da-{bg_k}")
                if fg_val and bg_val:
                    results.append(evaluate_pair(fg_val, bg_val, kind, label, theme=tname, token_map=tmap))
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
