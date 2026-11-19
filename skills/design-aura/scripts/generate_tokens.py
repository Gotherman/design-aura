#!/usr/bin/env python3
"""Compilador de Design Tokens em 3 camadas (tokens.json -> tokens.css) da Design Aura.

Gera CSS com suporte completo a Light/Dark, 5 planos Z0->Z4, tematizacao de
superficies do browser, tipografia tabular/balanced e prefers-reduced-motion.
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


def build_css(data: dict) -> str:
    meta = data.get("meta", {})
    brand = meta.get("brand", "Design Aura Project")
    version = meta.get("version", "1.0.0")
    default_theme = meta.get("defaultTheme", "dark")

    primitives = data.get("primitive", {})
    semantic = data.get("semantic", {})
    typo = data.get("typography", {})
    spacing = data.get("spacing", {})
    radii = data.get("radii", {})
    motion = data.get("motion", {})

    light_resolved = {k: resolve_ref(v, primitives) for k, v in semantic.get("light", {}).items()}
    dark_resolved = {k: resolve_ref(v, primitives) for k, v in semantic.get("dark", {}).items()}

    base_theme_vars = dark_resolved if default_theme == "dark" else light_resolved

    spacing_vars = {f"space-{k}": v for k, v in spacing.items()}
    radii_vars = {f"radius-{k}": v for k, v in radii.items()}
    motion_vars = {f"motion-{k}": v for k, v in motion.items()}

    css = [
        f"/* {brand} · Design Tokens v{version} (Design Aura) */",
        ":root {",
        emit_css_vars(base_theme_vars),
        emit_css_vars(typo),
        emit_css_vars(spacing_vars),
        emit_css_vars(radii_vars),
        emit_css_vars(motion_vars),
        "  --shadow-z1: 0 0 0 1px rgba(15, 23, 42, 0.08), 0 1px 2px -1px rgba(15, 23, 42, 0.08), 0 2px 6px 0 rgba(15, 23, 42, 0.05);",
        "  --shadow-z2: 0 0 0 1px rgba(15, 23, 42, 0.10), 0 2px 4px -1px rgba(15, 23, 42, 0.08), 0 6px 14px -2px rgba(15, 23, 42, 0.06);",
        "  --shadow-z3: 0 0 0 1px rgba(15, 23, 42, 0.12), 0 6px 16px -4px rgba(15, 23, 42, 0.12), 0 14px 28px -6px rgba(15, 23, 42, 0.08);",
        "}",
        "",
        'html[data-theme="light"], [data-theme="light"] {',
        "  color-scheme: light;",
        emit_css_vars(light_resolved),
        "  --shadow-z1: 0 0 0 1px rgba(15, 23, 42, 0.08), 0 1px 2px -1px rgba(15, 23, 42, 0.08), 0 2px 6px 0 rgba(15, 23, 42, 0.05);",
        "  --shadow-z2: 0 0 0 1px rgba(15, 23, 42, 0.10), 0 2px 4px -1px rgba(15, 23, 42, 0.08), 0 6px 14px -2px rgba(15, 23, 42, 0.06);",
        "  --shadow-z3: 0 0 0 1px rgba(15, 23, 42, 0.12), 0 6px 16px -4px rgba(15, 23, 42, 0.12), 0 14px 28px -6px rgba(15, 23, 42, 0.08);",
        "}",
        "",
        'html[data-theme="dark"], [data-theme="dark"] {',
        "  color-scheme: dark;",
        emit_css_vars(dark_resolved),
        "  --shadow-z1: inset 0 1px 0 rgba(255, 255, 255, 0.05), 0 2px 8px rgba(0, 0, 0, 0.24);",
        "  --shadow-z2: inset 0 1px 0 rgba(255, 255, 255, 0.07), 0 6px 18px rgba(0, 0, 0, 0.30);",
        "  --shadow-z3: inset 0 1px 0 rgba(255, 255, 255, 0.10), 0 14px 32px rgba(0, 0, 0, 0.38);",
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
        "  outline: 2px solid var(--accent);",
        "  outline-offset: 2px;",
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
        raw = {k: resolve_ref(v, primitives) for k, v in semantic.get(theme, {}).items()}
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


def build_swift(data: dict) -> str:
    _, themes = _resolved_themes(data)
    lines = [
        "import SwiftUI",
        "",
        "/// Tokens de cor da Design Aura. Movimento nativo continua no guia 10 (spring interrompivel, Reduce Motion).",
        "enum DesignTokens {",
    ]
    for theme, mapping in themes.items():
        lines.append(f"    enum {theme.capitalize()} {{")
        for key, value in mapping.items():
            if _is_color(value):
                lines.append(f"        static let {_camel(key)} = {_swift_color(value)}")
        lines.append("    }")
        lines.append("")
    motion = data.get("motion", {})
    if motion:
        lines.append("    enum Motion {")
        for key, value in motion.items():
            lines.append(f"        static let {_camel(key)} = \"{value}\"")
        lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def _argb(hex_color: str) -> str | None:
    rgb = color_to_hex(hex_color)
    if not rgb:
        return None
    value = rgb.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return "FF" + value[0:6].upper()


def build_kotlin(data: dict) -> str:
    _, themes = _resolved_themes(data)
    lines = [
        "package design.aura",
        "",
        "import androidx.compose.ui.graphics.Color",
        "",
        "/** Tokens da Design Aura. No Android, duracao de pagina segue Material 3, nao este hex. */",
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
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_dart(data: dict) -> str:
    _, themes = _resolved_themes(data)
    lines = [
        "import 'package:flutter/material.dart';",
        "",
        "/// Tokens da Design Aura. Curvas de pagina no Flutter nao copiam o cubic-bezier do CSS.",
        "abstract final class DesignTokens {",
    ]
    for theme, mapping in themes.items():
        for key, value in mapping.items():
            argb = _argb(value) if _is_color(value) else None
            if argb:
                lines.append(f"  static const {theme}{_pascal(key)} = Color(0x{argb});")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_formats(data: dict, fmt: str, out: Path) -> list[Path]:
    builders = {
        "css": build_css,
        "tailwind": build_tailwind,
        "ts": build_ts,
        "swift": build_swift,
        "kotlin": build_kotlin,
        "dart": build_dart,
    }
    names = {
        "css": "tokens.css",
        "tailwind": "tokens.tailwind.css",
        "ts": "tokens.ts",
        "swift": "DesignTokens.swift",
        "kotlin": "DesignTokens.kt",
        "dart": "design_tokens.dart",
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
    parser = argparse.ArgumentParser(description="Compilador de tokens.json para CSS, Tailwind v4, TS, Swift, Kotlin e Dart.")
    parser.add_argument("input", help="Caminho para tokens.json")
    parser.add_argument("--out", default="tokens.css", help="Arquivo ou pasta de saida")
    parser.add_argument(
        "--format",
        default="css",
        choices=["css", "tailwind", "ts", "swift", "kotlin", "dart", "all"],
        help="Formato de exportacao",
    )
    parser.add_argument("--check-contrast", action="store_true", help="Valida WCAG e APCA apos gerar o CSS")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"Arquivo nao encontrado: {src}", file=sys.stderr)
        sys.exit(1)

    try:
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
