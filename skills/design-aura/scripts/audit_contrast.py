#!/usr/bin/env python3
"""Validador de contraste WCAG 2.1 e APCA-W3 (0.0.98G-4g) da skill Design Aura.

Aceita arquivos tokens.css, tokens.json ou pares avulsos --pair "#fg:#bg:label".
Em modo --strict, retorna codigo de saida 1 se houver qualquer violacao BLOCK.
"""
import argparse
import json
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


def evaluate_pair(fg_hex: str, bg_hex: str, kind: str, label: str, theme: str = "custom") -> dict:
    fg_rgb = parse_hex(fg_hex)
    bg_rgb = parse_hex(bg_hex)
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
            "reason": "Cor fora do formato hexadecimal (#RGB ou #RRGGBB)",
        }

    ratio = round(wcag_ratio(fg_rgb, bg_rgb), 2)
    lc = round(apca_lc(fg_rgb, bg_rgb), 1)
    abs_lc = abs(lc)

    n_fg = normalize_hex(fg_hex)
    n_bg = normalize_hex(bg_hex)

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
                    results.append(evaluate_pair(tmap[fg_k], tmap[bg_k], kind, label, theme=tname))
    else:
        css_text = path.read_text(encoding="utf-8")
        themes = parse_css_themes(css_text)
        for tname, tmap in themes.items():
            for fg_k, bg_k, kind, label in REQUIRED_LIGHT_DARK_PAIRS:
                # Suporte a prefixo --da- ou nome direto --
                fg_val = tmap.get(fg_k) or tmap.get(f"da-{fg_k}")
                bg_val = tmap.get(bg_k) or tmap.get(f"da-{bg_k}")
                if fg_val and bg_val:
                    results.append(evaluate_pair(fg_val, bg_val, kind, label, theme=tname))
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
