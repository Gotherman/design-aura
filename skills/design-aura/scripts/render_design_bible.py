#!/usr/bin/env python3
"""Gera a Biblia Visual de Design em HTML e PDF sem corte (Design Aura v2.0).

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
                "z0": pick_token(m, ["--surface-z0", "--bg-well", "--well", "--bg-recess"], "#081018"),
                "z1": pick_token(m, ["--surface-z1", "--bg-canvas", "--bg", "--canvas"], "#0E1724"),
                "z2": pick_token(m, ["--surface-z2", "--bg-card", "--card", "--surface"], "#152336"),
                "z3": pick_token(m, ["--surface-z3", "--bg-elevated", "--popover"], "#1D3048"),
                "z4": pick_token(m, ["--surface-z4", "--bg-modal", "--drawer"], "#243A56"),
                "border": pick_token(m, ["--border-card", "--border", "--border-subtle"], "#2B3F57"),
                "borderStrong": pick_token(m, ["--border-strong", "--border-focus"], "#456384"),
                "textStrong": pick_token(m, ["--text-strong", "--ink-strong", "--fg-strong", "--text"], "#F3F6FA"),
                "textBody": pick_token(m, ["--text-body", "--ink", "--fg", "--text-primary"], "#D3DEEC"),
                "textMuted": pick_token(m, ["--text-muted", "--ink-muted", "--muted"], "#95A8BE"),
                "primary": pick_token(m, ["--brand-primary", "--primary", "--brand-navy"], "#3B82F6"),
                "accent": pick_token(m, ["--brand-accent", "--accent", "--cta", "--accent-deep"], "#FF6B38"),
                "onAccent": pick_token(m, ["--on-accent", "--text-on-accent"], "#101822"),
                "success": pick_token(m, ["--semantic-success", "--success", "--ok"], "#34D399"),
                "warning": pick_token(m, ["--semantic-warning", "--warning", "--warn"], "#FBBF24"),
                "danger": pick_token(m, ["--semantic-danger", "--danger", "--error"], "#F87171"),
                "info": pick_token(m, ["--semantic-info", "--info"], "#60A5FA"),
                "fontDisplay": pick_token(m, ["--font-display", "--font-heading"], "'Plus Jakarta Sans', system-ui, sans-serif"),
                "fontUi": pick_token(m, ["--font-ui", "--font-sans", "--font-body"], "'Inter', system-ui, sans-serif"),
                "fontMono": pick_token(m, ["--font-mono"], "'JetBrains Mono', ui-monospace, monospace"),
            }
        return {
            "z0": pick_token(m, ["--surface-z0", "--bg-well", "--well", "--bg-recess"], "#E2E8F0"),
            "z1": pick_token(m, ["--surface-z1", "--bg-canvas", "--bg", "--canvas"], "#F1F5F9"),
            "z2": pick_token(m, ["--surface-z2", "--bg-card", "--card", "--surface"], "#FFFFFF"),
            "z3": pick_token(m, ["--surface-z3", "--bg-elevated", "--popover"], "#FFFFFF"),
            "z4": pick_token(m, ["--surface-z4", "--bg-modal", "--drawer"], "#FFFFFF"),
            "border": pick_token(m, ["--border-card", "--border", "--border-subtle"], "#CBD5E1"),
            "borderStrong": pick_token(m, ["--border-strong", "--border-focus"], "#94A3B8"),
            "textStrong": pick_token(m, ["--text-strong", "--ink-strong", "--fg-strong", "--text"], "#0F172A"),
            "textBody": pick_token(m, ["--text-body", "--ink", "--fg", "--text-primary"], "#334155"),
            "textMuted": pick_token(m, ["--text-muted", "--ink-muted", "--muted"], "#64748B"),
            "primary": pick_token(m, ["--brand-primary", "--primary", "--brand-navy"], "#0F2942"),
            "accent": pick_token(m, ["--brand-accent", "--accent", "--cta", "--accent-deep"], "#EA580C"),
            "onAccent": pick_token(m, ["--on-accent", "--text-on-accent"], "#FFFFFF"),
            "success": pick_token(m, ["--semantic-success", "--success", "--ok"], "#059669"),
            "warning": pick_token(m, ["--semantic-warning", "--warning", "--warn"], "#D97706"),
            "danger": pick_token(m, ["--semantic-danger", "--danger", "--error"], "#DC2626"),
            "info": pick_token(m, ["--semantic-info", "--info"], "#2563EB"),
            "fontDisplay": pick_token(m, ["--font-display", "--font-heading"], "'Plus Jakarta Sans', system-ui, sans-serif"),
            "fontUi": pick_token(m, ["--font-ui", "--font-sans", "--font-body"], "'Inter', system-ui, sans-serif"),
            "fontMono": pick_token(m, ["--font-mono"], "'JetBrains Mono', ui-monospace, monospace"),
        }

    lp = theme_palette(light, False)
    dp = theme_palette(dark, True)

    def render_theme_card(label: str, p: dict[str, str]) -> str:
        e = html.escape
        swatches = [
            ("Z0 Poço", p["z0"]),
            ("Z1 Canvas", p["z1"]),
            ("Z2 Card", p["z2"]),
            ("Z3 Float", p["z3"]),
            ("Primary", p["primary"]),
            ("Accent", p["accent"]),
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
          <div class="sp-panel-head" style="border-bottom:1px solid {e(p['border'])}">
            <strong style="color:{e(p['textStrong'])};font-family:{e(p['fontDisplay'])}">{e(label)}</strong>
            <span class="sp-mono" style="color:{e(p['textMuted'])};font-family:{e(p['fontMono'])}">{e(p['z1'])} → {e(p['z2'])}</span>
          </div>
          <div class="sp-swatch-grid">{sw_html}</div>
          <div class="sp-card" style="background:{e(p['z2'])};border:1.25px solid {e(p['border'])};color:{e(p['textBody'])}">
            <div class="sp-card-top">
              <div>
                <div class="sp-title" style="color:{e(p['textStrong'])};font-family:{e(p['fontDisplay'])}">Superfície Z2 &amp; Hierarquia Real</div>
                <div class="sp-sub" style="color:{e(p['textMuted'])}">Display: {e(p['fontDisplay'].split(',')[0])} · UI: {e(p['fontUi'].split(',')[0])}</div>
              </div>
              <div class="sp-kpi" style="color:{e(p['textStrong'])};font-family:{e(p['fontMono'])}">R$ 48.920,00</div>
            </div>
            <div class="sp-badges">
              <span class="sp-pill" style="background:{e(p['success'])}22;color:{e(p['success'])};border:1px solid {e(p['success'])}55">Em dia</span>
              <span class="sp-pill" style="background:{e(p['warning'])}22;color:{e(p['warning'])};border:1px solid {e(p['warning'])}55">Vence hoje</span>
              <span class="sp-pill" style="background:{e(p['danger'])}22;color:{e(p['danger'])};border:1px solid {e(p['danger'])}55">Crítico</span>
              <span class="sp-pill" style="background:{e(p['info'])}22;color:{e(p['info'])};border:1px solid {e(p['info'])}55">Info</span>
            </div>
            <div class="sp-actions">
              <span class="sp-btn" style="background:{e(p['accent'])};color:{e(p['onAccent'])};border:1px solid {e(p['accent'])}">Ação Primária</span>
              <span class="sp-btn" style="background:{e(p['z0'])};color:{e(p['textStrong'])};border:1px solid {e(p['borderStrong'])}">Secundária</span>
              <span class="sp-input" style="background:{e(p['z0'])};color:{e(p['textMuted'])};border:1px solid {e(p['border'])}">Buscar rotina · Ctrl+K</span>
            </div>
          </div>
        </div>
        """

    return f"""
    <section class="specimen-sheet" aria-label="Prancha Visual de Tokens">
      <div class="specimen-head">
        <span class="specimen-kicker">Espécime Visual Renderizado · {html.escape(title)}</span>
        <p>Esta prancha renderiza diretamente as cores, planos Z0–Z4, tipografia, badges semânticos e botões definidos em <code>tokens.css</code> para validação visual imediata antes de construir as telas.</p>
      </div>
      <div class="specimen-grid">
        {render_theme_card("Dark Mode (Luminosidade Z0 → Z4)", dp)}
        {render_theme_card("Light Mode (Canvas Aterrado Z0 → Z4)", lp)}
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
.sp-badges { display: flex; flex-wrap: wrap; gap: 1.5mm; }
.sp-pill { font-size: 7.5pt; font-weight: 700; padding: 0.6mm 1.8mm; border-radius: 999px; }
.sp-actions { display: flex; flex-wrap: wrap; gap: 1.5mm; align-items: center; }
.sp-btn { font-size: 8pt; font-weight: 700; padding: 1.2mm 2.6mm; border-radius: 1.4mm; display: inline-block; }
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
    """Sincroniza hexes em tabelas Markdown (ex.: Secao 8.1) contra tokens.css atual."""
    if not tokens_light and not tokens_dark:
        return md, []
    hex_re = re.compile(r"#[0-9A-Fa-f]{6}\b")
    var_re = re.compile(r"--([a-zA-Z0-9_-]+)")
    synced_vars: list[str] = []
    new_lines: list[str] = []
    for line in md.splitlines():
        if line.strip().startswith("|") and "--" in line:
            cells = line.split("|")
            # Detecta o primeiro --token-name na linha da tabela
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
                # Quando a linha tem 2 hexes (Dark | Light ou Light | Dark) e diverge de tokens.css
                if len(hexes) >= 2 and d_val.startswith("#") and l_val.startswith("#"):
                    h0, h1 = hexes[0].upper(), hexes[1].upper()
                    du, lu = d_val.upper(), l_val.upper()
                    if {h0, h1} != {du, lu}:
                        # Preserva ordem Dark vs Light conforme a luminancia do primeiro hex
                        first_is_dark = int(h0[1:3], 16) + int(h0[3:5], 16) + int(h0[5:7], 16) < 380
                        rep0 = du if first_is_dark else lu
                        rep1 = lu if first_is_dark else du
                        updated = hex_re.sub("__HEX_SLOT__", line, count=2)
                        updated = updated.replace("__HEX_SLOT__", rep0, 1).replace("__HEX_SLOT__", rep1, 1)
                        if updated != line:
                            line = updated
                            synced_vars.append(token_name)
        new_lines.append(line)
    return "\n".join(new_lines) + ("\n" if md.endswith("\n") else ""), synced_vars


def build_html(
    md: str,
    title: str,
    tokens_light: dict[str, str] | None = None,
    tokens_dark: dict[str, str] | None = None,
    golden_paths: list[tuple[str, Path]] | None = None,
) -> str:
    md_synced, _ = sync_markdown_token_tables(md, tokens_light or {}, tokens_dark or {})
    body = markdown_to_body(md_synced)
    specimen = build_specimen_board(tokens_light or {}, tokens_dark or {}, title)
    golden = build_golden_gallery(golden_paths or [])
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
    args = parser.parse_args()

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
    text_synced, synced_vars = sync_markdown_token_tables(text, tokens_light, tokens_dark)
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
        build_html(text, title, tokens_light=tokens_light, tokens_dark=tokens_dark, golden_paths=golden_paths),
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
