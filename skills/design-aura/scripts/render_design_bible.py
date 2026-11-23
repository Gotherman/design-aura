#!/usr/bin/env python3
"""Gera a Biblia Visual de Design em HTML e PDF sem corte.

Le DESIGN-BIBLE.md e (opcionalmente ou por autodetecao) tokens.css / tokens.json
para renderizar pranchas visuais REAIS (paleta Light/Dark Z0-Z4, tipografia,
botoes, inputs, tabela com tabular-nums, cartao Z2 e mini-shells Desktop/Mobile)
antes das secoes textuais, garantindo que o usuario veja a cara real da UI antes
de aprovar a construcao.
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def parse_tokens_css(css_text: str) -> tuple[dict[str, str], dict[str, str]]:
    """Extrai variaveis CSS para light e dark a partir de tokens.css."""
    light: dict[str, str] = {}
    dark: dict[str, str] = {}

    def extract_vars(block: str) -> dict[str, str]:
        return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", block)}

    # Blocos :root ou [data-theme="light"]
    for m in re.finditer(r"(?::root|html\[data-theme=[\"']light[\"']\]|\[data-theme=[\"']light[\"']\])\s*\{([^}]*)\}", css_text, re.S):
        light.update(extract_vars(m.group(1)))

    for m in re.finditer(r"(?:html\[data-theme=[\"']dark[\"']\]|\[data-theme=[\"']dark[\"']\]|\.dark)\s*\{([^}]*)\}", css_text, re.S):
        dark.update(extract_vars(m.group(1)))

    # Se dark estiver vazio, tenta herdar de root
    if not dark and light:
        dark = dict(light)
    if not light and dark:
        light = dict(dark)

    def resolve_map(mapping: dict[str, str]) -> dict[str, str]:
        resolved = dict(mapping)
        for _ in range(4):
            changed = False
            for k, v in list(resolved.items()):
                m = re.match(r"^var\(\s*(--[a-zA-Z0-9_-]+)\s*(?:,\s*([^)]+))?\)$", v)
                if m:
                    target = m.group(1)
                    fallback = m.group(2).strip() if m.group(2) else ""
                    new_val = resolved.get(target) or light.get(target) or fallback
                    if new_val and new_val != v:
                        resolved[k] = new_val
                        changed = True
            if not changed:
                break
        return resolved

    return resolve_map(light), resolve_map(dark)


def parse_tokens_json(json_text: str) -> tuple[dict[str, str], dict[str, str]]:
    """Extrai tokens de tokens.json suportando schema plano e schema semantic/primitive/typography."""
    data = json.loads(json_text)
    primitives = data.get("primitive") or data.get("primitives") or {}
    typography = data.get("typography") or {}

    def resolve_val(val: str) -> str:
        m = re.match(r"^\{primitive\.([^}]+)\}$", val.strip())
        if m and m.group(1) in primitives:
            return str(primitives[m.group(1)])
        return val

    light: dict[str, str] = {}
    dark: dict[str, str] = {}
    for theme_key, dest in (("light", light), ("dark", dark)):
        block = (
            data.get("semantic", {}).get(theme_key)
            or data.get("themes", {}).get(theme_key)
            or data.get(theme_key)
            or {}
        )
        if isinstance(block, dict):
            for k, v in block.items():
                if isinstance(v, str):
                    dest[f"--{k.lstrip('-')}"] = resolve_val(v)
                elif isinstance(v, dict):
                    for sk, sv in v.items():
                        if isinstance(sv, str):
                            dest[f"--{k}-{sk}"] = resolve_val(sv)
        if isinstance(typography, dict):
            for k, v in typography.items():
                if isinstance(v, str):
                    dest.setdefault(f"--{k.lstrip('-')}", v)
    return light, dark


def pick_token(mapping: dict[str, str], candidates: list[str], default: str) -> str:
    for c in candidates:
        if c in mapping and mapping[c]:
            return mapping[c]
    return default


def build_specimen_board(light: dict[str, str], dark: dict[str, str], title: str) -> str:
    """Renderiza prancha visual real com os tokens de Light e Dark."""
    if not light and not dark:
        return ""

    def theme_palette(m: dict[str, str], is_dark: bool) -> dict[str, str]:
        if is_dark:
            return {
                "z0": pick_token(m, ["--surface-z0", "--bg-well", "--well", "--bg-recess"], "#090E16"),
                "z1": pick_token(m, ["--surface-z1", "--bg-canvas", "--bg", "--canvas"], "#101620"),
                "z2": pick_token(m, ["--surface-z2", "--bg-card", "--card", "--surface"], "#17202E"),
                "z3": pick_token(m, ["--surface-z3", "--bg-elevated", "--popover"], "#1F2B3E"),
                "z4": pick_token(m, ["--surface-z4", "--bg-modal", "--drawer"], "#283750"),
                "brandDark": pick_token(m, ["--surface-brand-dark"], "#0C254A"),
                "brandHeader": pick_token(m, ["--surface-brand-header", "--surface-brand-dark"], "#112C54"),
                "border": pick_token(m, ["--border-card", "--border", "--border-subtle"], "#2C3E58"),
                "borderStrong": pick_token(m, ["--border-strong", "--border-focus"], "#49638A"),
                "textStrong": pick_token(m, ["--text-strong", "--ink-strong", "--fg-strong", "--text"], "#F3F6FB"),
                "textBody": pick_token(m, ["--text-body", "--ink", "--fg", "--text-primary"], "#D6E1F0"),
                "textMuted": pick_token(m, ["--text-muted", "--ink-muted", "--muted"], "#A9BAD1"),
                "primary": pick_token(m, ["--brand-primary", "--primary", "--brand-navy"], "#2563EB"),
                "onPrimary": pick_token(m, ["--on-primary"], "#FFFFFF"),
                "primarySurf": pick_token(m, ["--primary-surface"], "#10264A"),
                "primaryBorder": pick_token(m, ["--primary-border"], "#3B7CF0"),
                "primaryText": pick_token(m, ["--primary-text"], "#7CBCFF"),
                "accent": pick_token(m, ["--brand-accent", "--accent", "--cta", "--accent-deep"], "#C8460E"),
                "onAccent": pick_token(m, ["--on-accent", "--text-on-accent"], "#FFFFFF"),
                "success": pick_token(m, ["--semantic-success", "--success", "--ok"], "#15803D"),
                "onSuccess": pick_token(m, ["--on-success"], "#FFFFFF"),
                "successSurf": pick_token(m, ["--success-surface"], "#0D2B1D"),
                "successBorder": pick_token(m, ["--success-border"], "#22C55E"),
                "successText": pick_token(m, ["--success-text"], "#4ADE80"),
                "warning": pick_token(m, ["--semantic-warning", "--warning", "--warn"], "#F59E0B"),
                "onWarning": pick_token(m, ["--on-warning"], "#140B02"),
                "warningSurf": pick_token(m, ["--warning-surface"], "#2E1F0A"),
                "warningBorder": pick_token(m, ["--warning-border"], "#F59E0B"),
                "warningText": pick_token(m, ["--warning-text"], "#FBBF24"),
                "danger": pick_token(m, ["--semantic-danger", "--danger", "--error"], "#DC2626"),
                "onDanger": pick_token(m, ["--on-danger"], "#FFFFFF"),
                "dangerSurf": pick_token(m, ["--danger-surface"], "#2C1216"),
                "dangerBorder": pick_token(m, ["--danger-border"], "#EF4444"),
                "dangerText": pick_token(m, ["--danger-text"], "#FF6E6E"),
                "info": pick_token(m, ["--semantic-info", "--info"], "#1D6FD6"),
                "infoSurf": pick_token(m, ["--info-surface"], "#102546"),
                "infoBorder": pick_token(m, ["--info-border"], "#3B82F6"),
                "infoText": pick_token(m, ["--info-text"], "#74B8FF"),
                "rim": "inset 0 1px 0 rgba(148,197,255,0.14)",
                "fontDisplay": pick_token(m, ["--font-display", "--font-heading"], "'Geist', 'Inter', system-ui, sans-serif"),
                "fontUi": pick_token(m, ["--font-ui", "--font-sans", "--font-body"], "'Geist', 'Inter', system-ui, sans-serif"),
                "fontMono": pick_token(m, ["--font-mono"], "'Geist Mono', 'JetBrains Mono', ui-monospace, monospace"),
            }
        return {
            "z0": pick_token(m, ["--surface-z0", "--bg-well", "--well", "--bg-recess"], "#C6D6EA"),
            "z1": pick_token(m, ["--surface-z1", "--bg-canvas", "--bg", "--canvas"], "#D9E5F3"),
            "z2": pick_token(m, ["--surface-z2", "--bg-card", "--card", "--surface"], "#FFFFFF"),
            "z3": pick_token(m, ["--surface-z3", "--bg-elevated", "--popover"], "#ECF3FB"),
            "z4": pick_token(m, ["--surface-z4", "--bg-modal", "--drawer"], "#FFFFFF"),
            "brandDark": pick_token(m, ["--surface-brand-dark"], "#0C254A"),
            "brandHeader": pick_token(m, ["--surface-brand-header", "--surface-tint-soft"], "#E3EEFC"),
            "border": pick_token(m, ["--border-card", "--border", "--border-subtle"], "#93ABC7"),
            "borderStrong": pick_token(m, ["--border-strong", "--border-focus"], "#5A769B"),
            "textStrong": pick_token(m, ["--text-strong", "--ink-strong", "--fg-strong", "--text"], "#0E1726"),
            "textBody": pick_token(m, ["--text-body", "--ink", "--fg", "--text-primary"], "#1C2B3F"),
            "textMuted": pick_token(m, ["--text-muted", "--ink-muted", "--muted"], "#3E4E63"),
            "primary": pick_token(m, ["--brand-primary", "--primary", "--brand-navy"], "#14427A"),
            "onPrimary": pick_token(m, ["--on-primary"], "#F8FAFC"),
            "primarySurf": pick_token(m, ["--primary-surface"], "#E3EEFC"),
            "primaryBorder": pick_token(m, ["--primary-border"], "#8EB4E6"),
            "primaryText": pick_token(m, ["--primary-text", "--primary"], "#14427A"),
            "accent": pick_token(m, ["--brand-accent", "--accent", "--cta", "--accent-deep"], "#C2410C"),
            "onAccent": pick_token(m, ["--on-accent", "--text-on-accent"], "#FFFFFF"),
            "success": pick_token(m, ["--semantic-success", "--success", "--ok"], "#15803D"),
            "onSuccess": pick_token(m, ["--on-success"], "#FFFFFF"),
            "successSurf": pick_token(m, ["--success-surface"], "#DCFCE7"),
            "successBorder": pick_token(m, ["--success-border"], "#16A34A"),
            "successText": pick_token(m, ["--success-text", "--success"], "#15803D"),
            "warning": pick_token(m, ["--semantic-warning", "--warning", "--warn"], "#B45309"),
            "onWarning": pick_token(m, ["--on-warning"], "#FFFFFF"),
            "warningSurf": pick_token(m, ["--warning-surface"], "#FEF3C7"),
            "warningBorder": pick_token(m, ["--warning-border"], "#D97706"),
            "warningText": pick_token(m, ["--warning-text"], "#9A4A06"),
            "danger": pick_token(m, ["--semantic-danger", "--danger", "--error"], "#B91C1C"),
            "onDanger": pick_token(m, ["--on-danger"], "#FFFFFF"),
            "dangerSurf": pick_token(m, ["--danger-surface"], "#FEE2E2"),
            "dangerBorder": pick_token(m, ["--danger-border"], "#DC2626"),
            "dangerText": pick_token(m, ["--danger-text", "--danger"], "#B91C1C"),
            "info": pick_token(m, ["--semantic-info", "--info"], "#1D4ED8"),
            "infoSurf": pick_token(m, ["--info-surface"], "#DBEAFE"),
            "infoBorder": pick_token(m, ["--info-border"], "#2563EB"),
            "infoText": pick_token(m, ["--info-text", "--info"], "#1D4ED8"),
            "rim": "inset 0 1px 0 rgba(255,255,255,0.85)",
            "fontDisplay": pick_token(m, ["--font-display", "--font-heading"], "'Geist', 'Inter', system-ui, sans-serif"),
            "fontUi": pick_token(m, ["--font-ui", "--font-sans", "--font-body"], "'Geist', 'Inter', system-ui, sans-serif"),
            "fontMono": pick_token(m, ["--font-mono"], "'Geist Mono', 'JetBrains Mono', ui-monospace, monospace"),
        }

    lp = theme_palette(light, False)
    dp = theme_palette(dark, True)

    ico_ok = '<svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5 6.5 12 13 4.5"/></svg>'
    ico_warn = '<svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2.2 14.2 13H1.8Z"/><path d="M8 6.2v3.2M8 11.4h.01"/></svg>'
    ico_err = '<svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="8" cy="8" r="6"/><path d="m5.7 5.7 4.6 4.6m0-4.6-4.6 4.6"/></svg>'
    ico_info = '<svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="8" cy="8" r="6"/><path d="M8 7.4v3.4M8 5.2h.01"/></svg>'

    def render_theme_card(label: str, p: dict[str, str]) -> str:
        e = html.escape
        swatches = [
            ("Z1 Canvas", p["z1"]),
            ("Z2 Card", p["z2"]),
            ("Marca/Head", p["brandHeader"]),
            ("Primary", p["primary"]),
            ("Success", p["success"]),
            ("Danger", p["danger"]),
        ]
        sw_html = "".join(
            f'<div class="sp-sw">'
            f'<div class="sp-sw-chip" style="background:{e(val)};border-color:{e(p["borderStrong"])}"></div>'
            f'<span class="sp-sw-name" style="color:{e(p["textStrong"])}">{e(name)}</span>'
            f'<code class="sp-sw-val" style="color:{e(p["textMuted"])}">{e(val)}</code>'
            f'</div>'
            for name, val in swatches
        )
        return f"""
        <div class="sp-panel" style="background:{e(p['z1'])};color:{e(p['textBody'])};border:1.25px solid {e(p['border'])};font-family:{e(p['fontUi'])}">
          <div class="sp-panel-head" style="background:{e(p['brandHeader'])};border-bottom:1px solid {e(p['border'])};margin:-3mm -3mm 0;padding:2.2mm 3mm;border-radius:2.2mm 2.2mm 0 0">
            <strong style="color:{e(p['textStrong'])};font-family:{e(p['fontDisplay'])}">{e(label)}</strong>
            <span class="sp-mono" style="color:{e(p['textMuted'])};font-family:{e(p['fontMono'])}">{e(p['z1'])} → {e(p['z2'])}</span>
          </div>
          <div class="sp-swatch-grid">{sw_html}</div>
          <div class="sp-tabs" style="background:{e(p['z0'])};border:1px solid {e(p['border'])}">
            <span class="sp-tab is-active" style="background:{e(p['primary'])};color:{e(p['onPrimary'])};box-shadow:{e(p['rim'])}">Aguardando <b>6</b></span>
            <span class="sp-tab" style="color:{e(p['textBody'])}">Em revisão <b>2</b></span>
            <span class="sp-tab" style="color:{e(p['textBody'])}">Concluídas <b>14</b></span>
          </div>
          <div class="sp-card" style="background:{e(p['z2'])};border:1.25px solid {e(p['border'])};color:{e(p['textBody'])};box-shadow:{e(p['rim'])}">
            <div class="sp-card-top">
              <div>
                <div class="sp-title" style="color:{e(p['textStrong'])};font-family:{e(p['fontDisplay'])}">Conferência Focada · Superfície Z2</div>
                <div class="sp-sub" style="color:{e(p['textMuted'])}">Protocolo <code style="background:{e(p['z0'])};color:{e(p['textStrong'])}">#2408</code> · Turno Manhã</div>
              </div>
              <span class="sp-squircle" style="background:{e(p['dangerSurf'])};color:{e(p['dangerText'])};border:1px solid {e(p['dangerBorder'])}">{ico_err} Crítico</span>
            </div>
            <div class="sp-diff-strip" style="background:{e(p['z0'])};border:1px solid {e(p['border'])}">
              <span class="sp-diff-old" style="color:{e(p['textMuted'])}">Antes: <s>--:--</s></span>
              <span style="color:{e(p['primaryText'])};font-weight:700">→</span>
              <span class="sp-diff-new" style="background:{e(p['primarySurf'])};color:{e(p['primaryText'])};border:1px solid {e(p['primaryBorder'])}">Proposto: 07:00 · 16:00</span>
            </div>
            <div class="sp-badges">
              <span class="sp-squircle" style="background:{e(p['successSurf'])};color:{e(p['successText'])};border:1px solid {e(p['successBorder'])}">{ico_ok} Em dia</span>
              <span class="sp-squircle" style="background:{e(p['warningSurf'])};color:{e(p['warningText'])};border:1px solid {e(p['warningBorder'])}">{ico_warn} Aguardando</span>
              <span class="sp-squircle" style="background:{e(p['dangerSurf'])};color:{e(p['dangerText'])};border:1px solid {e(p['dangerBorder'])}">{ico_err} Falha</span>
              <span class="sp-squircle" style="background:{e(p['infoSurf'])};color:{e(p['infoText'])};border:1px solid {e(p['infoBorder'])}">{ico_info} Info</span>
            </div>
            <div class="sp-alert" style="background:{e(p['warningSurf'])};border:1px solid {e(p['warningBorder'])};border-left:2.4px solid {e(p['warningBorder'])};color:{e(p['warningText'])}">
              {ico_warn} <span>Confirmação explícita obrigatória para ações críticas · Toast com Desfazer.</span>
            </div>
            <div class="sp-actions">
              <span class="sp-btn" style="background:{e(p['success'])};color:{e(p['onSuccess'])};border:1px solid {e(p['success'])};box-shadow:{e(p['rim'])}">Aprovar</span>
              <span class="sp-btn" style="background:{e(p['z3'])};color:{e(p['textStrong'])};border:1px solid {e(p['borderStrong'])}">Devolver</span>
              <span class="sp-btn" style="background:{e(p['dangerSurf'])};color:{e(p['dangerText'])};border:1px solid {e(p['dangerBorder'])}">Indeferir</span>
              <span class="sp-btn" style="background:{e(p['accent'])};color:{e(p['onAccent'])};border:1px solid {e(p['accent'])}">Ação</span>
            </div>
          </div>
        </div>
        """

    return f"""
    <section class="specimen-sheet" aria-label="Prancha Visual de Tokens">
      <div class="specimen-head">
        <span class="specimen-kicker">Espécime Visual Studio · Paridade Cromática Light &amp; Dark · {html.escape(title)}</span>
        <p>Prancha gerada diretamente de <code>tokens.css</code>: valida profundidade Z0→Z4, cabeçalhos com cor da marca (zero monobloco cinza/branco), badges squircle 6px com ícone semântico e paridade de cor (vermelho=falha, verde=sucesso, âmbar=atenção, azul=marca) nos dois modos.</p>
      </div>
      <div class="specimen-grid">
        {render_theme_card("Dark Mode (Profundidade Z0 → Z4 + Marca)", dp)}
        {render_theme_card("Light Mode (Canvas Aterrado + Marca)", lp)}
      </div>
    </section>
    """


def build_golden_gallery(golden_paths: list[tuple[str, Path]]) -> str:
    if not golden_paths:
        return ""
    cards = []
    for label, p in golden_paths:
        if not p.exists():
            continue
        cards.append(
            f'<figure class="golden-fig">'
            f'<figcaption>{html.escape(label)} <code>{html.escape(p.name)}</code></figcaption>'
            f'<img src="{html.escape(p.resolve().as_uri())}" alt="{html.escape(label)}">'
            f'</figure>'
        )
    if not cards:
        return ""
    return (
        '<section class="specimen-sheet" aria-label="Telas-Mae Renderizadas">'
        '<div class="specimen-head"><span class="specimen-kicker">Telas-Mae (Golden Screens)</span>'
        '<p>Capturas reais das telas-mae que travam o padrao estetico e funcional para todos os subagentes.</p></div>'
        f'<div class="golden-grid">{"".join(cards)}</div></section>'
    )


def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    escaped = re.sub(
        r"#([0-9A-Fa-f]{6})",
        r'<span class="swatch" style="background:#\1"></span>#\1',
        escaped,
    )
    return escaped


def markdown_to_body(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush_paragraph()
            fence = line[3:].strip().lower()
            buff = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buff.append(lines[i])
                i += 1
            raw_code = "\n".join(buff)
            if fence in {"html-specimen", "html preview", "specimen"}:
                out.append(f'<div class="live-specimen">{raw_code}</div>')
            else:
                out.append("<pre><code>" + html.escape(raw_code) + "</code></pre>")
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*-+", lines[i + 1]):
            flush_paragraph()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            head, body = rows[0], rows[2:]
            table = ["<table><thead><tr>"]
            table.extend(f"<th>{inline(cell)}</th>" for cell in head)
            table.append("</tr></thead><tbody>")
            for row in body:
                table.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>")
            table.append("</tbody></table>")
            out.append("".join(table))
            continue
        if line.startswith("#"):
            flush_paragraph()
            level = min(len(line) - len(line.lstrip("#")), 3)
            title = line.lstrip("#").strip()
            out.append(f"<h{level}>{inline(title)}</h{level}>")
            i += 1
            continue
        if re.match(r"^(\s*)[-*] ", line):
            flush_paragraph()
            out.append("<ul>")
            while i < len(lines) and re.match(r"^(\s*)[-*] ", lines[i]):
                item = re.sub(r"^(\s*)[-*] ", "", lines[i])
                out.append(f"<li>{inline(item)}</li>")
                i += 1
            out.append("</ul>")
            continue
        if re.match(r"^---+$", line.strip()):
            flush_paragraph()
            out.append("<hr>")
            i += 1
            continue
        if line.strip() == "":
            flush_paragraph()
            i += 1
            continue
        if line.startswith(">"):
            flush_paragraph()
            out.append(f"<blockquote><p>{inline(line.lstrip('> ').strip())}</p></blockquote>")
            i += 1
            continue
        paragraph.append(line.strip())
        i += 1
    flush_paragraph()
    return "\n".join(out)


PAPER_CSS = """
@page { size: A4 portrait; margin: 14mm 13mm 16mm; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  color: #0F172A;
  background: #F8FAFC;
  font-family: "Plus Jakarta Sans", "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 10.5pt;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
main { max-width: 184mm; margin: 0 auto; padding: 6mm 0 12mm; }
h1 { font-size: 20pt; line-height: 1.15; letter-spacing: -0.025em; margin: 0 0 5mm; color: #0B1320; }
h2 { font-size: 13.5pt; line-height: 1.25; letter-spacing: -0.015em; margin: 7mm 0 3mm; padding-top: 3mm; border-top: 0.3mm solid #CBD5E1; color: #0F172A; break-after: avoid; }
h3 { font-size: 11pt; margin: 4.5mm 0 2mm; color: #1E293B; break-after: avoid; }
p, li { orphans: 3; widows: 3; color: #334155; }
ul { margin: 0 0 3.5mm; padding-left: 5mm; }
li { margin: 0.8mm 0; }
hr { border: 0; border-top: 0.3mm solid #CBD5E1; margin: 5mm 0; }
code, pre { font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace; font-size: 8.5pt; }
code { background: #E2E8F0; color: #0F172A; padding: 0.3mm 1.3mm; border-radius: 1mm; }
.swatch { display: inline-block; width: 3mm; height: 3mm; margin-right: 1mm; border-radius: 0.6mm; border: 0.25mm solid rgba(15,23,42,0.3); vertical-align: -0.4mm; }
pre, table, blockquote, .specimen-sheet, .live-specimen { break-inside: avoid; }
pre { white-space: pre-wrap; background: #0F172A; color: #E2E8F0; padding: 3.5mm 4mm; border-radius: 2mm; }
pre code { background: transparent; color: inherit; padding: 0; }
table { width: 100%; border-collapse: collapse; margin: 0 0 4.5mm; background: #FFFFFF; border: 0.3mm solid #CBD5E1; border-radius: 1.5mm; }
th, td { border-bottom: 0.25mm solid #E2E8F0; text-align: left; vertical-align: top; padding: 1.8mm 2.2mm; font-size: 9.2pt; }
th { background: #F1F5F9; color: #0F172A; font-weight: 700; font-size: 8.5pt; }
blockquote { margin: 0 0 4mm; padding: 2mm 3.5mm; border-left: 0.9mm solid #2563EB; background: #EFF6FF; color: #1E3A5F; border-radius: 0 1.5mm 1.5mm 0; }

.specimen-sheet { margin: 4mm 0 6mm; padding: 4mm; background: #FFFFFF; border: 0.35mm solid #CBD5E1; border-radius: 3mm; }
.specimen-head { margin-bottom: 3mm; }
.specimen-kicker { display: inline-block; font-family: "JetBrains Mono", monospace; font-size: 8pt; font-weight: 700; color: #0F2942; background: #E2E8F0; padding: 0.8mm 2mm; border-radius: 1.5mm; margin-bottom: 1.5mm; }
.specimen-head p { margin: 0; font-size: 9pt; color: #475569; }
.specimen-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3.5mm; }
.sp-panel { border-radius: 2.5mm; padding: 3mm; display: flex; flex-direction: column; gap: 2.5mm; }
.sp-panel-head { display: flex; align-items: center; justify-content: space-between; padding-bottom: 1.8mm; font-size: 9pt; }
.sp-mono { font-size: 7.5pt; }
.sp-swatch-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.8mm; }
.sp-sw { display: flex; flex-direction: column; gap: 0.6mm; }
.sp-sw-chip { height: 7mm; border-radius: 1.2mm; border: 0.3mm solid transparent; }
.sp-sw-name { font-size: 7.5pt; font-weight: 700; }
.sp-sw-val { font-size: 7pt; background: transparent; padding: 0; }
.sp-card { border-radius: 2mm; padding: 2.8mm; display: flex; flex-direction: column; gap: 2mm; }
.sp-card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 2mm; }
.sp-title { font-size: 9.5pt; font-weight: 700; }
.sp-sub { font-size: 7.5pt; }
.sp-kpi { font-size: 10pt; font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }
.sp-tabs { display: flex; gap: 1mm; padding: 0.9mm; border-radius: 1.6mm; }
.sp-tab { font-size: 7.2pt; font-weight: 600; padding: 0.8mm 1.8mm; border-radius: 1.1mm; display: inline-flex; align-items: center; gap: 1mm; }
.sp-tab b { font-family: "JetBrains Mono", monospace; font-size: 6.8pt; opacity: 0.88; }
.sp-diff-strip { display: flex; align-items: center; gap: 1.8mm; padding: 1.2mm 2mm; border-radius: 1.4mm; font-size: 7.3pt; font-family: "JetBrains Mono", monospace; }
.sp-diff-new { padding: 0.4mm 1.4mm; border-radius: 1mm; font-weight: 700; }
.sp-badges { display: flex; flex-wrap: wrap; gap: 1.3mm; }
.sp-squircle { display: inline-flex; align-items: center; gap: 1mm; font-size: 7.2pt; font-weight: 700; padding: 0.65mm 1.8mm; border-radius: 6px; }
.sp-alert { display: flex; align-items: center; gap: 1.4mm; font-size: 7pt; font-weight: 600; padding: 1.1mm 1.8mm; border-radius: 1.4mm; }
.sp-actions { display: flex; flex-wrap: wrap; gap: 1.4mm; align-items: center; }
.sp-btn { font-size: 7.6pt; font-weight: 700; padding: 1.1mm 2.3mm; border-radius: 1.4mm; display: inline-block; }
.sp-input { font-size: 7.5pt; padding: 1.2mm 2.2mm; border-radius: 1.4mm; flex: 1; min-width: 24mm; }
.live-specimen { margin: 3.5mm 0 5mm; padding: 3.5mm; background: #FFFFFF; border: 0.35mm solid #CBD5E1; border-radius: 2.5mm; }
.golden-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3.5mm; }
.golden-fig { margin: 0; border: 0.3mm solid #CBD5E1; border-radius: 2mm; padding: 2mm; background: #F8FAFC; }
.golden-fig figcaption { font-size: 8pt; font-weight: 700; margin-bottom: 1.5mm; color: #0F172A; }
.golden-fig img { width: 100%; height: auto; border-radius: 1.2mm; display: block; border: 0.25mm solid #CBD5E1; }
@media print { body { background: #FFFFFF; } }
"""


def sync_markdown_token_tables(
    md: str,
    tokens_light: dict[str, str],
    tokens_dark: dict[str, str],
) -> tuple[str, list[str]]:
    """Sincroniza hexes em tabelas Markdown (ex.: Secao 8.1) contra tokens.css atual.

    Detecta a ordem real das colunas (Light|Dark vs Dark|Light) pelo cabecalho
    da tabela, evitando inversao em tokens escuros como --danger (#B91C1C) ou --primary (#14427A).
    """
    if not tokens_light and not tokens_dark:
        return md, []
    hex_re = re.compile(r"#[0-9A-Fa-f]{6}\b")
    var_re = re.compile(r"--([a-zA-Z0-9_-]+)")
    synced_vars: list[str] = []
    new_lines: list[str] = []
    table_first_is_dark: bool | None = None

    for line in md.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            table_first_is_dark = None
            new_lines.append(line)
            continue

        # Detecta cabecalho de tabela com colunas Light/Claro e Dark/Escuro
        if "--" not in line and not re.match(r"^\|[\s:\-|]+\|$", stripped):
            cells_low = [c.strip().lower() for c in stripped.strip("|").split("|")]
            dark_idx = next((i for i, c in enumerate(cells_low) if "dark" in c or "escuro" in c), None)
            light_idx = next((i for i, c in enumerate(cells_low) if "light" in c or "claro" in c), None)
            if dark_idx is not None and light_idx is not None and dark_idx != light_idx:
                table_first_is_dark = dark_idx < light_idx

        if "--" in line:
            cells = line.split("|")
            token_name = None
            for cell in cells:
                m_var = var_re.search(cell)
                if m_var:
                    cand = f"--{m_var.group(1)}"
                    if cand in tokens_dark or cand in tokens_light:
                        token_name = cand
                        break
            if token_name:
                d_val = tokens_dark.get(token_name, "")
                l_val = tokens_light.get(token_name, "")
                hexes = hex_re.findall(line)
                if len(hexes) >= 2 and d_val.startswith("#") and l_val.startswith("#"):
                    h0, h1 = hexes[0].upper(), hexes[1].upper()
                    du, lu = d_val.upper(), l_val.upper()
                    if table_first_is_dark is not None:
                        first_is_dark = table_first_is_dark
                    else:
                        s0 = int(h0[1:3], 16) + int(h0[3:5], 16) + int(h0[5:7], 16)
                        s1 = int(h1[1:3], 16) + int(h1[3:5], 16) + int(h1[5:7], 16)
                        first_is_dark = s0 < s1
                    rep0 = du if first_is_dark else lu
                    rep1 = lu if first_is_dark else du
                    if (h0, h1) != (rep0, rep1):
                        updated = hex_re.sub("__HEX_SLOT__", line, count=2)
                        updated = updated.replace("__HEX_SLOT__", rep0, 1).replace("__HEX_SLOT__", rep1, 1)
                        if updated != line:
                            line = updated
                            synced_vars.append(token_name)
        new_lines.append(line)
    return "\n".join(new_lines) + ("\n" if md.endswith("\n") else ""), synced_vars


def check_inline_token_values(
    markdown: str, light: dict[str, str], dark: dict[str, str]
) -> list[str]:
    """Verifica declarações explícitas como `border-subtle` Light `#86A2C7`."""
    pattern = re.compile(
        r"`(?P<token>[-\w]+)`[ \t]+(?P<theme>Light|Claro|Dark|Escuro)[ \t]+"
        r"`(?P<value>#[a-f0-9]{6})(?=`|[ \t])",
        re.IGNORECASE,
    )
    differences = []
    for match in pattern.finditer(markdown):
        token = "--" + match["token"].removeprefix("--")
        theme = match["theme"]
        active = light if theme.lower() in {"light", "claro"} else dark
        expected = active.get(token)
        if expected and re.fullmatch(r"#[0-9a-fA-F]{6}", expected) and expected.lower() != match["value"].lower():
            differences.append(f"{token} {theme}: {match['value']} → {expected}")
    return differences


# ------------------------------------------------------------------ completude e diagramas de zona

REQUIRED_SECTIONS = [
    ("Contrato de plataforma", r"contrato de plataforma"),
    ("Direção escolhida", r"dire[cç][aã]o"),
    ("Cor", r"\bcor\b|paleta|crom"),
    ("Tipografia", r"tipograf"),
    ("Espaço e forma", r"espa[cç]o|escala espacial|forma"),
    ("Profundidade", r"profundidade|planos"),
    ("Orçamentos do projeto", r"or[cç]amento"),
    ("Componentes", r"componente"),
    ("Telas", r"telas|mapa de telas"),
    ("Motion", r"motion|movimento"),
    ("Conteúdo e dados", r"conte[uú]do|dados fict"),
    ("Leis do projeto", r"leis do projeto"),
    ("Verificação", r"port[oõ]es|verifica[cç][aã]o"),
    ("Histórico", r"hist[oó]rico"),
]
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}|:\*\*\s*\.\.\.\s*$|:\s*\.\.\.\s*$|_a fixar_|_descrever_", re.M)


def zone_width(z: dict) -> float:
    w = z.get("width")
    if isinstance(w, (int, float)):
        return float(w)
    return float(z.get("min", 0) or 0)


def check_zones(manifest: dict) -> list[str]:
    errors = []
    project_min = int((manifest.get("project") or {}).get("minDesktopWidth", 1024))
    for scr in manifest.get("screens", []):
        zones = scr.get("zones") or []
        if not zones or scr.get("platform") == "mobile":
            continue
        min_w = int(scr.get("minWidth", project_min))
        gap = int(scr.get("zoneGap", 16))
        total = sum(zone_width(z) for z in zones) + gap * (len(zones) - 1)
        if total > min_w:
            parts = " + ".join(f"{z.get('name')} {zone_width(z):.0f}" for z in zones)
            errors.append(f"Tela {scr.get('id')}: zonas somam {total:.0f}px ({parts} + gaps) e nao cabem na largura minima {min_w}px. Recolha uma zona em drawer ou suba a largura minima.")
    return errors


def zone_diagrams(manifest: dict) -> str:
    cards = []
    for scr in manifest.get("screens", []):
        zones = scr.get("zones") or []
        if not zones:
            continue
        min_w = int(scr.get("minWidth", (manifest.get("project") or {}).get("minDesktopWidth", 1024)))
        width, height, pad = 560, 150, 6
        fixed = sum(float(z["width"]) for z in zones if isinstance(z.get("width"), (int, float)))
        frs = [z for z in zones if not isinstance(z.get("width"), (int, float))]
        free = max(0.0, min_w - fixed - 16 * (len(zones) - 1))
        x = pad
        rects = []
        scale = (width - 2 * pad) / max(min_w, fixed + sum(zone_width(z) for z in frs))
        for z in zones:
            w_px = float(z["width"]) if isinstance(z.get("width"), (int, float)) else max(zone_width(z), free / max(1, len(frs)))
            w = max(24.0, w_px * scale)
            label = html.escape(str(z.get("name", "")))
            size = f"{int(w_px)}px" if isinstance(z.get("width"), (int, float)) else f"{z.get('width', '1fr')} (min {int(zone_width(z))})"
            rects.append(f'<rect x="{x:.1f}" y="{pad}" width="{w - 4:.1f}" height="{height - 2 * pad}" rx="6" class="zone"/>'
                         f'<text x="{x + 8:.1f}" y="{pad + 20}" class="zl">{label}</text><text x="{x + 8:.1f}" y="{pad + 36}" class="zs">{html.escape(size)}</text>')
            x += w
        over = x - pad > width - 2 * pad + 1
        action = scr.get("primaryAction") or {}
        action_txt = action.get("label", "") if isinstance(action, dict) else str(action)
        cards.append(f'<figure class="zone-card{" over" if over else ""}"><figcaption><strong>{html.escape(str(scr.get("title", scr.get("id"))))}</strong>'
                     f' · {html.escape(str(scr.get("archetype", "")))} · min {min_w}px{" · ação: " + html.escape(action_txt) if action_txt else ""}</figcaption>'
                     f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="Zonas de {html.escape(str(scr.get("id")))}">{"".join(rects)}</svg></figure>')
    if not cards:
        return ""
    style = ("<style>.zone-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0 24px}.zone-card{margin:0;padding:10px;border:1px solid #d0d5dd;border-radius:8px;break-inside:avoid}"
             ".zone-card.over{border-color:#b42318}.zone{fill:#eef2f6;stroke:#98a2b3}.zl{font:600 12px system-ui;fill:#101828}.zs{font:11px system-ui;fill:#475467}"
             ".zone-card figcaption{font:12px system-ui;color:#344054;margin-bottom:6px}</style>")
    return f'{style}<section class="zones"><h2>Diagramas de zona (gerados do manifesto)</h2><div class="zone-grid">{"".join(cards)}</div></section>'


def check_bible(md: str, manifest: dict | None, tokens_light: dict[str, str] | None) -> list[str]:
    """Aponta decisoes que a Biblia ainda nao tomou. Sem isto ela nao chega ao Portao 1."""
    errors = []
    if not re.search(r"\*\*Design Aura:\*\*\s*`v\d+\.\d+\.\d+`", md):
        errors.append("Selo '**Design Aura:** `vX.Y.Z`' ausente no topo.")
    headings = "\n".join(line.lower() for line in md.splitlines() if line.startswith("#"))
    for name, pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, headings):
            errors.append(f"Seção ausente: {name}.")
    for m in PLACEHOLDER.finditer(md):
        line = md[: m.start()].count("\n") + 1
        errors.append(f"Linha {line}: decisão em aberto ({m.group(0).strip()[:40]}).")
        if len(errors) > 40:
            break
    tl = tokens_light or {}
    if tl:
        for key, why in (("primary-surface", "cor de seleção e item ativo"), ("chart-1", "paleta de gráficos"), ("danger", "estado de erro")):
            if not any(k.lstrip("-") == key for k in tl):
                errors.append(f"Token ausente: --{key} ({why}).")
    if manifest:
        ids_in_text = set(re.findall(r"`([a-z0-9][a-z0-9-]{1,})`", md))
        for scr in manifest.get("screens", []):
            sid = scr.get("id", "?")
            missing = [f for f in ("archetype", "primaryAction", "states") if not scr.get(f)]
            if missing:
                errors.append(f"Tela {sid}: faltam {', '.join(missing)} no manifesto.")
            if sid not in ids_in_text and sid not in md:
                errors.append(f"Tela {sid} não aparece na Bíblia.")
        errors.extend(check_zones(manifest))
    return errors


def build_html(
    md: str,
    title: str,
    tokens_light: dict[str, str] | None = None,
    tokens_dark: dict[str, str] | None = None,
    golden_paths: list[tuple[str, Path]] | None = None,
    manifest: dict | None = None,
) -> str:
    md_synced, _ = sync_markdown_token_tables(md, tokens_light or {}, tokens_dark or {})
    body = markdown_to_body(md_synced)
    specimen = build_specimen_board(tokens_light or {}, tokens_dark or {}, title)
    golden = build_golden_gallery(golden_paths or []) + (zone_diagrams(manifest) if manifest else "")
    # Insere a prancha visual logo apos o primeiro <h1> se existir
    if specimen or golden:
        visual_block = specimen + golden
        m = re.search(r"</h1>", body)
        if m:
            body = body[: m.end()] + "\n" + visual_block + "\n" + body[m.end() :]
        else:
            body = visual_block + "\n" + body
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>{PAPER_CSS}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def find_browser() -> str | None:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


def write_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    subprocess.run(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            f"--print-to-pdf={pdf_path}",
            "--no-pdf-header-footer",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def load_tokens_for_bible(source: Path, explicit_tokens: str) -> tuple[dict[str, str], dict[str, str]]:
    candidates: list[Path] = []
    if explicit_tokens:
        candidates.append(Path(explicit_tokens))
    else:
        candidates.extend([
            source.parent / "tokens.css",
            source.parent / "tokens.json",
            source.parent / "telas" / "tokens.css",
        ])
    for cand in candidates:
        if cand.exists():
            raw = cand.read_text(encoding="utf-8", errors="ignore")
            if cand.suffix.lower() == ".json":
                return parse_tokens_json(raw)
            return parse_tokens_css(raw)
    return {}, {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Renderiza a Biblia Visual de Design em HTML e PDF sem corte.")
    parser.add_argument("markdown", help="DESIGN-BIBLE.md")
    parser.add_argument("--out-dir", default=".", help="Pasta de saida")
    parser.add_argument("--tokens", default="", help="Caminho opcional para tokens.css ou tokens.json (autodetectado por padrao)")
    parser.add_argument("--golden-desktop", default="", help="Screenshot opcional da Tela-Mae Desktop")
    parser.add_argument("--golden-mobile", default="", help="Screenshot opcional da Tela-Mae Mobile")
    parser.add_argument("--check-sync", action="store_true", help="Verifica referências de tokens sem escrever artefatos")
    parser.add_argument("--shell", type=Path, help="Contrato de shell a conferir junto da Bíblia com --check-sync")
    parser.add_argument("--compare-css", type=Path, action="append", default=[], help="Cópia compilada a comparar byte a byte com --tokens")
    parser.add_argument("--manifest", type=Path, help="screen-manifest.json: gera diagramas de zona e confere as telas")
    parser.add_argument("--check", action="store_true", help="Confere se a Biblia tomou todas as decisoes (sem escrever artefatos)")
    args = parser.parse_args()
    if (args.shell or args.compare_css) and not args.check_sync:
        parser.error("--shell e --compare-css requerem --check-sync")
    if args.compare_css and (not args.tokens or Path(args.tokens).suffix.lower() != ".css"):
        parser.error("--compare-css requer um arquivo CSS em --tokens")

    source = Path(args.markdown)
    if not source.exists():
        print(f"Arquivo nao encontrado: {source}", file=sys.stderr)
        sys.exit(1)
    text = source.read_text(encoding="utf-8")
    title = "Biblia de Design"
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    tokens_light, tokens_dark = load_tokens_for_bible(source, args.tokens)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8")) if args.manifest else None
    if args.check:
        problems = check_bible(text, manifest, tokens_light)
        if problems:
            print(f"Biblia incompleta ({len(problems)} pendencia(s)):", file=sys.stderr)
            for prob in problems:
                print(f"- {prob}", file=sys.stderr)
            sys.exit(1)
        print("Biblia completa: secoes, decisoes, telas e zonas conferidas.")
        return
    text_synced, synced_vars = sync_markdown_token_tables(text, tokens_light, tokens_dark)
    if args.check_sync:
        if not tokens_light or not tokens_dark:
            parser.error("Nenhum token Light/Dark encontrado para conferir")
        errors = []
        if synced_vars:
            errors.append(f"{source}: tokens divergentes: {', '.join(dict.fromkeys(synced_vars))}")
        if args.shell:
            shell_markdown = args.shell.read_text(encoding="utf-8")
            _, shell_drift = sync_markdown_token_tables(shell_markdown, tokens_light, tokens_dark)
            shell_drift += check_inline_token_values(shell_markdown, tokens_light, tokens_dark)
            if shell_drift:
                errors.append(f"{args.shell}: tokens divergentes: {', '.join(dict.fromkeys(shell_drift))}")
        if args.compare_css:
            compiled = Path(args.tokens).read_bytes()
            for copy in args.compare_css:
                if copy.read_bytes() != compiled:
                    errors.append(f"{copy}: CSS diverge de {args.tokens}")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            sys.exit(1)
        print("Referências de tokens e cópias CSS informadas conferidas.")
        return
    if synced_vars:
        source.write_text(text_synced, encoding="utf-8")
        text = text_synced
        print(f"[sync] {len(synced_vars)} token(s) sincronizados em {source.name} a partir de tokens.css: {', '.join(synced_vars[:8])}")
    golden_paths: list[tuple[str, Path]] = []
    if args.golden_desktop:
        golden_paths.append(("Tela-Mae Desktop", Path(args.golden_desktop)))
    if args.golden_mobile:
        golden_paths.append(("Tela-Mae Mobile", Path(args.golden_mobile)))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "DESIGN-BIBLE.html"
    pdf_path = out_dir / "DESIGN-BIBLE.pdf"
    html_path.write_text(
        build_html(text, title, tokens_light=tokens_light, tokens_dark=tokens_dark, golden_paths=golden_paths, manifest=manifest),
        encoding="utf-8",
    )
    print(f"Papel Visual HTML: {html_path}")

    browser = find_browser()
    if not browser:
        print("Chromium nao encontrado. O HTML esta pronto para imprimir em PDF, sem limite de paginas.", file=sys.stderr)
        sys.exit(0)
    try:
        write_pdf(browser, html_path, pdf_path)
    except subprocess.CalledProcessError as exc:
        print(f"Falha ao gerar PDF: {exc.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"PDF Visual sem corte: {pdf_path}")


if __name__ == "__main__":
    main()
