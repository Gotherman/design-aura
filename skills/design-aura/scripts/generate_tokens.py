#!/usr/bin/env python3
"""Compilador de Design Tokens da Design Aura.

Dois caminhos:
1. A partir da cor da marca (motor OKLCH):
   python3 generate_tokens.py --seed "#0F3B57" --accent "#F08A4B" --depth-style hairline --emit-json tokens.json --out tokens.css
2. A partir de um tokens.json ja escrito:
   python3 generate_tokens.py tokens.json --out tokens.css --format all --check-contrast

Saidas: CSS (Light/Dark, planos Z0-Z4, elevacao pelo estilo de profundidade), Tailwind v4,
TypeScript, Swift, Kotlin, Dart e DTCG 2025.10 (tokens.dtcg.json).
"""
import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_contrast import audit_file, color_to_hex  # noqa: E402

REQUIRED_SEMANTIC_KEYS = {
    "surface-z0",
    "surface-z1",
    "surface-z2",
    "surface-z3",
    "surface-z4",
    "text-strong",
    "text-body",
    "text-muted",
    "border-subtle",
    "border-strong",
    "primary",
    "on-primary",
    "accent",
    "on-accent",
    "success",
    "on-success",
    "warning",
    "on-warning",
    "danger",
    "on-danger",
    "info",
    "on-info",
}

ALLOWED_SPACING_PX = {0, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 32, 40, 48, 64, 80, 96}
SHAPE_RADII = {
    "sharp": {"control-sm": "2px", "control-md": "4px", "card-sm": "4px", "card-md": "6px", "card-lg": "8px", "pill": "999px"},
    "soft": {"control-sm": "6px", "control-md": "8px", "card-sm": "10px", "card-md": "12px", "card-lg": "16px", "pill": "999px"},
    "round": {"control-sm": "10px", "control-md": "12px", "card-sm": "16px", "card-md": "20px", "card-lg": "24px", "pill": "999px"},
}


def resolve_ref(val: str, primitives: dict) -> str:
    if not isinstance(val, str):
        return str(val)
    m = re.fullmatch(r"\{primitive\.([a-zA-Z0-9_-]+)\}", val.strip())
    if m:
        pkey = m.group(1)
        if pkey not in primitives:
            raise ValueError(f"Referencia primitiva nao encontrada: {val}")
        return primitives[pkey]
    return val.strip()


def validate_tokens(data: dict) -> list[str]:
    errors = []
    semantic = data.get("semantic", {})
    for theme in ("light", "dark"):
        tmap = semantic.get(theme, {})
        missing = sorted(REQUIRED_SEMANTIC_KEYS - set(tmap.keys()))
        if missing:
            errors.append(f"Tema '{theme}' sem tokens obrigatorios: {', '.join(missing)}")

    spacing = data.get("spacing", {})
    for k, v in spacing.items():
        m = re.fullmatch(r"(\d+)px", str(v).strip())
        if m:
            px = int(m.group(1))
            if px not in ALLOWED_SPACING_PX and px % 8 != 0:
                errors.append(f"Espacamento '{k}: {v}' viola escala 4/8px (Bloco 7)")
    return errors


def emit_css_vars(mapping: dict[str, str], prefix: str = "") -> str:
    lines = []
    for k, v in mapping.items():
        lines.append(f"  --{prefix}{k}: {v};")
    return "\n".join(lines)


def _mix_hex(hex_a: str, hex_b: str, ratio_a: float) -> str:
    """Mistura duas cores hex (ratio_a de hex_a + (1 - ratio_a) de hex_b)."""
    ha = color_to_hex(hex_a) or "#17202e"
    hb = color_to_hex(hex_b) or "#ffffff"
    ra, ga, ba = int(ha[1:3], 16), int(ha[3:5], 16), int(ha[5:7], 16)
    rb, gb, bb = int(hb[1:3], 16), int(hb[3:5], 16), int(hb[5:7], 16)
    r = int(round(ra * ratio_a + rb * (1.0 - ratio_a)))
    g = int(round(ga * ratio_a + gb * (1.0 - ratio_a)))
    b = int(round(ba * ratio_a + bb * (1.0 - ratio_a)))
    return f"#{r:02x}{g:02x}{b:02x}"


def _enrich_semantic_theme(tmap: dict[str, str], theme: str) -> dict[str, str]:
    """Completa tokens de superficie/borda/texto semanticos e cabecalhos da marca sem sobrescrever definidos."""
    enriched = dict(tmap)
    z2 = enriched.get("surface-z2", "#ffffff" if theme == "light" else "#17202e")
    brand_dark = enriched.get("surface-brand-dark", "#0c254a")
    primary = enriched.get("primary", "#14427a" if theme == "light" else "#2563eb")

    if theme == "light":
        enriched.setdefault("surface-brand-header", _mix_hex(primary, "#ffffff", 0.12))
        enriched.setdefault("surface-brand-panel", _mix_hex(primary, "#ffffff", 0.07))
        defaults = {
            "primary": ("#e3eefc", "#8eb4e6", primary),
            "accent": ("#ffedd5", "#ea580c", enriched.get("accent", "#c2410c")),
            "success": ("#dcfce7", "#16a34a", enriched.get("success", "#15803d")),
            "warning": ("#fef3c7", "#d97706", "#9a4a06"),
            "danger": ("#fee2e2", "#dc2626", enriched.get("danger", "#b91c1c")),
            "info": ("#dbeafe", "#2563eb", enriched.get("info", "#1d4ed8")),
        }
    else:
        enriched.setdefault("surface-brand-header", _mix_hex(brand_dark, primary, 0.78))
        enriched.setdefault("surface-brand-panel", _mix_hex(brand_dark, z2, 0.65))
        defaults = {
            "primary": (_mix_hex(primary, z2, 0.22), _mix_hex(primary, "#ffffff", 0.76), "#7cbcff"),
            "accent": (_mix_hex(enriched.get("accent", "#c8460e"), z2, 0.24), "#ea580c", "#ff9a66"),
            "success": ("#0d2b1d", "#22c55e", "#4ade80"),
            "warning": ("#2e1f0a", "#f59e0b", "#fbbf24"),
            "danger": ("#2c1216", "#ef4444", "#ff6e6e"),
            "info": ("#102546", "#3b82f6", "#74b8ff"),
        }

    for role, (surf, bord, txt) in defaults.items():
        enriched.setdefault(f"{role}-surface", surf)
        enriched.setdefault(f"{role}-border", bord)
        enriched.setdefault(f"{role}-text", txt)
    return enriched


def elevation_lines(style: str, theme: str) -> list[str]:
    """Sombras e brilho de borda por estilo de profundidade, tingidos pelos tokens do proprio projeto."""
    ink = "var(--text-strong)"
    if theme == "light":
        table = {
            "tactile": ("inset 0 1px 0 rgba(255, 255, 255, 0.85)",
                        f"0 0 0 1px color-mix(in srgb, {ink} 9%, transparent), 0 1px 2px -1px color-mix(in srgb, {ink} 8%, transparent), 0 3px 8px -1px color-mix(in srgb, {ink} 6%, transparent)",
                        f"0 0 0 1px color-mix(in srgb, {ink} 11%, transparent), 0 3px 6px -2px color-mix(in srgb, {ink} 9%, transparent), 0 10px 22px -6px color-mix(in srgb, {ink} 8%, transparent)",
                        f"0 0 0 1px color-mix(in srgb, {ink} 14%, transparent), 0 8px 20px -4px color-mix(in srgb, {ink} 13%, transparent), 0 18px 34px -8px color-mix(in srgb, {ink} 10%, transparent)"),
            "hairline": ("inset 0 1px 0 rgba(255, 255, 255, 0.6)",
                         f"0 1px 2px color-mix(in srgb, {ink} 5%, transparent)",
                         f"0 1px 3px color-mix(in srgb, {ink} 7%, transparent)",
                         f"0 8px 24px -6px color-mix(in srgb, {ink} 16%, transparent), 0 0 0 1px color-mix(in srgb, {ink} 8%, transparent)"),
            "soft": ("inset 0 1px 0 rgba(255, 255, 255, 0.7)",
                     f"0 1px 2px color-mix(in srgb, {ink} 5%, transparent), 0 2px 8px color-mix(in srgb, {ink} 5%, transparent)",
                     f"0 2px 4px color-mix(in srgb, {ink} 5%, transparent), 0 12px 28px -8px color-mix(in srgb, {ink} 12%, transparent)",
                     f"0 16px 40px -12px color-mix(in srgb, {ink} 20%, transparent)"),
            "tonal": ("none", "none", "none", f"0 6px 18px -6px color-mix(in srgb, {ink} 14%, transparent)"),
        }
    else:
        rim = "color-mix(in srgb, var(--primary) 14%, transparent)"
        table = {
            "tactile": (f"inset 0 1px 0 {rim}", f"inset 0 1px 0 {rim}, 0 2px 10px -2px rgba(0, 0, 0, 0.36)",
                        f"inset 0 1px 0 {rim}, 0 8px 22px -6px rgba(0, 0, 0, 0.44)", f"inset 0 1px 0 {rim}, 0 16px 36px -8px rgba(0, 0, 0, 0.54)"),
            "hairline": ("inset 0 1px 0 rgba(255, 255, 255, 0.05)", "none", "0 1px 2px rgba(0, 0, 0, 0.3)", "0 12px 32px -8px rgba(0, 0, 0, 0.6)"),
            "soft": ("inset 0 1px 0 rgba(255, 255, 255, 0.06)", "0 2px 8px rgba(0, 0, 0, 0.3)", "0 10px 26px -8px rgba(0, 0, 0, 0.5)", "0 18px 44px -12px rgba(0, 0, 0, 0.62)"),
            "tonal": ("none", "none", "none", "0 10px 28px -10px rgba(0, 0, 0, 0.55)"),
        }
    rim_hl, z1, z2, z3 = table.get(style, table["tactile"])
    return [f"  --rim-highlight: {rim_hl};", f"  --shadow-z1: {z1};", f"  --shadow-z2: {z2};", f"  --shadow-z3: {z3};"]


LIGHT_ELEVATION_LINES = [
    "  --rim-highlight: inset 0 1px 0 rgba(255, 255, 255, 0.85);",
    "  --shadow-z1: 0 0 0 1px rgba(14, 41, 75, 0.09), 0 1px 2px -1px rgba(14, 41, 75, 0.08), 0 3px 8px -1px rgba(14, 41, 75, 0.06);",
    "  --shadow-z2: 0 0 0 1px rgba(14, 41, 75, 0.11), 0 3px 6px -2px rgba(14, 41, 75, 0.09), 0 10px 22px -6px rgba(14, 41, 75, 0.08);",
    "  --shadow-z3: 0 0 0 1px rgba(14, 41, 75, 0.14), 0 8px 20px -4px rgba(14, 41, 75, 0.13), 0 18px 34px -8px rgba(14, 41, 75, 0.10);",
]

DARK_ELEVATION_LINES = [
    "  --rim-highlight: inset 0 1px 0 rgba(148, 197, 255, 0.12);",
    "  --shadow-z1: inset 0 1px 0 rgba(148, 197, 255, 0.09), 0 2px 10px -2px rgba(2, 6, 18, 0.36);",
    "  --shadow-z2: inset 0 1px 0 rgba(148, 197, 255, 0.12), 0 8px 22px -6px rgba(2, 6, 18, 0.44);",
    "  --shadow-z3: inset 0 1px 0 rgba(148, 197, 255, 0.15), 0 16px 36px -8px rgba(2, 6, 18, 0.54);",
]


def build_css(data: dict) -> str:
    meta = data.get("meta", {})
    brand = meta.get("brand", "Design Aura Project")
    version = meta.get("version", "2.4.0")
    default_theme = meta.get("defaultTheme", "dark")

    primitives = data.get("primitive", {})
    semantic = data.get("semantic", {})
    typo = data.get("typography", {})
    spacing = data.get("spacing", {})
    sizing = data.get("sizing", {})
    radii = data.get("radii", {})
    motion = data.get("motion", {})

    light_resolved = _enrich_semantic_theme(
        {k: resolve_ref(v, primitives) for k, v in semantic.get("light", {}).items()},
        "light",
    )
    dark_resolved = _enrich_semantic_theme(
        {k: resolve_ref(v, primitives) for k, v in semantic.get("dark", {}).items()},
        "dark",
    )

    depth_style = str(meta.get("depth_style") or "tactile")
    base_theme_vars = dark_resolved if default_theme == "dark" else light_resolved
    base_elevation = elevation_lines(depth_style, "dark" if default_theme == "dark" else "light")

    spacing_vars = {f"space-{k}": v for k, v in spacing.items()}
    radii_vars = {f"radius-{k}": v for k, v in radii.items()}
    motion_vars = {f"motion-{k}": v for k, v in motion.items()}

    css = [
        f"/* {brand} · Design Tokens v{version} (Design Aura) */",
        ":root {",
        emit_css_vars(base_theme_vars),
        emit_css_vars(typo),
        emit_css_vars(spacing_vars),
        emit_css_vars(sizing),
        emit_css_vars(radii_vars),
        emit_css_vars(motion_vars),
        f"  --da-depth-style: {depth_style};",
        *base_elevation,
        "}",
        "",
        'html[data-theme="light"], [data-theme="light"] {',
        "  color-scheme: light;",
        emit_css_vars(light_resolved),
        *elevation_lines(depth_style, "light"),
        "}",
        "",
        'html[data-theme="dark"], [data-theme="dark"] {',
        "  color-scheme: dark;",
        emit_css_vars(dark_resolved),
        *elevation_lines(depth_style, "dark"),
        "}",
        "",
        "/* Superficies base e micro-craft obrigatorio (Blocos 3, 4, 6, 9) */",
        "html {",
        "  -webkit-font-smoothing: antialiased;",
        "  -moz-osx-font-smoothing: grayscale;",
        "  font-family: var(--font-ui);",
        "  background: var(--surface-z1);",
        "  color: var(--text-body);",
        "}",
        "",
        "::selection {",
        "  background: var(--accent);",
        "  color: var(--on-accent);",
        "}",
        "",
        "input, textarea, select {",
        "  caret-color: var(--accent);",
        "}",
        "",
        ":focus-visible {",
        "  outline: 2px solid var(--focus-ring, var(--accent));",
        "  outline-offset: 2px;",
        "}",
        "",
        "/* Cores forcadas (Windows alto contraste): o sistema troca as cores e remove sombras; borda e foco continuam visiveis. */",
        "@media (forced-colors: active) {",
        "  :focus-visible { outline: 2px solid CanvasText; }",
        "  button, [role=\"button\"], input, select, textarea { border: 1px solid ButtonText; }",
        "}",
        "",
        "a {",
        "  text-underline-offset: 3px;",
        "  text-decoration-thickness: 1.5px;",
        "}",
        "",
        "* {",
        "  scrollbar-width: thin;",
        "  scrollbar-color: var(--border-strong) var(--surface-z0);",
        "}",
        "",
        "h1, h2, h3, .text-balance {",
        "  font-family: var(--font-display);",
        "  letter-spacing: var(--tracking-display, -0.025em);",
        "  text-wrap: balance;",
        "}",
        "",
        "p, li, figcaption, .text-pretty {",
        "  text-wrap: pretty;",
        "}",
        "",
        ".tabular-nums, td[data-numeric='true'], th[data-numeric='true'], .num {",
        "  font-variant-numeric: tabular-nums;",
        "}",
        "",
        "@media (prefers-reduced-motion: reduce) {",
        "  *, *::before, *::after {",
        "    animation-duration: 0.01ms !important;",
        "    animation-iteration-count: 1 !important;",
        "    transition-duration: 0.01ms !important;",
        "    scroll-behavior: auto !important;",
        "  }",
        "}",
        "",
    ]
    return "\n".join(css)


def _camel(key: str) -> str:
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", key) if p]
    if not parts:
        return "token"
    head = parts[0][0].lower() + parts[0][1:]
    return head + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def _pascal(key: str) -> str:
    camel = _camel(key)
    return camel[:1].upper() + camel[1:]


def _resolved_themes(data: dict) -> tuple[dict, dict[str, dict[str, str]]]:
    primitives = data.get("primitive", {})
    semantic = data.get("semantic", {})
    themes = {}
    for theme in ("light", "dark"):
        raw = _enrich_semantic_theme(
            {k: resolve_ref(v, primitives) for k, v in semantic.get(theme, {}).items()},
            theme,
        )
        themes[theme] = {k: color_to_hex(v, raw) or v for k, v in raw.items()}
    return primitives, themes


def _is_color(value: str) -> bool:
    return bool(re.match(r"^#[0-9a-fA-F]{3,8}$", str(value).strip()))


def build_tailwind(data: dict) -> str:
    _, themes = _resolved_themes(data)
    typo = data.get("typography", {})
    spacing = data.get("spacing", {})
    radii = data.get("radii", {})
    lines = [
        "/* Design Aura · Tailwind v4 @theme. Re-tema o projeto; nao misture paletas de registries. */",
        "@theme {",
    ]
    for key, value in themes["light"].items():
        lines.append(f"  --color-{key}: {value};")
    for key, value in typo.items():
        lines.append(f"  --font-{key}: {value};" if key.startswith("font-") else f"  --{key}: {value};")
    for key, value in spacing.items():
        lines.append(f"  --spacing-{key}: {value};")
    for key, value in radii.items():
        lines.append(f"  --radius-{key}: {value};")
    lines.extend(["}", "", '[data-theme="dark"], .dark {'])
    for key, value in themes["dark"].items():
        lines.append(f"  --color-{key}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_ts(data: dict) -> str:
    _, themes = _resolved_themes(data)
    payload = {
        "meta": data.get("meta", {}),
        "light": themes["light"],
        "dark": themes["dark"],
        "typography": data.get("typography", {}),
        "spacing": data.get("spacing", {}),
        "radii": data.get("radii", {}),
        "motion": data.get("motion", {}),
    }
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    return (
        "/** Design tokens gerados pela Design Aura. Nao edite a mao. */\n"
        f"export const tokens = {body} as const;\n"
        "export type DesignTokens = typeof tokens;\n"
        "export const lightColors = tokens.light;\n"
        "export const darkColors = tokens.dark;\n"
    )


def _swift_color(hex_color: str) -> str:
    rgb = color_to_hex(hex_color)
    if not rgb:
        return "Color.clear"
    value = rgb.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    r = int(value[0:2], 16) / 255.0
    g = int(value[2:4], 16) / 255.0
    b = int(value[4:6], 16) / 255.0
    return f"Color(red: {r:.4f}, green: {g:.4f}, blue: {b:.4f})"


# Sombras nativas por estilo de profundidade: (deslocamento y, desfoque CSS, opacidade) para z1, z2 e z3.
NATIVE_SHADOW = {
    "light": {"hairline": ((1, 2, 0.05), (1, 3, 0.07), (8, 24, 0.16)), "soft": ((2, 8, 0.05), (12, 28, 0.12), (16, 40, 0.20)),
              "tactile": ((3, 8, 0.08), (10, 22, 0.10), (18, 34, 0.13)), "tonal": ((0, 0, 0.0), (0, 0, 0.0), (6, 18, 0.14))},
    "dark": {"hairline": ((0, 0, 0.0), (1, 2, 0.30), (12, 32, 0.60)), "soft": ((2, 8, 0.30), (10, 26, 0.50), (18, 44, 0.62)),
             "tactile": ((2, 10, 0.36), (8, 22, 0.44), (16, 36, 0.54)), "tonal": ((0, 0, 0.0), (0, 0, 0.0), (10, 28, 0.55))},
}
SCHEME_ROLES = [  # papel do Material 3 -> token da Design Aura
    ("primary", "primary"), ("onPrimary", "on-primary"), ("primaryContainer", "primary-surface"), ("onPrimaryContainer", "primary-text"),
    ("secondary", "accent"), ("onSecondary", "on-accent"), ("secondaryContainer", "accent-surface"), ("onSecondaryContainer", "accent-text"),
    ("error", "danger"), ("onError", "on-danger"), ("errorContainer", "danger-surface"), ("onErrorContainer", "danger-text"),
    ("surface", "surface-z2"), ("onSurface", "text-strong"), ("onSurfaceVariant", "text-muted"),
    ("outline", "border-strong"), ("outlineVariant", "border-subtle"),
]


def _px(value) -> float | None:
    m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*(px|dp|pt)?\s*", str(value))
    return float(m.group(1)) if m else None


def _ms(value) -> int | None:
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*ms\s*", str(value))
    return int(float(m.group(1))) if m else None


def _bezier(value) -> tuple[float, ...] | None:
    m = re.fullmatch(r"\s*cubic-bezier\(([^)]*)\)\s*", str(value))
    if not m:
        return None
    nums = [float(x) for x in m.group(1).split(",")]
    return tuple(nums) if len(nums) == 4 else None


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def _family(stack: str) -> str | None:
    first = str(stack or "").split(",")[0].strip().strip("'\"")
    return None if not first or first.lower() in {"system-ui", "-apple-system", "sans-serif", "serif", "ui-monospace", "monospace"} else first


def _native_groups(data: dict) -> dict:
    meta = data.get("meta", {})
    style = str(meta.get("depth_style") or "hairline")
    typo = data.get("typography", {})
    motion = data.get("motion", {})
    return {
        "radius": {k: _px(v) for k, v in data.get("radii", {}).items() if _px(v) is not None},
        "space": {k: _px(v) for k, v in data.get("spacing", {}).items() if _px(v) is not None},
        "size": {k: _px(v) for k, v in data.get("sizing", {}).items() if _px(v) is not None},
        "fonts": {k: _family(typo.get(k, "")) for k in ("font-display", "font-ui", "font-mono")},
        "text_base": _px(typo.get("text-base", "16px")) or 16.0,
        "durations": {k: _ms(v) for k, v in motion.items() if _ms(v) is not None},
        "curves": {k: _bezier(v) for k, v in motion.items() if _bezier(v)},
        "press": float(motion.get("press-scale", 0.97)),
        "shadow": {theme: NATIVE_SHADOW[theme].get(style, NATIVE_SHADOW[theme]["hairline"]) for theme in ("light", "dark")},
    }


def build_swift(data: dict) -> str:
    _, themes = _resolved_themes(data)
    g = _native_groups(data)
    lines = [
        "import SwiftUI",
        "#if canImport(UIKit)",
        "import UIKit",
        "#elseif canImport(AppKit)",
        "import AppKit",
        "#endif",
        "",
        "/// Tokens da Design Aura (gerados; nao edite a mao). Transicoes de navegacao usam as do sistema;",
        "/// Motion vale para respostas do produto e respeita Reduce Motion (guia 10).",
        "enum DesignTokens {",
    ]
    for theme, mapping in themes.items():
        lines.append(f"    enum {theme.capitalize()} {{")
        for key, value in mapping.items():
            if _is_color(value):
                lines.append(f"        static let {_camel(key)} = {_swift_color(value)}")
        lines.append("    }")
        lines.append("")
    lines.append("    /// Cores que acompanham o tema do sistema (claro/escuro).")
    lines.append("    enum Adaptive {")
    for key, value in themes["light"].items():
        if _is_color(value) and _is_color(themes["dark"].get(key, "")):
            name = _camel(key)
            lines.append(f"        static let {name} = Color.designAura(light: Light.{name}, dark: Dark.{name})")
    lines.append("    }")
    lines.append("")
    for enum_name, group, prefix in (("Radius", g["radius"], ""), ("Space", g["space"], "s"), ("Size", g["size"], "")):
        lines.append(f"    enum {enum_name} {{")
        for k, v in group.items():
            lines.append(f"        static let {prefix + _camel(k) if prefix else _camel(k)}: CGFloat = {_num(v)}")
        lines.append("    }")
        lines.append("")
    lines.append("    enum Typography {")
    for k, fam in g["fonts"].items():
        literal = '"' + fam + '"' if fam else "nil"
        lines.append(f"        static let {_camel(k)}: String? = {literal}")
    lines.append(f"        static let textBase: CGFloat = {_num(g['text_base'])}")
    lines.append("    }")
    lines.append("")
    lines.append("    enum Motion {")
    for k, ms in g["durations"].items():
        lines.append(f"        static let {_camel(k)}: Double = {_num(ms / 1000)}")
    lines.append(f"        static let pressScale: CGFloat = {_num(g['press'])}")
    enter = g["durations"].get("duration-enter", 220) / 1000
    for k, (a, b, c, d) in g["curves"].items():
        lines.append(f"        static let {_camel(k)} = Animation.timingCurve({_num(a)}, {_num(b)}, {_num(c)}, {_num(d)}, duration: {_num(enter)})")
    lines.append("    }")
    lines.append("")
    lines.append("    struct Elevation { let y: CGFloat; let radius: CGFloat; let opacity: Double }")
    lines.append("    enum Shadow {")
    for theme, levels in g["shadow"].items():
        for i, (y, blur, op) in enumerate(levels, 1):
            lines.append(f"        static let {theme}Z{i} = Elevation(y: {_num(y)}, radius: {_num(blur / 2)}, opacity: {_num(op)})")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    lines.extend([
        "extension Color {",
        "    /// Cor dinamica: escolhe a variante pelo tema do sistema.",
        "    static func designAura(light: Color, dark: Color) -> Color {",
        "        #if canImport(UIKit)",
        "        return Color(UIColor { traits in traits.userInterfaceStyle == .dark ? UIColor(dark) : UIColor(light) })",
        "        #elseif canImport(AppKit)",
        "        return Color(NSColor(name: nil) { appearance in",
        "            appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? NSColor(dark) : NSColor(light)",
        "        })",
        "        #else",
        "        return light",
        "        #endif",
        "    }",
        "}",
    ])
    return "\n".join(lines) + "\n"


def _argb(hex_color: str) -> str | None:
    rgb = color_to_hex(hex_color)
    if not rgb:
        return None
    value = rgb.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return "FF" + value[0:6].upper()


def _kt_float(x: float) -> str:
    return f"{x:g}f"


def build_kotlin(data: dict) -> str:
    _, themes = _resolved_themes(data)
    g = _native_groups(data)
    lines = [
        "package design.aura",
        "",
        "import androidx.compose.animation.core.CubicBezierEasing",
        "import androidx.compose.foundation.shape.RoundedCornerShape",
        "import androidx.compose.material3.Shapes",
        "import androidx.compose.material3.darkColorScheme",
        "import androidx.compose.material3.lightColorScheme",
        "import androidx.compose.ui.graphics.Color",
        "import androidx.compose.ui.unit.dp",
        "import androidx.compose.ui.unit.sp",
        "",
        "/** Tokens da Design Aura (gerados). Transicao de pagina segue o Material 3 e a escala de animacao do sistema. */",
        "object DesignTokens {",
    ]
    for theme, mapping in themes.items():
        lines.append(f"    object {theme.capitalize()} {{")
        for key, value in mapping.items():
            argb = _argb(value) if _is_color(value) else None
            if argb:
                lines.append(f"        val {_pascal(key)} = Color(0x{argb})")
        lines.append("    }")
        lines.append("")
    for obj, group, prefix in (("Radius", g["radius"], ""), ("Space", g["space"], "S")):
        lines.append(f"    object {obj} {{")
        for k, v in group.items():
            lines.append(f"        val {prefix + _pascal(k)} = {_num(v)}.dp")
        lines.append("    }")
        lines.append("")
    lines.append("    object Size {")
    for k, v in g["size"].items():
        v = max(v, 48.0) if k == "touch-min" else v  # Android: alvo minimo de 48 dp
        lines.append(f"        val {_pascal(k)} = {_num(v)}.dp")
    lines.append("    }")
    lines.append("")
    lines.append("    object Type {")
    lines.append(f"        val TextBase = {_num(g['text_base'])}.sp")
    for k, fam in g["fonts"].items():
        literal = '"' + fam + '"' if fam else "null"
        lines.append(f"        val {_pascal(k)}: String? = {literal}")
    lines.append("    }")
    lines.append("")
    lines.append("    object Motion {")
    for k, ms in g["durations"].items():
        lines.append(f"        const val {_pascal(k)} = {ms}")
    lines.append(f"        const val PressScale = {_kt_float(g['press'])}")
    for k, (a, b, c, d) in g["curves"].items():
        lines.append(f"        val {_pascal(k)} = CubicBezierEasing({_kt_float(a)}, {_kt_float(b)}, {_kt_float(c)}, {_kt_float(d)})")
    lines.append("    }")
    lines.append("")
    lines.append("    object Elevation {")
    for i, level in enumerate(("1", "3", "6"), 1):
        lines.append(f"        val Z{i} = {level}.dp")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    for theme, fn in (("light", "lightColorScheme"), ("dark", "darkColorScheme")):
        obj = theme.capitalize()
        args = [f"    {role} = DesignTokens.{obj}.{_pascal(tok)}," for role, tok in SCHEME_ROLES if _is_color(themes[theme].get(tok, ""))]
        if _is_color(themes[theme].get("surface-z1", "")):
            args.append(f"    background = DesignTokens.{obj}.SurfaceZ1,")
            args.append(f"    onBackground = DesignTokens.{obj}.TextStrong,")
        if _is_color(themes[theme].get("surface-z0", "")):
            args.append(f"    surfaceVariant = DesignTokens.{obj}.SurfaceZ0,")
        lines.append(f"val Aura{obj}ColorScheme = {fn}(")
        lines.extend(args)
        lines.append(")")
        lines.append("")
    r = g["radius"]
    def shape(key, fallback):
        return f"RoundedCornerShape({_num(r.get(key, fallback))}.dp)"
    lines.append("val AuraShapes = Shapes(")
    lines.append(f"    extraSmall = {shape('control-sm', 6)},")
    lines.append(f"    small = {shape('control-md', 8)},")
    lines.append(f"    medium = {shape('card-md', 12)},")
    lines.append(f"    large = {shape('card-lg', 16)},")
    lines.append(")")
    return "\n".join(lines) + "\n"


def build_dart(data: dict) -> str:
    _, themes = _resolved_themes(data)
    g = _native_groups(data)
    lines = [
        "import 'package:flutter/material.dart';",
        "",
        "/// Tokens da Design Aura (gerados). Curvas de pagina seguem a plataforma; Motion vale para respostas do produto.",
        "abstract final class DesignTokens {",
    ]
    for theme, mapping in themes.items():
        for key, value in mapping.items():
            argb = _argb(value) if _is_color(value) else None
            if argb:
                lines.append(f"  static const {theme}{_pascal(key)} = Color(0x{argb});")
        lines.append("")
    for k, v in g["radius"].items():
        lines.append(f"  static const radius{_pascal(k)} = {float(v)};")
    for k, v in g["space"].items():
        lines.append(f"  static const space{_pascal(k)} = {float(v)};")
    for k, v in g["size"].items():
        v = max(v, 48.0) if k == "touch-min" else v
        lines.append(f"  static const {_camel(k)} = {float(v)};")
    lines.append(f"  static const textBase = {float(g['text_base'])};")
    for k, fam in g["fonts"].items():
        literal = "'" + fam + "'" if fam else "null"
        lines.append(f"  static const String? {_camel(k)} = {literal};")
    lines.append("")
    for k, ms in g["durations"].items():
        lines.append(f"  static const {_camel(k)} = Duration(milliseconds: {ms});")
    for k, (a, b, c, d) in g["curves"].items():
        lines.append(f"  static const {_camel(k)} = Cubic({_num(a)}, {_num(b)}, {_num(c)}, {_num(d)});")
    lines.append(f"  static const pressScale = {g['press']};")
    lines.append("")
    for theme, levels in g["shadow"].items():
        for i, (y, blur, op) in enumerate(levels, 1):
            alpha = f"{round(op * 255):02X}"
            body = "[]" if op == 0 else f"[BoxShadow(color: Color(0x{alpha}000000), offset: Offset(0, {float(y)}), blurRadius: {float(blur)})]"
            lines.append(f"  static const {theme}ShadowZ{i} = <BoxShadow>{body};")
    lines.append("")
    for theme, bright in (("light", "Brightness.light"), ("dark", "Brightness.dark")):
        args = [f"    {role}: {theme}{_pascal(tok)}," for role, tok in SCHEME_ROLES if _is_color(themes[theme].get(tok, ""))]
        lines.append(f"  static const {theme}Scheme = ColorScheme(")
        lines.append(f"    brightness: {bright},")
        lines.extend(args)
        lines.append("  );")
        lines.append("")
    lines.extend([
        "  static ThemeData theme(Brightness brightness) => ThemeData(",
        "        useMaterial3: true,",
        "        colorScheme: brightness == Brightness.dark ? darkScheme : lightScheme,",
        "        scaffoldBackgroundColor: brightness == Brightness.dark ? darkSurfaceZ1 : lightSurfaceZ1,",
        "        fontFamily: fontUi,",
        "      );",
        "}",
    ])
    return "\n".join(lines) + "\n"


def build_dtcg(data: dict) -> str:
    """Exporta no formato DTCG 2025.10 ($type/$value) para Figma Variables, Tokens Studio e Style Dictionary."""
    primitives = data.get("primitive", {})
    g = _native_groups(data)
    out: dict = {"$description": f"{data.get('meta', {}).get('brand', 'Projeto')} · Design Aura"}
    for theme in ("light", "dark"):
        tmap = _enrich_semantic_theme({k: resolve_ref(v, primitives) for k, v in data.get("semantic", {}).get(theme, {}).items()}, theme)
        group = {}
        for k, v in tmap.items():
            hexv = color_to_hex(v)
            group[k] = {"$type": "color", "$value": hexv.upper() if hexv else v}
        shadows = {}
        for i, (y, blur, op) in enumerate(g["shadow"][theme], 1):
            shadows[f"z{i}"] = {"$type": "shadow", "$value": {"color": f"#000000{round(op * 255):02X}", "offsetX": "0px",
                                                             "offsetY": f"{_num(y)}px", "blur": f"{_num(blur)}px", "spread": "0px"}}
        out[theme] = {"color": group, "shadow": shadows}
    out["dimension"] = {f"space-{k}": {"$type": "dimension", "$value": v} for k, v in data.get("spacing", {}).items()}
    out["dimension"].update({f"radius-{k}": {"$type": "dimension", "$value": v} for k, v in data.get("radii", {}).items()})
    out["dimension"].update({k: {"$type": "dimension", "$value": v} for k, v in data.get("sizing", {}).items()})
    out["duration"] = {k: {"$type": "duration", "$value": v} for k, v in data.get("motion", {}).items() if str(v).endswith("ms")}
    out["cubicBezier"] = {k: {"$type": "cubicBezier", "$value": list(v)} for k, v in g["curves"].items()}
    out["number"] = {"press-scale": {"$type": "number", "$value": g["press"]}}
    out["fontFamily"] = {k: {"$type": "fontFamily", "$value": v} for k, v in data.get("typography", {}).items() if k.startswith("font-")}
    return json.dumps(out, ensure_ascii=False, indent=2) + "\n"


def write_formats(data: dict, fmt: str, out: Path) -> list[Path]:
    builders = {
        "css": build_css,
        "tailwind": build_tailwind,
        "ts": build_ts,
        "swift": build_swift,
        "kotlin": build_kotlin,
        "dart": build_dart,
        "dtcg": build_dtcg,
    }
    names = {
        "css": "tokens.css",
        "tailwind": "tokens.tailwind.css",
        "ts": "tokens.ts",
        "swift": "DesignTokens.swift",
        "kotlin": "DesignTokens.kt",
        "dart": "design_tokens.dart",
        "dtcg": "tokens.dtcg.json",
    }
    if fmt != "all":
        path = out / names[fmt] if out.suffix == "" else out
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(builders[fmt](data), encoding="utf-8")
        return [path]

    folder = out if out.suffix == "" else out.parent
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for name, builder in builders.items():
        path = folder / names[name]
        path.write_text(builder(data), encoding="utf-8")
        written.append(path)
    return written


def main():
    parser = argparse.ArgumentParser(description="Gera tokens a partir da cor da marca (OKLCH) ou compila um tokens.json.")
    parser.add_argument("input", nargs="?", help="Caminho para tokens.json (dispensavel com --seed)")
    parser.add_argument("--out", default="tokens.css", help="Arquivo ou pasta de saida")
    parser.add_argument("--format", default="css", choices=["css", "tailwind", "ts", "swift", "kotlin", "dart", "dtcg", "all"], help="Formato de exportacao")
    parser.add_argument("--check-contrast", action="store_true", help="Valida WCAG e APCA apos gerar o CSS")
    parser.add_argument("--direction", help="direcao-N.json do Estudio de Direcao: semente, acento, harmonia, profundidade, forma, "
                                                "densidade, tema e fontes. Opcoes explicitas abaixo sobrescrevem a direcao")
    parser.add_argument("--seed", help="Cor principal da marca (#hex, rgb(), hsl(), oklch() ou nome CSS)")
    parser.add_argument("--accent", help="Cor de acento. Sem ela, o acento sai da harmonia escolhida")
    parser.add_argument("--harmony", choices=["complementar", "analoga", "dividida", "triade", "mono"])
    parser.add_argument("--depth-style", choices=["hairline", "soft", "tonal", "tactile"])
    parser.add_argument("--neutral-tint", type=float, help="Croma dos neutros tingidos pela marca (0 a 0.03; padrao 0.012)")
    parser.add_argument("--shape", choices=["sharp", "soft", "round"], help="Linguagem de forma (raios)")
    parser.add_argument("--density", choices=["compact", "regular", "airy"])
    parser.add_argument("--motion", choices=["none", "subtle", "expressive"], help="Personalidade de motion da direcao (padrao subtle)")
    parser.add_argument("--default-theme", choices=["light", "dark"])
    parser.add_argument("--brand")
    parser.add_argument("--font-display", default="")
    parser.add_argument("--font-ui", default="")
    parser.add_argument("--font-mono", default="")
    parser.add_argument("--emit-json", help="Onde gravar o tokens.json gerado por --seed (padrao: ao lado de --out)")
    args = parser.parse_args()

    direction = {}
    if args.direction:
        direction = json.loads(Path(args.direction).read_text(encoding="utf-8"))
    pick = lambda flag, key, default: flag if flag not in (None, "") else (direction.get(key) or default)  # noqa: E731
    seed = pick(args.seed, "seed", None)
    if not args.input and not seed:
        parser.error("informe um tokens.json, --seed ou --direction")

    try:
        if seed:
            from color_engine import build_tokens, parse_color  # noqa: E402

            dfonts = direction.get("fonts") or {}
            fonts = {k: v for k, v in (("display", args.font_display or dfonts.get("display", "")),
                                       ("ui", args.font_ui or dfonts.get("ui", "")),
                                       ("mono", args.font_mono or dfonts.get("mono", ""))) if v}
            accent = pick(args.accent, "accent", None)
            shape = pick(args.shape, "shape", "soft")
            density = pick(args.density, "density", "regular")
            for label, value in (("--seed", seed), ("--accent", accent)):
                if value:
                    try:
                        parse_color(value)
                    except ValueError as exc:
                        parser.error(f"{label}: {exc}")
            data = build_tokens(seed, accent, pick(args.harmony, "harmony", "complementar"), pick(args.depth_style, "depth_style", "hairline"),
                                args.neutral_tint if args.neutral_tint is not None else float(direction.get("neutral_tint", 0.012)),
                                pick(args.brand, "project", "Projeto"), pick(args.default_theme, "default_theme", "light"), fonts, density,
                                pick(args.motion, "motion", "subtle"))
            data["radii"] = SHAPE_RADII.get(shape, SHAPE_RADII["soft"])
            data["meta"]["shape"] = shape
            for key in ("name", "skin"):
                if direction.get(key):
                    data["meta"]["direction" if key == "name" else key] = direction[key]
            for note in data["report"].get("notes", []):
                print(f"[nota] {note}")
            out_path = Path(args.out)
            json_path = Path(args.emit_json) if args.emit_json else (out_path if out_path.suffix == "" else out_path.parent) / "tokens.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"tokens.json gerado pelo motor OKLCH: {json_path}")
            for theme, checks in data["report"]["checks"].items():
                print(f"  {theme}: " + ", ".join(f"{k}={v}" for k, v in checks.items()))
        else:
            src = Path(args.input)
            if not src.exists():
                print(f"Arquivo nao encontrado: {src}", file=sys.stderr)
                sys.exit(1)
            data = json.loads(src.read_text(encoding="utf-8"))
        errors = validate_tokens(data)
        if errors:
            for e in errors:
                print(f"[BLOCK] {e}", file=sys.stderr)
            sys.exit(1)

        written = write_formats(data, args.format, Path(args.out))
        for path in written:
            print(f"Tokens gerados com sucesso: {path}")

        if args.check_contrast:
            css_path = next((p for p in written if p.suffix == ".css" and "tailwind" not in p.name), None)
            if css_path is None:
                css_path = write_formats(data, "css", Path(args.out).with_suffix(".css"))[0]
            results = audit_file(css_path)
            blocks = [r for r in results if r["severity"] == "BLOCK"]
            if blocks:
                for b in blocks:
                    print(f"[BLOCK] {b['theme']} · {b['label']}: {b['reason']}", file=sys.stderr)
                sys.exit(1)
            print(f"Contraste validado: {len(results)} pares WCAG/APCA aprovados em Light & Dark.")
    except Exception as exc:
        print(f"Erro ao gerar tokens: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
