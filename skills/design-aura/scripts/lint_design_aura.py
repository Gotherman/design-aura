#!/usr/bin/env python3
"""Linter deterministico dos 10 Blocos de Leis Inegociaveis da skill Design Aura.

Analisa arquivos ou diretorios (.html, .css, .scss, .js, .jsx, .ts, .tsx,
.vue, .svelte, .swift, .kt, .dart) sem modificar arquivos.
"""
import argparse
import bisect
import json
import os
import re
import sys
from pathlib import Path

UI_EXTS = {
    ".html", ".htm", ".css", ".scss", ".js", ".jsx",
    ".ts", ".tsx", ".vue", ".svelte", ".swift", ".kt", ".dart",
}
CSS_EXTS = {".css", ".scss"}
MARKUP_EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".svelte-kit",
    ".nuxt", "coverage", ".venv", "venv", "__pycache__", "audit-shots",
}
SKIP_FILES = {"package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}
MAX_BYTES = 1_000_000


def blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group(0))


COMMENT_PATTERNS = {
    "jsx": re.compile(r"\{/\*.*?\*/\}", re.S),
    "html": re.compile(r"<!--.*?-->", re.S),
    "block": re.compile(r"/\*.*?\*/", re.S),
    "line": re.compile(r"^[ \t]*//.*$", re.M),
    "trailing": re.compile(r"(?<=[;,{}()\[\]])[ \t]*//(?!/)[^<\n]*$", re.M),
}


def strip_comments(text: str, ext: str) -> str:
    keys = ("block", "line") if ext in CSS_EXTS else ("jsx", "html", "block", "line", "trailing")
    for k in keys:
        text = COMMENT_PATTERNS[k].sub(blank, text)
    return text


def line_index_map(text: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def pos_to_line(starts: list[int], pos: int) -> int:
    return bisect.bisect_right(starts, pos)


def snippet_at(raw_text: str, pos: int) -> str:
    ls = raw_text.rfind("\n", 0, pos) + 1
    le = raw_text.find("\n", pos)
    if le == -1:
        le = len(raw_text)
    s = raw_text[ls:le].strip()
    return (s[:117] + "...") if len(s) > 120 else s


RULES = [
    {
        "id": "DA-B1-01",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"(?:from|via|to)-(?:purple|indigo|violet|fuchsia)-(?:[3-9]00)"
            r"|linear-gradient\([^;)]*(?:#a855f7|#8b5cf6|#7c3aed|#6366f1|#4f46e5|#ec4899|purple|violet|indigo|magenta)",
            re.I,
        ),
        "message": "Gradiente roxo/indigo/neon generico sem justificativa da marca (Bloco 1)",
        "fix": "Use paleta aterrada ou cores reais do dominio definidas na DESIGN-BIBLE.md",
    },
    {
        "id": "DA-B1-02",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"shadow-\[0_0_(?:1[5-9]|[2-9]\d)px"
            r"|box-shadow\s*:[^;]*\b0(?:px)?\s+0(?:px)?\s+(?:1[5-9]|[2-9]\d)px\b[^;]*(?:rgba?\(|#)",
            re.I,
        ),
        "message": "Halo de glow colorido com offset zero (decoracao gratuita, Bloco 1)",
        "fix": "Use elevacao fisica com offset e blur suave no Light Mode ou luminosidade no Dark Mode",
    },
    {
        "id": "DA-B1-03",
        "severity": "BLOCK",
        "exts": MARKUP_EXTS | {".swift", ".kt", ".dart"},
        "pattern": re.compile(r"[✨🚀⚡🛡️🔥💡🎯]"),
        "message": "Emoji cliche usado como icone de UI (Bloco 1)",
        "fix": "Substitua por icone SVG de uma unica familia consistente (Phosphor/Lucide/SF Symbols)",
    },
    {
        "id": "DA-B1-05",
        "severity": "BLOCK",
        "exts": MARKUP_EXTS,
        "pattern": re.compile(
            r'class(?:Name)?="[^"]*\b(?:eyebrow|kicker)\b[^"]*"'
            r"|>\s*0[1-9]\s*(?://|·|—)\s*[A-ZÀ-Úa-zà-ú]",
        ),
        "message": "Eyebrow decorativo ou numeracao ornamental '01 //' sobre titulo (Bloco 1)",
        "fix": "Remova o eyebrow/numero ornamental e deixe o titulo principal conduzir a hierarquia",
    },
    {
        "id": "DA-B1-06A",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(r"\bbg-clip-text\b|(?:-webkit-)?background-clip\s*:\s*text\b", re.I),
        "message": "Gradiente em texto (bg-clip-text) proibido (Bloco 1)",
        "fix": "Use peso, tamanho e cor solida de alto contraste para enfase tipografica",
    },
    {
        "id": "DA-B1-06B",
        "severity": "BLOCK",
        "exts": MARKUP_EXTS,
        "pattern": re.compile(r"\bborder-l-[248]\b[^>]*\brounded-|\brounded-[^>]*\bborder-l-[248]\b"),
        "message": "Barrinha colorida em um lado de caixa arredondada (Bloco 1)",
        "fix": "Substitua por borda completa sutil, tint leve de fundo ou icone/badge semantico",
    },
    {
        "id": "DA-B1-06C",
        "severity": "HIGH",
        "exts": MARKUP_EXTS,
        "pattern": re.compile(
            r"\banimate-pulse\b(?![^<]{0,80}(?:skeleton|loading|placeholder))"
            r"|<(?:span|div|small)[^>]*>\s*(?:LIVE|AO VIVO|NEW|AI)\s*</(?:span|div|small)>",
            re.I,
        ),
        "message": "Badge LIVE/NEW/AI ou pulso decorativo sem ligacao a estado real (Bloco 1)",
        "fix": "Vincule a um estado real observado ou remova a pílula decorativa",
    },
    {
        "id": "DA-B2-03",
        "severity": "HIGH",
        "exts": MARKUP_EXTS,
        "pattern": re.compile(r"<(?:p|ul|ol)[^>]*\btext-center\b[^>]*>[^<]{140,}", re.S),
        "message": "Bloco longo de texto ou lista centralizado prejudicando escaneabilidade (Bloco 2)",
        "fix": "Alinhe paragrafos longos e listas a esquerda (text-left)",
    },
    {
        "id": "DA-B3-02",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"(?:bg-black[^\"'>]{0,40}text-white|bg-white[^\"'>]{0,40}text-black)"
            r"|(?:color\s*:\s*#fff(?:fff)?\b[^}]{0,80}background(?:-color)?\s*:\s*#000(?:000)?\b)"
            r"|(?:background(?:-color)?\s*:\s*#000(?:000)?\b[^}]{0,80}color\s*:\s*#fff(?:fff)?\b)",
            re.I | re.S,
        ),
        "message": "Pareamento cru #000000 com #FFFFFF sem elevacao controlada de superficie (Bloco 3)",
        "fix": "Use superfícies aterradas/ardosia (Z1/Z2) e texto de alto contraste calibrado (ex.: #101822 / #F3F6FA)",
    },
    {
        "id": "DA-B3-03",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(r"font-size\s*:\s*(?:[6-9]|10)px\b|\btext-\[(?:[6-9]|10)px\]"),
        "message": "Tamanho de fonte ilegivel abaixo de 11px em interface (Bloco 3)",
        "fix": "Eleve para >= 12px em rotulos tecnicos/mono e >= 14px em corpo de leitura",
    },
    {
        "id": "DA-B4-01",
        "severity": "HIGH",
        "exts": UI_EXTS,
        "pattern": re.compile(r"\bfont-(?:extrabold|black)\b|font-weight\s*:\s*(?:800|900)\b"),
        "message": "Peso tipografico excessivo (800/900) fora de display intencional (Bloco 4)",
        "fix": "Use pesos 500, 600 ou 700 deixando escala e cor criarem a hierarquia",
    },
    {
        "id": "DA-B5-01",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(r"\b(?:Lorem\s+ipsum|dolor\s+sit\s+amet|John\s+Doe|Jane\s+Doe|Acme\s+Corp|example\.com)\b", re.I),
        "message": "Texto placeholder generico (Lorem ipsum / John Doe / Acme) em entrega (Bloco 5)",
        "fix": "Substitua por dados ficticios verossimeis e consistentes do dominio real",
    },
    {
        "id": "DA-B5-02",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"\b(?:Transforme\s+seu\s+neg[oó]cio|Eleve\s+sua\s+experi[eê]ncia|Solu[cç][aã]o\s+definitiva"
            r"|Potencializado\s+por\s+IA|Revolucione\s+sua\s+rotina|Desbloqueie\s+seu\s+potencial"
            r"|Unlock\s+your\s+potential|Elevate\s+your\s+workflow|All-in-one\s+platform)\b",
            re.I,
        ),
        "message": "Microcopy cliche de template de IA (Bloco 5)",
        "fix": "Escreva com verbos concretos e resultado mensuravel ligado ao produto",
    },
    {
        "id": "DA-B5-03",
        "severity": "HIGH",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"\b(?:Clique\s+no\s+bot[aã]o\s+abaixo|Click\s+the\s+button\s+below"
            r"|Este\s+gr[aá]fico\s+mostra|This\s+chart\s+shows|\(powered\s+by\s+AI\)|\(atualiza\s+em\s+tempo\s+real\))",
            re.I,
        ),
        "message": "Botsplaining ou nota tecnica vazada na copy visivel (Bloco 5)",
        "fix": "Remova a frase redundante; deixe o controle ou titulo comunicar o dado diretamente",
    },
    {
        "id": "DA-B2-08A",
        "severity": "BLOCK",
        "exts": MARKUP_EXTS,
        "pattern": re.compile(
            r"(?:n[aã]o\s+est[aã]o\s+nesta\s+amostra|semente\s+do\s+funil|sem\s+classe\s+card"
            r"|dados\s+de\s+exemplo\s+apenas|placeholder\s+de\s+tela|em\s+constru[cç][aã]o\s+aqui)",
            re.I,
        ),
        "message": "Copy de dev/desculpa de stub vazada na interface (Bloco 2 / Bloco 5)",
        "fix": "Substitua por dados completos e realistas do dominio, sem desculpas de amostra ou jargao de seed",
    },
    {
        "id": "DA-B6-02A",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(r"\btransition-all\b|transition\s*:\s*all\b", re.I),
        "message": "Uso de transition-all / transition: all proibido (Bloco 6)",
        "fix": "Especifique as propriedades exatas (ex.: transition: transform 150ms ease-out, background-color 150ms ease-out)",
    },
    {
        "id": "DA-B6-02B",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(r"\bhover:scale-(?:105|110)\b|\banimate-bounce\b"),
        "message": "Microinteracao gratuita exagerada (hover:scale-105 / animate-bounce) (Bloco 6)",
        "fix": "Use elevacao sutil de cor/borda no hover e press scale 0.97 em botoes",
    },
    {
        "id": "DA-B6-02C",
        "severity": "MEDIUM",
        "exts": UI_EXTS,
        "pattern": re.compile(r"\bduration-(?:500|700|1000)\b|transition(?:-duration)?\s*:\s*(?:[4-9]\d{2}|[1-9]\d{3})ms\b"),
        "message": "Transicao lenta acima de 300ms em interacao simples (Bloco 6)",
        "fix": "Reduza para 120ms-240ms para manter resposta tatil imediata",
    },
    {
        "id": "DA-B7-02",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"(?:margin|padding|gap|row-gap|column-gap)(?:-[a-z]+)?\s*:\s*(?:7|9|11|13|15|17|19|21|23)px\b"
            r"|\b(?:p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap)-\[(?:7|9|11|13|15|17|19|21|23)px\]",
        ),
        "message": "Magic number de espacamento fora da escala 4px/8px (Bloco 7)",
        "fix": "Arredonde para o passo mais proximo de 4, 8, 12, 16, 20, 24, 32px (ou 2/6/10/14px interno de controle)",
    },
    {
        "id": "DA-B7-03",
        "severity": "HIGH",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"(?:\[data-theme=[\"']dark[\"']\]|\.dark\b)[^{]{0,240}\{[^}]*box-shadow\s*:[^;]*rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*(?:0\.[4-9]\d*|1(?:\.0+)?)\s*\)"
            r"|dark:[^\s\"']*shadow-\[[^\]]*rgba\(\s*0\s*,\s*0\s*,\s*0",
            re.I | re.S,
        ),
        "message": "Sombra preta chapada em Dark Mode; elevacao some no fundo escuro (Bloco 7)",
        "fix": "Suba a luminosidade da superficie e use borda/inset claros. Reserve sombra preta fraca so como apoio, nunca como unico plano",
    },
    {
        "id": "DA-B8-03",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(
            r"\b(?:Gr[aá]fico\s+de\s+(?:barras|linhas|pizza)|Bar\s+chart\s+of|Line\s+chart\s+of|Pie\s+chart\s+of"
            r"|Passe\s+o\s+mouse\s+para\s+ver|Hover\s+for\s+details|Cada\s+barra\s+representa)\b",
            re.I,
        ),
        "message": "Titulo nomeando tipo de grafico ou instrucao redundante de leitura (Bloco 8)",
        "fix": "Nomeie a metrica/conclusao real (ex.: 'Receita mensal') e remova instrucoes obvias",
    },
    {
        "id": "DA-B9-02",
        "severity": "BLOCK",
        "exts": UI_EXTS,
        "pattern": re.compile(r"outline\s*:\s*(?:none|0)\b|\boutline-none\b"),
        "message": "Remocao de outline sem indicador :focus-visible garantido (Bloco 9)",
        "fix": "Mantenha :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }",
    },
    {
        "id": "DA-B10-02",
        "severity": "MEDIUM",
        "exts": UI_EXTS,
        "pattern": re.compile(r"(?:min-)?height\s*:\s*100vh\b|\bh-screen\b|\bmin-h-screen\b"),
        "message": "Uso de 100vh rigido sujeito a corte em barras de navegador mobile (Bloco 10)",
        "fix": "Prefira 100dvh / min-h-dvh com env(safe-area-inset-*) quando aplicavel a mobile",
    },
]


def check_structural_rules(raw_text: str, clean_text: str, ext: str, rel_path: str, starts: list[int]) -> list[dict]:
    findings = []

    # DA-B4-02: tabela sem tabular-nums
    if ext in MARKUP_EXTS and "<table" in clean_text.lower() and "tabular-nums" not in clean_text:
        m = re.search(r"<table\b", clean_text, re.I)
        if m:
            findings.append({
                "rule": "DA-B4-02",
                "severity": "HIGH",
                "location": f"{rel_path}:{pos_to_line(starts, m.start())}",
                "evidence": snippet_at(raw_text, m.start()),
                "message": "Tabela detectada sem uso visivel de tabular-nums no arquivo (Bloco 4)",
                "fix": "Aplique font-variant-numeric: tabular-nums (ou .tabular-nums) em colunas numericas",
            })

    # DA-B6-02D: arquivo CSS/HTML com transition/@keyframes sem prefers-reduced-motion
    if ext in CSS_EXTS and ("@keyframes" in clean_text or "animation:" in clean_text) and "prefers-reduced-motion" not in clean_text:
        m = re.search(r"@keyframes|animation\s*:", clean_text)
        if m:
            findings.append({
                "rule": "DA-B6-02D",
                "severity": "HIGH",
                "location": f"{rel_path}:{pos_to_line(starts, m.start())}",
                "evidence": snippet_at(raw_text, m.start()),
                "message": "Animacoes CSS definidas sem media query prefers-reduced-motion (Bloco 6)",
                "fix": "Inclua @media (prefers-reduced-motion: reduce) reduzindo duracoes",
            })

    # DA-B9-01: <input placeholder=...> sem label ou aria-label
    if ext in MARKUP_EXTS:
        for m in re.finditer(r"<input\b([^>]+)>", clean_text, re.I | re.S):
            attrs = m.group(1)
            if re.search(r'\btype\s*=\s*["\'](?:hidden|submit|button|reset|checkbox|radio)["\']', attrs, re.I):
                continue
            if "placeholder=" not in attrs.lower():
                continue
            if re.search(r"\baria-label(?:ledby)?\s*=", attrs, re.I):
                continue
            id_m = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', attrs, re.I)
            has_label = False
            if id_m:
                fid = re.escape(id_m.group(1))
                if re.search(rf'\b(?:for|htmlFor)\s*=\s*["\']{fid}["\']', clean_text):
                    has_label = True
            if not has_label:
                window = clean_text[max(0, m.start() - 220):m.end() + 120]
                if "<label" in window.lower():
                    has_label = True
            if not has_label:
                findings.append({
                    "rule": "DA-B9-01",
                    "severity": "BLOCK",
                    "location": f"{rel_path}:{pos_to_line(starts, m.start())}",
                    "evidence": snippet_at(raw_text, m.start()),
                    "message": "Input com placeholder sem <label> visivel ou aria-label associado (Bloco 9)",
                    "fix": "Adicione <label for=...> visivel (ou aria-label em barras de busca dedicadas)",
                })

    # DA-B10-03: <img> sem alt
    if ext in MARKUP_EXTS:
        for m in re.finditer(r"<img\b([^>]+)>", clean_text, re.I | re.S):
            attrs = m.group(1)
            if not re.search(r"\balt\s*=", attrs, re.I):
                findings.append({
                    "rule": "DA-B10-03",
                    "severity": "BLOCK",
                    "location": f"{rel_path}:{pos_to_line(starts, m.start())}",
                    "evidence": snippet_at(raw_text, m.start()),
                    "message": "Tag <img> sem atributo alt (Bloco 10)",
                    "fix": 'Inclua alt descritivo ou alt="" quando puramente decorativa, mais object-fit: cover',
                })
            else:
                classes = ""
                class_match = re.search(r'\bclass(?:Name)?\s*=\s*["\']([^"\']+)["\']', attrs, re.I)
                if class_match:
                    classes = class_match.group(1)
                looks_media = re.search(r"\b(?:avatar|thumb|photo|media|cover|portrait)\b", classes, re.I)
                has_fit = re.search(r"\bobject-(?:cover|contain|fill)\b|object-fit\s*:", attrs + classes, re.I)
                if looks_media and not has_fit:
                    findings.append({
                        "rule": "DA-B10-04",
                        "severity": "HIGH",
                        "location": f"{rel_path}:{pos_to_line(starts, m.start())}",
                        "evidence": snippet_at(raw_text, m.start()),
                        "message": "Midia de retrato/capa sem object-fit (Bloco 10)",
                        "fix": "Aplique object-cover (ou object-contain quando o recorte distorcer o conteudo) e um fundo de fallback",
                    })

    findings.extend(_nested_surface_findings(clean_text, raw_text, ext, rel_path, starts))
    findings.extend(_motion_findings(clean_text, raw_text, ext, rel_path, starts))
    findings.extend(_craft_floor_findings(clean_text, raw_text, ext, rel_path, starts))
    return findings


def _craft_floor_findings(clean_text: str, raw_text: str, ext: str, rel_path: str, starts: list[int]) -> list[dict]:
    """Checagens estaticas de piso de craft (v2.0): anti-stub, serifa em Operate e textarea cru."""
    findings: list[dict] = []
    lower_name = Path(rel_path).name.lower()
    is_vitrine = lower_name in {"fluxo.html", "preview.html", "index.html", "design-bible.html"}

    # DA-B4-04: fonte serifada editorial em tela operacional ou CSS de sistema
    if not is_vitrine and ext in (MARKUP_EXTS | CSS_EXTS):
        serif_re = re.compile(
            r"(?:Source\s+Serif|Playfair\s+Display|Merriweather|Iowan\s+Old\s+Style|Palatino|Times\s+New\s+Roman|Garamond|Georgia\s*,?\s*serif)",
            re.I,
        )
        m = serif_re.search(clean_text)
        looks_operate = (
            "<table" in clean_text.lower()
            or "sidebar" in clean_text.lower()
            or "shell" in lower_name
            or "tokens" in lower_name
            or "desktop-" in lower_name
            or "mobile-" in lower_name
            or "dashboard" in lower_name
            or "--font-display" in clean_text.lower()
        )
        if m and looks_operate and 'data-allow-serif="true"' not in clean_text:
            findings.append({
                "rule": "DA-B4-04",
                "severity": "HIGH",
                "location": f"{rel_path}:{pos_to_line(starts, m.start())}",
                "evidence": snippet_at(raw_text, m.start()),
                "message": "Fonte serifada editorial detectada em sistema operacional Operate sem autorizacao explicita (Bloco 4)",
                "fix": "Use sans-serif geometrica/neo-grotesca (Plus Jakarta Sans, Inter, Instrument Sans, Geist) ou anote design-aura-allow: DA-B4-04 com motivo aprovado",
            })

    # DA-B2-08B: tabela operacional estatica rasa (apenas 1 ou 2 linhas <tr> em <tbody> sem renderizacao dinamica)
    if not is_vitrine and ext in {".html", ".htm"}:
        for tm in re.finditer(r"<tbody\b[^>]*>(.*?)</tbody>", clean_text, re.I | re.S):
            body_html = tm.group(1)
            row_count = len(re.findall(r"<tr\b", body_html, re.I))
            has_dynamic_fill = bool(re.search(r"(?:innerHTML|insertRow|appendChild|createElement\(['\"]tr['\"]\))", clean_text))
            if 1 <= row_count <= 2 and not has_dynamic_fill:
                findings.append({
                    "rule": "DA-B2-08B",
                    "severity": "HIGH",
                    "location": f"{rel_path}:{pos_to_line(starts, tm.start())}",
                    "evidence": snippet_at(raw_text, tm.start()),
                    "message": f"Tabela operacional rasa com apenas {row_count} linha(s) estatica(s) em <tbody> (Bloco 2)",
                    "fix": "Popule a tabela com pelo menos 5 registros realistas e coerentes do dominio (ou renderize a colecao real via JS)",
                })

    # DA-B9-05: <textarea> cru sem classe do design system em tela HTML
    if not is_vitrine and ext in MARKUP_EXTS:
        for tm in re.finditer(r"<textarea\b([^>]*)>", clean_text, re.I | re.S):
            attrs = tm.group(1)
            if not re.search(r"\bclass(?:Name)?\s*=", attrs, re.I):
                findings.append({
                    "rule": "DA-B9-05",
                    "severity": "MEDIUM",
                    "location": f"{rel_path}:{pos_to_line(starts, tm.start())}",
                    "evidence": snippet_at(raw_text, tm.start()),
                    "message": "Campo <textarea> sem classe/estilizacao propria do design system (Bloco 9)",
                    "fix": "Aplique a classe de campo do design system (borda, padding, radius, resize: vertical e :focus-visible)",
                })

    return findings


_TAG_RE = re.compile(r"<(/?)([A-Za-z][\w:-]*)\b([^>]*)>", re.S)
_CLASS_RE = re.compile(r"""\bclass(?:Name)?\s*=\s*["']([^"']+)["']""", re.I)
_RADIUS_RE = re.compile(r"\b(rounded-(?:none|sm|md|lg|xl|2xl|3xl|full|\[[^\]]+\]))\b")
_PAD_RE = re.compile(r"\b(?:p|px|py|pt|pr|pb|pl)-(?:1|2|3|4|\[(?:4|8|12|16)px\])\b")
_VOID_TAGS = {"img", "input", "br", "hr", "meta", "link", "source", "area", "col", "embed", "wbr"}


def _is_cardish(tag: str, classes: str) -> bool:
    if tag.lower() == "card":
        return True
    for token in classes.split():
        name = token.lower()
        if name in {"card", "da-card", "surface-card"} or name.endswith("-card") or name.startswith("card-") or "-card-" in name:
            return True
    return False


def _nested_surface_findings(clean_text: str, raw_text: str, ext: str, rel_path: str, starts: list[int]) -> list[dict]:
    if ext not in MARKUP_EXTS:
        return []
    findings = []
    stack: list[tuple[str, bool, str | None, bool, int]] = []
    for match in _TAG_RE.finditer(clean_text):
        closing, tag, attrs = match.group(1), match.group(2), match.group(3)
        self_close = tag.lower() in _VOID_TAGS or attrs.rstrip().endswith("/")
        class_match = _CLASS_RE.search(attrs)
        classes = class_match.group(1) if class_match else ""
        if closing == "/":
            wanted = tag.lower()
            while stack:
                top = stack.pop()
                if top[0] == wanted:
                    break
            continue
        cardish = _is_cardish(tag, classes)
        radius = None
        radii = _RADIUS_RE.findall(classes)
        if radii:
            radius = radii[-1]
        tight_pad = bool(_PAD_RE.search(classes))
        if cardish and any(item[1] for item in stack):
            findings.append({
                "rule": "DA-B2-01",
                "severity": "BLOCK",
                "location": f"{rel_path}:{pos_to_line(starts, match.start())}",
                "evidence": snippet_at(raw_text, match.start()),
                "message": "Card dentro de card (Bloco 2)",
                "fix": "Achate a hierarquia: superficie externa unica e conteudo interno sem segunda caixa",
            })
        if radius:
            for item in reversed(stack):
                if item[2] == radius and item[3]:
                    findings.append({
                        "rule": "DA-B7-01",
                        "severity": "HIGH",
                        "location": f"{rel_path}:{pos_to_line(starts, match.start())}",
                        "evidence": snippet_at(raw_text, match.start()),
                        "message": f"Mesmo raio {radius} aninhado com padding curto; cantos beliscados (Bloco 7)",
                        "fix": "Raio interno = raio externo - padding. Ex.: externo 20px, padding 8px, interno 12px",
                    })
                    break
        if not self_close:
            stack.append((tag.lower(), cardish, radius, tight_pad, match.start()))
    return findings


def _motion_findings(clean_text: str, raw_text: str, ext: str, rel_path: str, starts: list[int]) -> list[dict]:
    if ext not in UI_EXTS:
        return []
    findings = []
    for match in re.finditer(r"animation\s*:[^;{}]*\binfinite\b", clean_text, re.I):
        window = clean_text[max(0, match.start() - 180):match.end() + 80]
        if re.search(r"skeleton|spinner|progress|loading|indeterminate", window, re.I):
            continue
        findings.append({
            "rule": "DA-B6-04",
            "severity": "HIGH",
            "location": f"{rel_path}:{pos_to_line(starts, match.start())}",
            "evidence": snippet_at(raw_text, match.start()),
            "message": "Animacao infinita sem papel de espera (Bloco 6)",
            "fix": "Reserve loop para skeleton, spinner ou progresso real. O resto entra, comunica a mudanca e para",
        })
    return findings


_ALLOW_RE = re.compile(r"design-aura-allow:\s*(DA-[A-Z0-9-]+)\s+(\S(?:.*\S)?)", re.I)


def _line_window(raw_text: str, pos: int) -> str:
    line_start = raw_text.rfind("\n", 0, pos) + 1
    prev = raw_text.rfind("\n", 0, max(0, line_start - 1)) + 1
    line_end = raw_text.find("\n", pos)
    if line_end == -1:
        line_end = len(raw_text)
    return raw_text[prev:line_end]


def _allowed(raw_text: str, pos: int, rule_id: str) -> bool:
    window = _line_window(raw_text, pos)
    for match in _ALLOW_RE.finditer(window):
        if match.group(1).upper() != rule_id.upper():
            continue
        reason = match.group(2).strip()
        if len(reason) >= 8:
            return True
    return False


def scan_file(path: Path, root: Path) -> list[dict]:
    ext = path.suffix.lower()
    if ext not in UI_EXTS or path.name in SKIP_FILES:
        return []
    try:
        if path.stat().st_size > MAX_BYTES:
            return []
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    clean_text = strip_comments(raw_text, ext)
    starts = line_index_map(raw_text)
    try:
        rel_path = str(path.relative_to(root))
    except ValueError:
        rel_path = str(path)

    findings = []
    for rule in RULES:
        if ext not in rule["exts"]:
            continue
        for m in rule["pattern"].finditer(clean_text):
            # Excecao para DA-B9-02 quando :focus-visible esta explicitamente definido logo abaixo ou no arquivo
            if rule["id"] == "DA-B9-02" and "focus-visible" in clean_text[m.start():m.start() + 300]:
                continue
            if _allowed(raw_text, m.start(), rule["id"]):
                continue
            findings.append({
                "rule": rule["id"],
                "severity": rule["severity"],
                "location": f"{rel_path}:{pos_to_line(starts, m.start())}",
                "evidence": snippet_at(raw_text, m.start()),
                "message": rule["message"],
                "fix": rule["fix"],
            })

    findings.extend(check_structural_rules(raw_text, clean_text, ext, rel_path, starts))
    findings = [f for f in findings if not _allowed(raw_text, _pos_from_location(raw_text, f["location"]), f["rule"])]
    return findings


def _pos_from_location(raw_text: str, location: str) -> int:
    try:
        line_no = int(location.rsplit(":", 1)[-1])
    except ValueError:
        return 0
    starts = line_index_map(raw_text)
    idx = max(0, min(len(starts) - 1, line_no - 1))
    return starts[idx]


def collect_files(targets: list[str]) -> tuple[list[Path], Path]:
    files: list[Path] = []
    first_root = Path(targets[0]).resolve()
    root = first_root if first_root.is_dir() else first_root.parent
    for t in targets:
        p = Path(t).resolve()
        if not p.exists():
            continue
        if p.is_file():
            files.append(p)
        else:
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for fn in sorted(filenames):
                    files.append(Path(dirpath) / fn)
    return files, root


def format_markdown(findings: list[dict], scanned_count: int) -> str:
    blocks = sum(1 for f in findings if f["severity"] == "BLOCK")
    highs = sum(1 for f in findings if f["severity"] == "HIGH")
    meds = sum(1 for f in findings if f["severity"] == "MEDIUM")
    lines = [
        "# Auditoria Estática Design Aura (10 Blocos)",
        f"- **Arquivos inspecionados:** {scanned_count} · **BLOCK:** {blocks} · **HIGH:** {highs} · **MEDIUM:** {meds}",
        "",
    ]
    if not findings:
        lines.append("Nenhuma violacao detectada pelos portoes estaticos dos 10 Blocos.")
        return "\n".join(lines)

    lines.extend([
        "| Severity | Rule | Location | Evidence | Fix |",
        "|---|---|---|---|---|",
    ])
    for f in findings:
        ev = f["evidence"].replace("|", "\\|").replace("`", "'")
        lines.append(f"| **{f['severity']}** | `{f['rule']}` | `{f['location']}` | `{ev}` | {f['fix']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Linter dos 10 Blocos de Leis Inegociaveis (Design Aura).")
    parser.add_argument("targets", nargs="+", help="Arquivos ou pastas a inspecionar")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"], help="Formato da saida")
    parser.add_argument("--strict", action="store_true", help="Sai com codigo 1 se houver BLOCK")
    parser.add_argument("--max-block", type=int, default=0, help="Numero maximo tolerado de BLOCK no modo --strict")
    args = parser.parse_args()

    files, root = collect_files(args.targets)
    all_findings: list[dict] = []
    scanned = 0
    for f in files:
        if f.suffix.lower() in UI_EXTS and f.name not in SKIP_FILES:
            scanned += 1
            all_findings.extend(scan_file(f, root))

    sev_rank = {"BLOCK": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_findings.sort(key=lambda x: (sev_rank.get(x["severity"], 9), x["location"], x["rule"]))

    if args.format == "json":
        print(json.dumps({"scanned": scanned, "findings": all_findings}, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(all_findings, scanned))

    blocks = sum(1 for f in all_findings if f["severity"] == "BLOCK")
    if args.strict and blocks > args.max_block:
        sys.exit(1)


if __name__ == "__main__":
    main()
