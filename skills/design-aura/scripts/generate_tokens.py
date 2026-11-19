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

from audit_contrast import audit_file  # noqa: E402

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


def main():
    parser = argparse.ArgumentParser(description="Compilador de tokens.json -> tokens.css da Design Aura.")
    parser.add_argument("input", help="Caminho para tokens.json")
    parser.add_argument("--out", default="tokens.css", help="Arquivo CSS de saida")
    parser.add_argument("--check-contrast", action="store_true", help="Valida WCAG e APCA apos gerar")
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

        css_text = build_css(data)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(css_text, encoding="utf-8")
        print(f"Tokens gerados com sucesso: {out_path}")

        if args.check_contrast:
            results = audit_file(out_path)
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
