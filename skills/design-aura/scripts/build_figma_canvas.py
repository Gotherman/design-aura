#!/usr/bin/env python3
"""Gerador da Vitrine Interativa Estilo Figma da skill Design Aura.

Le screen-manifest.json (+ opcional --tokens tokens.css) e gera:
  - fluxo.html   (Canvas Infinito Estilo Figma com pan/zoom, setas Bezier, iframes vivos e minimapa)
  - preview.html (Player Guiado de Uso Real por jornada/persona)
  - index.html   (Galeria de Telas com busca Cmd+K / Ctrl+K)
"""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

BASE_STYLES = """
:root {
  --da-bg-dark: __BG_DARK__;
  --da-card-dark: __CARD_DARK__;
  --da-well-dark: __WELL_DARK__;
  --da-border-dark: __BORDER_DARK__;
  --da-border-strong-dark: __BORDER_STRONG_DARK__;
  --da-text-strong-dark: __TEXT_STRONG_DARK__;
  --da-text-body-dark: __TEXT_BODY_DARK__;
  --da-text-muted-dark: __TEXT_MUTED_DARK__;

  --da-bg-light: __BG_LIGHT__;
  --da-card-light: __CARD_LIGHT__;
  --da-well-light: __WELL_LIGHT__;
  --da-border-light: __BORDER_LIGHT__;
  --da-border-strong-light: __BORDER_STRONG_LIGHT__;
  --da-text-strong-light: __TEXT_STRONG_LIGHT__;
  --da-text-body-light: __TEXT_BODY_LIGHT__;
  --da-text-muted-light: __TEXT_MUTED_LIGHT__;

  --da-navy: __BRAND_NAVY__;
  --da-accent-dark: __BRAND_ACCENT_DARK__;
  --da-accent-light: __BRAND_ACCENT_LIGHT__;
  --da-accent: __BRAND_ACCENT_DARK__;
  --da-accent-deep: __BRAND_ACCENT_DEEP__;
  --da-on-accent: #FFFFFF;

  --da-font-display: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --da-font-ui: 'Instrument Sans', system-ui, -apple-system, sans-serif;
  --da-font-mono: 'JetBrains Mono', ui-monospace, monospace;
}

html[data-theme="dark"] {
  color-scheme: dark;
  --surface-z0: var(--da-well-dark);
  --surface-z1: var(--da-bg-dark);
  --surface-z2: var(--da-card-dark);
  --surface-glass: rgba(14, 19, 29, 0.92);
  --border-card: var(--da-border-dark);
  --border-strong: var(--da-border-strong-dark);
  --text-strong: var(--da-text-strong-dark);
  --text-body: var(--da-text-body-dark);
  --text-muted: var(--da-text-muted-dark);
  --da-accent: var(--da-accent-dark);
  --da-accent-text: var(--da-accent-dark);
  --da-mini-vp-border: #6EB5FF;
  --da-mini-vp-bg: rgba(110, 181, 255, 0.16);
  --shadow-z1: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 4px 12px rgba(0, 0, 0, 0.25);
  --shadow-z2: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 10px 24px rgba(0, 0, 0, 0.35);
}

html[data-theme="light"] {
  color-scheme: light;
  --surface-z0: var(--da-well-light);
  --surface-z1: var(--da-bg-light);
  --surface-z2: var(--da-card-light);
  --surface-glass: rgba(248, 251, 255, 0.95);
  --border-card: var(--da-border-light);
  --border-strong: var(--da-border-strong-light);
  --text-strong: var(--da-text-strong-light);
  --text-body: var(--da-text-body-light);
  --text-muted: var(--da-text-muted-light);
  --da-accent: var(--da-accent-light);
  --da-accent-text: var(--da-accent-light);
  --da-mini-vp-border: var(--da-navy);
  --da-mini-vp-bg: rgba(20, 66, 122, 0.14);
  --shadow-z1: 0 0 0 1px rgba(14, 41, 75, 0.08), 0 1px 2px -1px rgba(14, 41, 75, 0.08), 0 4px 10px -2px rgba(14, 41, 75, 0.07);
  --shadow-z2: 0 0 0 1px rgba(14, 41, 75, 0.12), 0 4px 12px -2px rgba(14, 41, 75, 0.11), 0 12px 24px -6px rgba(14, 41, 75, 0.09);
}

* { box-sizing: border-box; scrollbar-width: thin; scrollbar-color: var(--border-strong) var(--surface-z0); }
html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-family: var(--da-font-ui);
  background: var(--surface-z1);
  color: var(--text-body);
}
body { margin: 0; font-size: 14px; line-height: 1.5; background: var(--surface-z1); color: var(--text-body); }
::selection { background: var(--da-accent); color: var(--da-on-accent); }
input, textarea, select { caret-color: var(--da-accent); }
:focus-visible { outline: 2px solid var(--da-accent); outline-offset: 2px; }
a { color: inherit; text-underline-offset: 3px; text-decoration-thickness: 1.5px; }
h1, h2, h3 { font-family: var(--da-font-display); letter-spacing: -0.025em; text-wrap: balance; margin: 0; color: var(--text-strong); }
p { text-wrap: pretty; }
.tabular-nums { font-variant-numeric: tabular-nums; }

.da-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 36px;
  padding: 0 12px;
  border-radius: 9px;
  border: 1.25px solid var(--border-card);
  background: var(--surface-z2);
  color: var(--text-strong);
  font-family: var(--da-font-ui);
  font-size: 12.5px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: var(--shadow-z1);
  transition-property: transform, background-color, border-color;
  transition-duration: 150ms;
  transition-timing-function: ease-out;
}
.da-btn:hover:not(:disabled) { border-color: var(--border-strong); }
.da-btn:active:not(:disabled) { transform: scale(0.97); }
.da-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.da-btn--primary {
  background: var(--da-accent-deep);
  border-color: var(--da-accent-deep);
  color: #FFFFFF;
}
.da-btn--primary:hover:not(:disabled) { background: var(--da-accent); border-color: var(--da-accent); }
.da-btn--icon { width: 36px; padding: 0; }
.da-btn--sm { min-height: 34px; padding: 0 10px; font-size: 12px; }
.da-btn.is-on {
  background: var(--da-accent-deep);
  border-color: var(--da-accent-deep);
  color: #FFFFFF;
}
@media (max-width: 768px) {
  .da-btn { min-height: 44px; padding: 0 14px; font-size: 13px; }
  .da-btn--icon { width: 44px; }
  .da-btn--sm { min-height: 44px; padding: 0 12px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
"""

ICONS_JS = """
const DA_ICONS = {
  grid: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
  play: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="margin-left:2px"><polygon points="6 4 20 12 6 20 6 4"/></svg>',
  flow: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="4" width="6" height="6" rx="1"/><rect x="15" y="14" width="6" height="6" rx="1"/><path d="M9 7h4a2 2 0 0 1 2 2v5"/></svg>',
  search: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  sun: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32 1.41-1.41"/></svg>',
  moon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  arrowUpRight: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10"/></svg>',
  arrowRight: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>',
  arrowLeft: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M19 12H5m6 6-6-6 6-6"/></svg>',
  plus: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
  minus: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14"/></svg>',
  fit: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
  close: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
  home: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/></svg>',
  phone: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4"/></svg>',
  monitor: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/></svg>'
};
"""

THEME_BOOT_JS = """
(function() {
  var key = 'design-aura:theme';
  try {
    var saved = localStorage.getItem(key);
    if (saved === 'light' || saved === 'dark') {
      document.documentElement.setAttribute('data-theme', saved);
    }
  } catch (e) {}
})();
"""

THEME_TOGGLE_JS = """
function daGetTheme() {
  return document.documentElement.getAttribute('data-theme') || 'dark';
}
function daSetTheme(next) {
  document.documentElement.setAttribute('data-theme', next);
  try { localStorage.setItem('design-aura:theme', next); } catch (e) {}
  document.dispatchEvent(new CustomEvent('designaura:themechange', { detail: { theme: next } }));
  document.dispatchEvent(new CustomEvent('horizonte:themechange', { detail: { theme: next } }));
  var btn = document.getElementById('btnThemeToggle');
  if (btn) {
    btn.setAttribute('aria-pressed', next === 'dark' ? 'true' : 'false');
    btn.innerHTML = (next === 'dark' ? DA_ICONS.sun : DA_ICONS.moon);
  }
}
function daToggleTheme() {
  daSetTheme(daGetTheme() === 'dark' ? 'light' : 'dark');
}
window.addEventListener('message', function(ev) {
  if (ev && ev.data && ev.data.type === 'designaura:theme' && (ev.data.theme === 'dark' || ev.data.theme === 'light')) {
    if (daGetTheme() !== ev.data.theme) daSetTheme(ev.data.theme);
  }
});
"""


STUDIO_FLOW_PALETTE = [
    "#38BDF8",  # sky
    "#FF6B38",  # vibrant orange
    "#10B981",  # emerald
    "#F59E0B",  # amber
    "#60A5FA",  # steel blue
    "#14B8A6",  # teal
    "#F43F5E",  # rose
]


def _box(screen: dict) -> tuple[float, float, float, float]:
    return (
        float(screen.get("x") or 0),
        float(screen.get("y") or 0),
        float(screen.get("w") or 360),
        float(screen.get("h") or 330),
    )


_ENTRY_WORD_RE = re.compile(
    r"(?:^|[^a-z0-9])(?:login|signin|signup|entrada|acesso|auth|2fa|onboarding|perfil|preferencias|configuracoes|minha-conta|settings)(?:$|[^a-z0-9])",
    re.I,
)
_MODULE_FLOWS = {
    "financeiro", "licitacoes", "atendimento", "certidoes", "vendas", "estoque",
    "rh", "clinica", "operacao", "operacoes", "logistica", "projetos", "comercial",
    "compras", "fiscal", "juridico", "relatorios", "analytics", "crm", "suporte",
}

_FLOW_LABELS_PT = {
    "nucleo": "Núcleo",
    "inicio": "Início",
    "acesso": "Acesso",
    "conta": "Conta",
    "financeiro": "Financeiro",
    "licitacoes": "Licitações",
    "certidoes": "Certidões",
    "atendimento": "Atendimento",
    "socios-mobile": "App Sócios",
    "mobile": "Mobile",
    "configuracoes": "Configurações",
    "preferencias": "Preferências",
    "operacoes": "Operações",
    "operacao": "Operação",
    "relatorios": "Relatórios",
    "cobranca": "Cobrança",
    "saude": "Saúde",
    "juridico": "Jurídico",
    "logistica": "Logística",
    "integracoes": "Integrações",
    "usuarios": "Usuários",
    "producao": "Produção",
    "gestao": "Gestão",
    "comercio": "Comércio",
    "educacao": "Educação",
    "notificacoes": "Notificações",
}


def _format_flow_label(flow: str, manifest: dict) -> str:
    custom = (manifest.get("flowLabels") or {}).get(flow)
    if custom:
        return str(custom)
    key = str(flow or "geral").strip().lower()
    if key in _FLOW_LABELS_PT:
        return _FLOW_LABELS_PT[key]
    words = [w for w in re.split(r"[-_\s]+", key) if w]
    return " ".join(_FLOW_LABELS_PT.get(w, w.capitalize()) for w in words) or "Geral"


def _is_entry_like(screen: dict) -> bool:
    fl = str(screen.get("flow") or "").strip().lower()
    if fl in _MODULE_FLOWS:
        return False
    sid = str(screen.get("id") or "").lower()
    title = str(screen.get("title") or "").lower()
    return bool(_ENTRY_WORD_RE.search(sid) or _ENTRY_WORD_RE.search(title) or fl in ("acesso", "auth", "conta"))


def _pick_hub_id(screens: list[dict], edges: list[dict], start_id: str) -> str:
    desktop = [s for s in screens if s.get("platform") != "mobile"]
    if not desktop:
        return start_id
    # Se existe um "portal" / "home" / "dashboard" / "inicio" com maior grau de saida, usa como hub central
    out_deg: dict[str, int] = {s["id"]: 0 for s in desktop}
    for e in edges:
        if e.get("from") in out_deg:
            out_deg[e["from"]] += 1
    for s in desktop:
        sid = str(s["id"]).lower()
        if any(k in sid for k in ("portal", "home", "dashboard", "painel", "inicio")) and out_deg.get(s["id"], 0) >= 2:
            return s["id"]
    if start_id in out_deg and out_deg[start_id] >= 2:
        return start_id
    best = max(desktop, key=lambda s: out_deg.get(s["id"], 0))
    return best["id"] if out_deg.get(best["id"], 0) >= 2 else start_id


def _smart_edge_sides(n1: dict, n2: dict) -> tuple[str, str]:
    cx1 = float(n1["x"]) + float(n1["w"]) * 0.5
    cy1 = float(n1["y"]) + float(n1["h"]) * 0.5
    cx2 = float(n2["x"]) + float(n2["w"]) * 0.5
    cy2 = float(n2["y"]) + float(n2["h"]) * 0.5
    dx = cx2 - cx1
    dy = cy2 - cy1
    if abs(dx) >= abs(dy) * 0.85:
        return ("r", "l") if dx >= 0 else ("l", "r")
    return ("b", "t") if dy >= 0 else ("t", "b")


def classify_and_style_edges(manifest: dict, recompute_sides: bool = False) -> None:
    """Classifica arestas em primary/secondary e aplica cores legiveis por fluxo."""
    screens = manifest.get("screens", [])
    edges = manifest.get("edges", [])
    if not edges or not screens:
        return

    node_map = {s["id"]: s for s in screens}
    proj = manifest.get("project", {})
    start_id = proj.get("startScreenId") or screens[0]["id"]
    hub_id = _pick_hub_id(screens, edges, start_id)

    # Paleta distinta por fluxo para eliminar monocromia de setas
    flow_colors: dict[str, str] = {}
    idx = 0
    for s in screens:
        fl = s.get("flow", "geral")
        if fl not in flow_colors:
            acc = s.get("accent") or ""
            # Se o accent e muito escuro/ferrugem repetido em tudo, usa a paleta de estudio
            flow_colors[fl] = STUDIO_FLOW_PALETTE[idx % len(STUDIO_FLOW_PALETTE)] if not acc else acc
            idx += 1
    # Se todas as arestas usam a mesma cor, re-colore pelo fluxo de destino
    distinct_edge_colors = {e.get("color") for e in edges if e.get("color")}
    recolor_all = len(distinct_edge_colors) <= 1 and len(flow_colors) > 1
    if recolor_all:
        unique_flows = list(flow_colors.keys())
        for i, fl in enumerate(unique_flows):
            flow_colors[fl] = STUDIO_FLOW_PALETTE[i % len(STUDIO_FLOW_PALETTE)]

    has_explicit_tier = any(e.get("tier") in ("primary", "secondary") for e in edges)
    dense_graph = len(edges) > 22

    primary_from_hub_flows: set[str] = set()
    primary_out_used: set[str] = set()
    primary_mobile_bridge = False

    for e in edges:
        n1 = node_map.get(e.get("from"))
        n2 = node_map.get(e.get("to"))
        if not n1 or not n2:
            continue
        if recolor_all or not e.get("color"):
            e["color"] = flow_colors.get(n2.get("flow", "geral"), "#38BDF8")
        if recompute_sides or not e.get("fromSide") or not e.get("toSide"):
            fs, ts = _smart_edge_sides(n1, n2)
            e["fromSide"] = fs
            e["toSide"] = ts

        if has_explicit_tier and e.get("tier") in ("primary", "secondary"):
            continue
        if not dense_graph:
            e["tier"] = "primary"
            continue

        f_id, t_id = n1["id"], n2["id"]
        same_sec = (n1.get("sectionId") or n1.get("flow")) == (n2.get("sectionId") or n2.get("flow"))
        same_row_forward = abs(float(n2.get("y") or 0) - float(n1.get("y") or 0)) < 48 and float(n2.get("x") or 0) > float(n1.get("x") or 0)

        if f_id == start_id and t_id == hub_id:
            e["tier"] = "primary"
        elif f_id == hub_id and n2.get("platform") != "mobile":
            t_flow = n2.get("flow", "geral")
            if t_flow not in primary_from_hub_flows:
                primary_from_hub_flows.add(t_flow)
                e["tier"] = "primary"
                if recompute_sides:
                    e["fromSide"] = "r"
                    e["toSide"] = "l"
            else:
                e["tier"] = "secondary"
        elif f_id == hub_id and n2.get("platform") == "mobile" and not primary_mobile_bridge:
            primary_mobile_bridge = True
            e["tier"] = "primary"
            if recompute_sides:
                e["fromSide"] = "b"
                e["toSide"] = "t"
        elif same_sec and same_row_forward and f_id not in primary_out_used and t_id not in (start_id, hub_id):
            primary_out_used.add(f_id)
            e["tier"] = "primary"
        else:
            e["tier"] = "secondary"


def apply_hub_and_spoke_layout(manifest: dict) -> list[str]:
    """Organiza o canvas em arvore panoramica Hub-and-Spoke (Acesso -> Hub Inicio -> Raias Desktop -> Faixa Mobile)."""
    notes: list[str] = []
    screens = manifest.get("screens", [])
    if not screens:
        return notes

    edges = manifest.get("edges", [])
    proj = manifest.setdefault("project", {})
    start_id = proj.get("startScreenId") or screens[0]["id"]
    hub_id = _pick_hub_id(screens, edges, start_id)

    old_sections = {s["id"]: s for s in manifest.get("sections", []) if s.get("id")}
    desktop_screens = [s for s in screens if s.get("platform") != "mobile"]
    mobile_screens = [s for s in screens if s.get("platform") == "mobile"]

    hub_screen = next((s for s in desktop_screens if s["id"] == hub_id), desktop_screens[0] if desktop_screens else screens[0])
    entry_screens = [s for s in desktop_screens if s["id"] != hub_screen["id"] and (_is_entry_like(s) or s["id"] == start_id)]
    # Limita coluna de acesso/conta a telas realmente de acesso/conta (max 4), o resto vai para raias
    entry_ids = {s["id"] for s in entry_screens}
    module_screens = [s for s in desktop_screens if s["id"] != hub_screen["id"] and s["id"] not in entry_ids]

    # Agrupa modulos desktop por secao/fluxo mantendo ordem
    mod_groups: dict[str, list[dict]] = {}
    mod_order: list[str] = []
    for s in module_screens:
        key = s.get("sectionId") or f"flow:{s.get('flow', 'geral')}"
        if key not in mod_groups:
            mod_groups[key] = []
            mod_order.append(key)
        mod_groups[key].append(s)

    new_sections: list[dict] = []
    gap_x = 34.0
    gap_y = 36.0
    pad_x = 28.0
    pad_top = 44.0
    pad_bot = 24.0
    lane_gap = 52.0

    # 1. Calcula raias horizontais Desktop na Coluna Direita
    desk_w, desk_h = 330.0, 290.0
    hub_w, hub_h = 410.0, 340.0
    col0_w = 340.0 if entry_screens else 0.0
    col1_x = (48.0 + col0_w + pad_x * 2 + 64.0) if entry_screens else 48.0
    col2_x = col1_x + hub_w + pad_x * 2 + 84.0

    cursor_y = 48.0
    flow_color_idx = 0
    for key in mod_order:
        grp = mod_groups[key]
        sid = grp[0].get("sectionId") or f"sec-{grp[0].get('flow', 'mod')}"
        prev_sec = old_sections.get(sid, {})
        per_row = 5 if len(grp) >= 9 else 4 if len(grp) >= 4 else max(1, len(grp))
        rows = (len(grp) + per_row - 1) // per_row
        cols = min(len(grp), per_row)
        sec_w = pad_x * 2 + cols * desk_w + max(0, cols - 1) * gap_x
        sec_h = pad_top + pad_bot + rows * desk_h + max(0, rows - 1) * gap_y
        accent = STUDIO_FLOW_PALETTE[flow_color_idx % len(STUDIO_FLOW_PALETTE)]
        flow_color_idx += 1

        for idx_s, s in enumerate(grp):
            r = idx_s // per_row
            c = idx_s % per_row
            s["w"] = desk_w
            s["h"] = desk_h
            s["x"] = round(col2_x + pad_x + c * (desk_w + gap_x))
            s["y"] = round(cursor_y + pad_top + r * (desk_h + gap_y))
            s["sectionId"] = sid
            s["accent"] = accent

        label = prev_sec.get("label") or str(grp[0].get("flow") or sid).upper()
        if f"({len(grp)}" not in label:
            label = f"{label} ({len(grp)} TELAS)" if len(grp) > 1 else label
        new_sections.append({
            "id": sid,
            "flow": grp[0].get("flow", "geral"),
            "label": label,
            "x": round(col2_x),
            "y": round(cursor_y),
            "w": round(sec_w),
            "h": round(sec_h),
            "accent": accent,
            "isStart": False,
            "isMobileSection": False,
        })
        cursor_y += sec_h + lane_gap

    desktop_bottom = max(cursor_y - lane_gap, 48.0 + hub_h + pad_top + pad_bot)
    center_y = max(48.0, round((desktop_bottom - (hub_h + pad_top + pad_bot)) * 0.45))

    # 2. Coluna 1: Hub / Tela Inicial em destaque
    hub_sec_w = hub_w + pad_x * 2
    hub_sec_h = hub_h + pad_top + pad_bot
    hub_screen["w"] = hub_w
    hub_screen["h"] = hub_h
    hub_screen["x"] = round(col1_x + pad_x)
    hub_screen["y"] = round(center_y + pad_top)
    hub_screen["isStart"] = True
    hub_screen["sectionId"] = "sec-start-hub"
    hub_accent = "#FF6B38"
    hub_screen["accent"] = hub_accent
    new_sections.insert(0, {
        "id": "sec-start-hub",
        "flow": hub_screen.get("flow", "inicio"),
        "label": f"★ TELA INICIAL · {hub_screen.get('title', 'INICIO').upper()}",
        "x": round(col1_x),
        "y": round(center_y),
        "w": round(hub_sec_w),
        "h": round(hub_sec_h),
        "accent": hub_accent,
        "isStart": True,
        "isMobileSection": False,
    })

    # 3. Coluna 0: Acesso / Conta empilhado limpo a esquerda do Hub
    if entry_screens:
        e_w, e_h = 310.0, 260.0
        e_gap = 28.0
        e_sec_h = pad_top + pad_bot + len(entry_screens) * e_h + max(0, len(entry_screens) - 1) * e_gap
        e_sec_w = e_w + pad_x * 2
        e_top = max(48.0, round(center_y + (hub_sec_h - e_sec_h) * 0.5))
        e_accent = "#60A5FA"
        for i_e, s in enumerate(entry_screens):
            s["w"] = e_w
            s["h"] = e_h
            s["x"] = round(48.0 + pad_x)
            s["y"] = round(e_top + pad_top + i_e * (e_h + e_gap))
            s["sectionId"] = "sec-acesso-conta"
            s["accent"] = e_accent
        new_sections.insert(0, {
            "id": "sec-acesso-conta",
            "flow": entry_screens[0].get("flow", "conta"),
            "label": f"ACESSO & CONTA ({len(entry_screens)})",
            "x": 48,
            "y": round(e_top),
            "w": round(e_sec_w),
            "h": round(e_sec_h),
            "accent": e_accent,
            "isStart": False,
            "isMobileSection": False,
        })
        desktop_bottom = max(desktop_bottom, e_top + e_sec_h)

    # 4. Faixa Inferior Dedicada: Mobile (panoramica em 1-2 linhas compactas)
    if mobile_screens:
        mob_y = round(desktop_bottom + 72.0)
        mob_w, mob_h = 236.0, 340.0
        mob_gap_x, mob_gap_y = 28.0, 34.0
        # Distribui panoramicamente (ate 8 por linha para casar com a largura do desktop)
        mob_per_row = 8 if len(mobile_screens) >= 10 else max(4, min(6, len(mobile_screens)))
        mob_rows = (len(mobile_screens) + mob_per_row - 1) // mob_per_row
        mob_cols = min(len(mobile_screens), mob_per_row)
        mob_sec_w = pad_x * 2 + mob_cols * mob_w + max(0, mob_cols - 1) * mob_gap_x
        mob_sec_h = pad_top + pad_bot + mob_rows * mob_h + max(0, mob_rows - 1) * mob_gap_y
        mob_accent = "#10B981"
        mob_sec_id = mobile_screens[0].get("sectionId") or "sec-mobile"
        prev_mob = old_sections.get(mob_sec_id, {})
        mob_label = prev_mob.get("label") or "MOBILE"
        if f"({len(mobile_screens)}" not in mob_label:
            mob_label = f"{mob_label} ({len(mobile_screens)} TELAS)"

        for i_m, s in enumerate(mobile_screens):
            r = i_m // mob_per_row
            c = i_m % mob_per_row
            s["w"] = mob_w
            s["h"] = mob_h
            s["x"] = round(48.0 + pad_x + c * (mob_w + mob_gap_x))
            s["y"] = round(mob_y + pad_top + r * (mob_h + mob_gap_y))
            s["sectionId"] = mob_sec_id
            s["accent"] = mob_accent

        new_sections.append({
            "id": mob_sec_id,
            "flow": mobile_screens[0].get("flow", "mobile"),
            "label": mob_label,
            "x": 48,
            "y": mob_y,
            "w": round(mob_sec_w),
            "h": round(mob_sec_h),
            "accent": mob_accent,
            "isStart": False,
            "isMobileSection": True,
        })

    manifest["sections"] = new_sections
    right_edge = max(float(s["x"]) + float(s["w"]) for s in new_sections) + 80
    bottom_edge = max(float(s["y"]) + float(s["h"]) for s in new_sections) + 80
    proj["worldWidth"] = int(right_edge)
    proj["worldHeight"] = int(bottom_edge)
    proj["hubScreenId"] = hub_screen["id"]
    classify_and_style_edges(manifest, recompute_sides=True)
    notes.append(f"hub-and-spoke layout aplicado ({len(screens)} telas, {int(right_edge)}x{int(bottom_edge)})")
    return notes


def apply_auto_layout(manifest: dict, force_relayout: bool = False) -> list[str]:
    """Preenche x/y ausentes, organiza mapas grandes em Hub-and-Spoke e afasta sobreposicoes."""
    notes: list[str] = []
    screens = manifest.get("screens", [])
    if not screens:
        return notes

    proj = manifest.setdefault("project", {})
    all_missing = all(s.get("x") is None or s.get("y") is None for s in screens)
    all_placed = all(s.get("x") is not None and s.get("y") is not None for s in screens)

    # Detecta layout torre vertical degenerado ou manifesto >= 6 telas ainda nao organizado em Hub-and-Spoke
    is_vertical_tower = False
    has_hub_section = any(sec.get("id") == "sec-start-hub" for sec in manifest.get("sections", []))
    needs_hub_tree = len(screens) >= 6 and not has_hub_section and not proj.get("lockManualLayout")
    if all_placed and len(screens) >= 10 and not proj.get("lockManualLayout"):
        xs = [float(s["x"]) + float(s.get("w") or 360) for s in screens]
        ys = [float(s["y"]) + float(s.get("h") or 350) for s in screens]
        span_w = max(xs) - min(float(s["x"]) for s in screens)
        span_h = max(ys) - min(float(s["y"]) for s in screens)
        if span_h > span_w * 1.12:
            is_vertical_tower = True

    if force_relayout or (all_missing and len(screens) >= 4) or is_vertical_tower or needs_hub_tree:
        if is_vertical_tower and not force_relayout:
            notes.append("torre vertical detectada; reorganizando para Hub-and-Spoke panoramico")
        elif needs_hub_tree and not force_relayout and not all_missing:
            notes.append("layout manual sem sec-start-hub detectado; aplicando arvore Hub-and-Spoke canonica")
        notes.extend(apply_hub_and_spoke_layout(manifest))
        return notes

    sections = manifest.setdefault("sections", [])
    sec_by_id = {s["id"]: s for s in sections if s.get("id")}
    for screen in screens:
        sid = screen.get("sectionId")
        if sid and sid not in sec_by_id:
            sec = {
                "id": sid,
                "flow": screen.get("flow", "geral"),
                "label": str(sid).replace("-", " "),
                "accent": screen.get("accent", "#EA580C"),
            }
            sections.append(sec)
            sec_by_id[sid] = sec
            notes.append(f"secao criada: {sid}")

    groups: dict[str, list] = {}
    order: list[str] = []
    for screen in screens:
        key = screen.get("sectionId") or f"flow:{screen.get('flow', 'geral')}"
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(screen)

    cursor_y = 40.0
    for key in order:
        group = groups[key]
        sid = group[0].get("sectionId")
        sec = sec_by_id.get(sid) if sid else None
        missing = [s for s in group if s.get("x") is None or s.get("y") is None]
        if not missing:
            continue
        mobile = all(s.get("platform") == "mobile" for s in group)
        gap = 28.0
        pad = 28.0
        col_w = 250.0 if mobile else 350.0
        row_h = 370.0 if mobile else 320.0
        per_row = 5 if mobile else 4
        placed = [s for s in group if s.get("x") is not None and s.get("y") is not None]
        if placed:
            x = max(float(s["x"]) + float(s.get("w") or col_w) for s in placed) + gap
            y = min(float(s["y"]) for s in placed)
            for screen in missing:
                screen["w"] = screen.get("w") or col_w
                screen["h"] = screen.get("h") or row_h
                screen["x"] = x
                screen["y"] = y
                x += float(screen["w"]) + gap
            notes.append(f"auto-layout parcial em {key}: {len(missing)} telas")
            continue
        origin_x = 40.0
        origin_y = cursor_y
        if sec and sec.get("x") is not None and sec.get("y") is not None:
            origin_x = float(sec["x"]) + pad
            origin_y = float(sec["y"]) + 40
        for index, screen in enumerate(group):
            screen["w"] = screen.get("w") or col_w
            screen["h"] = screen.get("h") or row_h
            col = index % per_row
            row = index // per_row
            screen["x"] = origin_x + col * (float(screen["w"]) + gap)
            screen["y"] = origin_y + row * (float(screen["h"]) + gap)
        rows = max(1, (len(group) + per_row - 1) // per_row)
        sec_w = pad * 2 + min(len(group), per_row) * col_w + max(0, min(len(group), per_row) - 1) * gap
        sec_h = 60 + rows * row_h + max(0, rows - 1) * gap
        if sec is not None:
            sec.setdefault("x", 40)
            sec.setdefault("y", cursor_y)
            sec.setdefault("w", sec_w)
            sec.setdefault("h", sec_h)
        cursor_y += sec_h + 48
        notes.append(f"auto-layout em {key}")

    changed = True
    guard = 0
    while changed and guard < 80:
        changed = False
        guard += 1
        for index, left in enumerate(screens):
            ax, ay, aw, ah = _box(left)
            for right in screens[index + 1:]:
                bx, by, bw, bh = _box(right)
                overlaps = ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by
                if overlaps:
                    right["x"] = ax + aw + 24
                    changed = True
                    notes.append(f"separou sobreposicao {left.get('id')} / {right.get('id')}")
                    break
            if changed:
                break

    if screens:
        right_edge = max(float(s.get("x") or 0) + float(s.get("w") or 0) for s in screens) + 80
        bottom_edge = max(float(s.get("y") or 0) + float(s.get("h") or 0) for s in screens) + 80
        proj["worldWidth"] = max(int(proj.get("worldWidth") or 0), int(right_edge))
        proj["worldHeight"] = max(int(proj.get("worldHeight") or 0), int(bottom_edge))
    classify_and_style_edges(manifest, recompute_sides=False)
    return notes


def verify_screen_files(manifest: dict, manifest_path: Path, out_dir: Path) -> list[str]:
    errors = []
    roots = [manifest_path.parent, out_dir]
    for screen in manifest.get("screens", []):
        rel = screen.get("file") or ""
        if not rel:
            errors.append(f"{screen.get('id')}: sem file")
            continue
        if rel.startswith(("http://", "https://", "/")):
            continue
        if screen.get("isSpaRoute") or (screen.get("route") and not screen.get("file")):
            continue
        if not any((root / rel).exists() for root in roots):
            errors.append(f"{screen.get('id')}: arquivo ausente '{rel}'")
    return errors


def _normalize_screen_targets(manifest: dict, app_base: str = "") -> bool:
    """Resolve telas SPA ('route') em URLs navegaveis para vitrine unificada. Retorna True se houver SPA."""
    base = (app_base or manifest.get("project", {}).get("appBaseUrl") or "").rstrip("/")
    has_spa = bool(base)
    for screen in manifest.get("screens", []):
        route = str(screen.get("route") or "").strip()
        fval = str(screen.get("file") or "").strip()
        if route and not fval:
            has_spa = True
            screen["isSpaRoute"] = True
            if route.startswith(("http://", "https://")):
                screen["file"] = route
            elif base:
                screen["file"] = f"{base}{route if route.startswith('/') else '/' + route}"
            else:
                screen["file"] = route if route.startswith("/") else "/" + route
        elif fval.startswith("/") and not fval.startswith("//"):
            has_spa = True
            screen["isSpaRoute"] = True
    return has_spa


def verify_generated_links(out_dir: Path) -> list[str]:
    errors = []
    href_re = re.compile(r"""(?:href|src)=["']([^"']+)["']""")
    for name in ("fluxo.html", "preview.html", "index.html", "entrega.html"):
        fpath = out_dir / name
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        for href in href_re.findall(text):
            if href.startswith(("#", "mailto:", "javascript:", "data:", "http://", "https://", "/")):
                continue
            path = href.split("?", 1)[0].split("#", 1)[0]
            if not path:
                continue
            if not (out_dir / path).exists() and not (out_dir / Path(path).name).exists():
                errors.append(f"{name}: href quebrado {href}")
    return errors


def validate_manifest(manifest: dict) -> None:
    screens = manifest.get("screens", [])
    if not screens:
        raise ValueError("screen-manifest.json deve conter ao menos 1 tela em 'screens'.")
    ids = [s["id"] for s in screens]
    if len(ids) != len(set(ids)):
        raise ValueError("IDs duplicados encontrados em 'screens'.")
    id_set = set(ids)
    for e in manifest.get("edges", []):
        if e["from"] not in id_set or e["to"] not in id_set:
            raise ValueError(f"Aresta '{e.get('id')}' aponta para tela inexistente: {e['from']} -> {e['to']}")
    for j in manifest.get("journeys", []):
        for st in j.get("steps", []):
            if st["screenId"] not in id_set:
                raise ValueError(f"Jornada '{j.get('id')}' referencia tela inexistente: {st['screenId']}")


def _is_dark_hex(hx: str) -> bool:
    h = hx.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) < 6:
        return False
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) < 128


def extract_tokens_from_css(tokens_path: Path | None) -> dict[str, dict[str, str]]:
    """Extrai variaveis hex Light/Dark de tokens.css para harmonizar a vitrine com o projeto."""
    result: dict[str, dict[str, str]] = {"light": {}, "dark": {}}
    if not tokens_path or not tokens_path.exists():
        return result
    try:
        text = tokens_path.read_text(encoding="utf-8")
    except OSError:
        return result
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    block_re = re.compile(r"([^{}]+)\{([^{}]+)\}", re.S)
    var_re = re.compile(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b")
    for m in block_re.finditer(text):
        sel = m.group(1).strip().lower()
        body = m.group(2)
        pairs = {vm.group(1): vm.group(2) for vm in var_re.finditer(body)}
        if not pairs:
            continue
        if 'data-theme="dark"' in sel or "data-theme='dark'" in sel or ".dark" in sel:
            bucket = result["dark"]
        elif 'data-theme="light"' in sel or "data-theme='light'" in sel:
            bucket = result["light"]
        elif ":root" in sel:
            z1 = pairs.get("--surface-z1") or pairs.get("--surface-z0") or ""
            bucket = result["dark"] if (z1 and _is_dark_hex(z1)) else result["light"]
        else:
            continue
        bucket.update(pairs)
    return result


def build_base_css(manifest: dict, tokens_link: str, parsed_tokens: dict[str, dict[str, str]] | None = None) -> str:
    th = manifest.get("theme", {})
    pt = parsed_tokens or {"light": {}, "dark": {}}
    tl, td = pt.get("light", {}), pt.get("dark", {})

    bg_dark = td.get("--surface-z1") or th.get("canvasBgDark", "#101620")
    card_dark = td.get("--surface-z2") or th.get("surfaceCardDark", "#17202E")
    well_dark = td.get("--surface-z0") or "#090E16"
    border_dark = td.get("--border-subtle") or "#2C3E58"
    border_strong_dark = td.get("--border-strong") or "#49638A"
    text_strong_dark = td.get("--text-strong") or "#F3F6FB"
    text_body_dark = td.get("--text-body") or "#D6E1F0"
    text_muted_dark = td.get("--text-muted") or "#A9BAD1"

    bg_light = tl.get("--surface-z1") or th.get("canvasBgLight", "#D9E5F3")
    card_light = tl.get("--surface-z2") or th.get("surfaceCardLight", "#FFFFFF")
    well_light = tl.get("--surface-z0") or "#C6D6EA"
    border_light = tl.get("--border-subtle") or "#93ABC7"
    border_strong_light = tl.get("--border-strong") or "#5A769B"
    text_strong_light = tl.get("--text-strong") or "#0E1726"
    text_body_light = tl.get("--text-body") or "#1C2B3F"
    text_muted_light = tl.get("--text-muted") or "#3E4E63"

    brand_navy = tl.get("--surface-brand-dark") or td.get("--surface-brand-dark") or th.get("brandNavy", "#0C254A")
    accent_dark = td.get("--primary") or td.get("--accent") or th.get("brandAccent", "#2563EB")
    accent_light = tl.get("--primary") or tl.get("--accent") or th.get("brandAccentDeep", "#14427A")
    accent_deep = tl.get("--primary") or td.get("--primary") or th.get("brandAccentDeep", "#14427A")

    css = BASE_STYLES
    replacements = {
        "__BG_DARK__": bg_dark,
        "__CARD_DARK__": card_dark,
        "__WELL_DARK__": well_dark,
        "__BORDER_DARK__": border_dark,
        "__BORDER_STRONG_DARK__": border_strong_dark,
        "__TEXT_STRONG_DARK__": text_strong_dark,
        "__TEXT_BODY_DARK__": text_body_dark,
        "__TEXT_MUTED_DARK__": text_muted_dark,
        "__BG_LIGHT__": bg_light,
        "__CARD_LIGHT__": card_light,
        "__WELL_LIGHT__": well_light,
        "__BORDER_LIGHT__": border_light,
        "__BORDER_STRONG_LIGHT__": border_strong_light,
        "__TEXT_STRONG_LIGHT__": text_strong_light,
        "__TEXT_BODY_LIGHT__": text_body_light,
        "__TEXT_MUTED_LIGHT__": text_muted_light,
        "__BRAND_NAVY__": brand_navy,
        "__BRAND_ACCENT_DARK__": accent_dark,
        "__BRAND_ACCENT_LIGHT__": accent_light,
        "__BRAND_ACCENT_DEEP__": accent_deep,
    }
    for k, v in replacements.items():
        css = css.replace(k, v)
    link_tag = f'<link rel="stylesheet" href="{html.escape(tokens_link)}">\n' if tokens_link else ""
    return f"{link_tag}<style>\n{css}\n</style>"


def render_fluxo_html(manifest: dict, tokens_link: str, parsed_tokens: dict[str, dict[str, str]] | None = None) -> str:
    proj = manifest.get("project", {})
    name = html.escape(proj.get("name", "Projeto Design Aura"))
    subtitle = html.escape(proj.get("subtitle", "Mapa de Fluxo Estilo Figma"))
    # Estudio Figma abre em dark por padrao para maximo contraste dos artboards (toggle T alterna livremente)
    canvas_theme = html.escape(proj.get("canvasTheme", "dark"))
    world_w = int(proj.get("worldWidth", 2400))
    world_h = int(proj.get("worldHeight", 1600))
    start_id = proj.get("hubScreenId") or proj.get("startScreenId") or manifest["screens"][0]["id"]
    has_mobile = any(s.get("platform") == "mobile" for s in manifest["screens"])
    head_css = build_base_css(manifest, tokens_link, parsed_tokens)
    manifest_json = json.dumps(manifest, ensure_ascii=False)

    flows = []
    flow_counts: dict[str, int] = {}
    flow_colors: dict[str, str] = {}
    for s in manifest["screens"]:
        fl = s.get("flow", "geral")
        flow_counts[fl] = flow_counts.get(fl, 0) + 1
        if fl not in flow_colors:
            flow_colors[fl] = s.get("accent", "#38BDF8")
            flows.append(fl)

    total_screens = len(manifest["screens"])
    flow_buttons = [
        f'<button type="button" class="fx-flow-btn is-active" data-flow="all">Todos <span class="fx-count tabular-nums">{total_screens}</span></button>'
    ]
    for fl in flows:
        col = flow_colors[fl]
        cnt = flow_counts[fl]
        lbl = _format_flow_label(fl, manifest)
        flow_buttons.append(
            f'<button type="button" class="fx-flow-btn" data-flow="{html.escape(fl)}">'
            f'<span class="fx-dot" style="background:{html.escape(col)}"></span>{html.escape(lbl)} '
            f'<span class="fx-count tabular-nums">{cnt}</span></button>'
        )

    mobile_jump_btn = (
        '<button type="button" class="da-btn fx-hide-sm" id="btnJumpMobile" title="Ir para secao Mobile (M)">Mobile</button>'
        if has_mobile
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="{canvas_theme}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mapa de Fluxo · Estilo Figma · {name}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap">
<script>{THEME_BOOT_JS}</script>
{head_css}
<style>
  html, body {{ height: 100%; overflow: hidden; user-select: none; touch-action: none; }}
  .fx-app {{ display: flex; flex-direction: column; height: 100dvh; width: 100vw; overflow: hidden; background: var(--surface-z1); }}
  .fx-bar {{
    position: relative; z-index: 40; display: flex; align-items: center; gap: 10px;
    min-height: 54px; padding: 6px 14px; background: var(--surface-glass);
    border-bottom: 1.25px solid var(--border-card); box-shadow: var(--shadow-z1);
  }}
  .fx-brand {{ display: flex; flex-direction: column; gap: 1px; min-width: 0; max-width: 240px; flex: 0 1 auto; }}
  .fx-brand strong {{ font-family: var(--da-font-display); font-size: 13px; font-weight: 700; color: var(--text-strong); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .fx-brand span {{ font-family: var(--da-font-mono); font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .fx-flows {{
    display: flex; align-items: center; gap: 2px; padding: 3px; border-radius: 10px;
    background: var(--surface-z0); border: 1px solid var(--border-card); overflow-x: auto; scrollbar-width: none; flex: 1 1 auto; min-width: 0;
  }}
  .fx-flows::-webkit-scrollbar {{ display: none; }}
  .fx-flow-btn {{
    display: inline-flex; align-items: center; gap: 4px; min-height: 30px; padding: 0 7px;
    border-radius: 7px; border: 1px solid transparent; background: transparent; color: var(--text-body);
    font-family: var(--da-font-ui); font-size: 11.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
    transition-property: background-color, border-color, color; transition-duration: 150ms; transition-timing-function: ease-out;
  }}
  .fx-flow-btn:hover {{ color: var(--text-strong); background: var(--surface-z2); }}
  .fx-flow-btn.is-active {{ background: var(--surface-z2); color: var(--text-strong); border-color: var(--border-strong); box-shadow: var(--shadow-z1); }}
  .fx-count {{ font-family: var(--da-font-mono); font-size: 11px; color: var(--text-muted); padding: 1px 5px; border-radius: 999px; background: rgba(148,163,184,0.16); }}
  .fx-dot {{ width: 8px; height: 8px; border-radius: 50%; flex: none; }}
  .fx-actions {{ display: flex; align-items: center; gap: 6px; flex: none; }}

  .fx-stage {{
    position: relative; flex: 1 1 auto; overflow: hidden; cursor: grab;
    background-color: var(--surface-z0);
    background-image: radial-gradient(rgba(148, 163, 184, 0.22) 1.25px, transparent 1.25px);
    background-size: 24px 24px;
  }}
  .fx-stage.is-panning {{ cursor: grabbing; }}
  .fx-world {{ position: absolute; top: 0; left: 0; width: {world_w}px; height: {world_h}px; transform-origin: 0 0; will-change: transform; }}

  .fx-section {{
    position: absolute; border-radius: 20px; border: 1.5px solid var(--sec-accent, var(--border-strong));
    background: rgba(15, 26, 38, 0.36); transition-property: opacity; transition-duration: 180ms;
  }}
  .fx-section.is-start {{
    border-width: 2px; background: rgba(255, 107, 56, 0.08);
    box-shadow: 0 0 0 1px rgba(255, 107, 56, 0.25), 0 16px 38px -12px rgba(255, 107, 56, 0.24);
  }}
  .fx-section.is-mobile-sec {{ background: rgba(16, 185, 129, 0.07); }}
  html[data-theme="light"] .fx-section {{ background: rgba(255, 255, 255, 0.52); }}
  html[data-theme="light"] .fx-section.is-start {{ background: rgba(234, 88, 12, 0.07); }}
  .fx-section.is-dim {{ opacity: 0.22; }}
  .fx-sec-label {{
    position: absolute; top: -14px; left: 16px; display: inline-flex; align-items: center; gap: 6px;
    height: 28px; padding: 0 12px; border-radius: 999px; background: var(--da-navy); color: #FFFFFF;
    font-family: var(--da-font-mono); font-size: 11.5px; font-weight: 700; letter-spacing: 0.02em;
    border: 1.25px solid var(--sec-accent, var(--border-strong));
  }}
  .fx-section.is-start .fx-sec-label {{ background: var(--da-accent-deep); border-color: var(--da-accent); color: #FFFFFF; }}

  .fx-edges {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible; z-index: 15; }}
  .fx-edge-path {{ fill: none; stroke-width: 2.25; opacity: 0.78; transition-property: opacity, stroke-width; transition-duration: 150ms; }}
  .fx-edge-path.is-dashed {{ stroke-dasharray: 6 5; }}
  .fx-edge-path.is-hl {{ opacity: 1; stroke-width: 3.25; }}
  .fx-edge-path.is-dim {{ opacity: 0.10; }}
  .fx-edge-path.is-hidden {{ display: none; }}
  .fx-edge-badge {{
    position: absolute; transform: translate(-50%, -50%); z-index: 18;
    display: inline-flex; align-items: center; gap: 4px; min-height: 26px; padding: 2px 10px; border-radius: 999px;
    background: var(--surface-z2); border: 1.25px solid var(--edge-color, var(--border-strong));
    color: var(--text-strong); font-family: var(--da-font-ui); font-size: 11px; font-weight: 600;
    cursor: pointer; box-shadow: var(--shadow-z1); transition-property: opacity, transform; transition-duration: 150ms;
    white-space: nowrap;
  }}
  .fx-edge-badge.is-dim {{ opacity: 0.14; }}
  .fx-edge-badge.is-hidden {{ display: none; }}

  .fx-node {{
    position: absolute; z-index: 10; display: flex; flex-direction: column; border-radius: 16px; padding: 8px;
    background: var(--surface-z2); border: 1.5px solid var(--border-card); box-shadow: var(--shadow-z2);
    cursor: pointer; transition-property: opacity, border-color, transform; transition-duration: 160ms;
  }}
  .fx-node.is-start {{ border-color: #FF6B38; border-width: 2px; }}
  .fx-node.is-selected {{ border-color: var(--da-accent); border-width: 2.5px; }}
  .fx-node.is-dim {{ opacity: 0.22; }}
  .fx-node-head {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 2px 4px 7px; }}
  .fx-node-titles {{ display: flex; flex-direction: column; min-width: 0; }}
  .fx-node-name {{ font-family: var(--da-font-display); font-size: 13px; font-weight: 700; color: var(--text-strong); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .fx-node-file {{ font-family: var(--da-font-mono); font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .fx-preview {{
    position: relative; flex: 1 1 auto; border-radius: 8px; overflow: hidden;
    border: 1px solid var(--border-card); background: var(--surface-z0);
  }}
  .fx-preview-frame {{ position: absolute; top: 0; left: 0; border: 0; transform-origin: 0 0; pointer-events: none; opacity: 0; transition-property: opacity; transition-duration: 180ms; }}
  .fx-preview-frame.is-loaded {{ opacity: 1; }}
  .fx-schematic {{
    position: absolute; inset: 0; padding: 12px; display: flex; flex-direction: column; justify-content: space-between;
    background: var(--surface-z1); color: var(--text-strong);
  }}
  .fx-node-foot {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 7px 4px 2px; font-size: 11.5px; }}
  .fx-node-metric {{ font-family: var(--da-font-mono); font-weight: 600; color: var(--text-strong); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .fx-node-pill {{ padding: 2px 8px; border-radius: 999px; border: 1px solid var(--border-card); background: var(--surface-z0); font-size: 11px; font-weight: 600; color: var(--text-body); flex: none; }}
  .fx-node.is-start .fx-node-pill {{ background: rgba(255,107,56,0.18); border-color: #FF6B38; color: var(--text-strong); }}

  .fx-inspector {{
    position: absolute; left: 16px; bottom: 16px; z-index: 35; width: 312px; max-width: calc(100vw - 32px);
    max-height: min(440px, calc(100dvh - 104px)); overflow-y: auto; border-radius: 16px; padding: 14px;
    background: var(--surface-glass); border: 1.5px solid var(--border-strong); box-shadow: var(--shadow-z2);
    display: flex; flex-direction: column; gap: 10px;
  }}
  .fx-inspector.is-collapsed {{ width: auto; padding: 8px 12px; }}
  .fx-insp-body {{ display: flex; flex-direction: column; gap: 10px; }}
  .fx-inspector.is-collapsed .fx-insp-body {{ display: none; }}
  .fx-insp-top {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }}
  .fx-insp-meta {{ font-family: var(--da-font-mono); font-size: 11.5px; color: var(--da-accent-text); font-weight: 600; }}
  .fx-insp-desc {{ margin: 0; font-size: 12.5px; color: var(--text-body); }}
  .fx-hop-list {{ display: flex; flex-direction: column; gap: 5px; }}
  .fx-hop {{
    display: flex; align-items: center; justify-content: space-between; gap: 8px; width: 100%; min-height: 36px;
    padding: 5px 10px; border-radius: 8px; border: 1px solid var(--border-card); background: var(--surface-z2);
    color: var(--text-strong); font-size: 12px; font-weight: 600; text-align: left; cursor: pointer;
  }}
  .fx-hop:hover {{ border-color: var(--da-accent); }}
  .fx-insp-btns {{ display: flex; gap: 8px; }}
  .fx-insp-btns .da-btn {{ flex: 1; }}

  .fx-hud {{ position: absolute; right: 16px; bottom: 16px; z-index: 35; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }}
  .fx-minimap {{
    position: relative; width: 204px; height: 132px; border-radius: 12px; background: var(--surface-glass);
    border: 1.5px solid var(--border-strong); box-shadow: var(--shadow-z2); overflow: hidden; cursor: crosshair;
  }}
  .fx-mini-node {{ position: absolute; border-radius: 2px; }}
  .fx-mini-vp {{ position: absolute; border: 2px solid var(--da-mini-vp-border); background: var(--da-mini-vp-bg); border-radius: 3px; pointer-events: none; }}
  .fx-zoombar {{
    display: inline-flex; align-items: center; gap: 4px; padding: 4px; border-radius: 10px;
    background: var(--surface-glass); border: 1.5px solid var(--border-strong); box-shadow: var(--shadow-z2);
  }}
  .fx-zoom-val {{ min-width: 46px; text-align: center; font-family: var(--da-font-mono); font-size: 12px; font-weight: 700; color: var(--text-strong); }}

  .fx-hintbar {{
    position: absolute; left: calc(50% + 56px); bottom: 16px; transform: translateX(-50%); z-index: 30;
    padding: 6px 14px; border-radius: 999px; background: var(--surface-glass);
    border: 1px solid var(--border-card); font-family: var(--da-font-mono); font-size: 11px;
    color: var(--text-muted); white-space: nowrap; pointer-events: none;
  }}

  .fx-modal {{ position: fixed; inset: 0; z-index: 90; display: flex; flex-direction: column; padding: 16px; background: rgba(8, 16, 24, 0.84); }}
  .fx-modal[hidden] {{ display: none !important; }}
  .fx-modal-box {{
    flex: 1; display: flex; flex-direction: column; max-width: 1440px; width: 100%; margin: 0 auto;
    border-radius: 16px; overflow: hidden; background: var(--surface-z2); border: 1.5px solid var(--border-strong);
  }}
  .fx-modal-bar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px; background: var(--da-navy); color: #FFFFFF; }}
  .fx-modal-stage {{ flex: 1; display: flex; align-items: center; justify-content: center; background: var(--surface-z0); overflow: hidden; padding: 16px; }}
  .fx-modal-wrap {{ width: 100%; height: 100%; border-radius: 12px; overflow: hidden; background: var(--surface-z1); isolation: isolate; }}
  .fx-modal-wrap.is-mobile {{
    width: 390px; height: min(844px, calc(100% - 8px)); border-radius: 38px; border: 8px solid #141923;
    outline: 1.5px solid var(--border-strong); box-shadow: 0 24px 60px -12px rgba(0, 0, 0, 0.55);
    overflow: hidden; clip-path: inset(0 round 30px); transform: translateZ(0);
  }}
  .fx-modal-iframe {{ width: 100%; height: 100%; display: block; border: 0; background: var(--surface-z1); }}

  @media (max-width: 1180px) {{
    .fx-hintbar {{ display: none; }}
  }}
  @media (max-width: 768px) {{
    .fx-bar {{ flex-wrap: wrap; gap: 8px; padding: 8px 10px; }}
    .fx-flows {{ order: 3; flex: 1 0 100%; }}
    .fx-flow-btn {{ min-height: 44px; }}
    .fx-hop {{ min-height: 44px; }}
    .fx-minimap, .fx-hide-sm {{ display: none; }}
    .fx-inspector {{ left: 10px; right: 10px; bottom: 72px; width: auto; max-height: 40dvh; }}
  }}
</style>
</head>
<body>
<div class="fx-app">
  <header class="fx-bar">
    <div class="fx-brand">
      <strong>{name}</strong>
      <span>{subtitle}</span>
    </div>
    <div class="fx-flows" role="group" aria-label="Filtrar por fluxo">
      {"".join(flow_buttons)}
    </div>
    <div class="fx-actions">
      <button type="button" class="da-btn fx-hide-sm" id="btnJumpStart" title="Centralizar na tela inicial (H)">★ Início</button>
      {mobile_jump_btn}
      <button type="button" class="da-btn fx-hide-sm" id="btnEdgesMode" title="Alternar setas principais / todas (E)">Setas</button>
      <button type="button" class="da-btn is-on fx-hide-sm" id="btnLive" title="Alternar preview ao vivo (L)">Ao Vivo</button>
      <a class="da-btn da-btn--primary" href="preview.html">Preview</a>
      <a class="da-btn fx-hide-sm" href="index.html">Galeria</a>
      <button type="button" class="da-btn da-btn--icon" id="btnThemeToggle" aria-label="Alternar tema" onclick="daToggleTheme()"></button>
    </div>
  </header>

  <main class="fx-stage" id="stage">
    <div class="fx-world" id="world">
      <div id="sectionsLayer"></div>
      <svg class="fx-edges" id="edgesSvg" viewBox="0 0 {world_w} {world_h}"></svg>
      <div id="nodesLayer"></div>
      <div id="badgesLayer"></div>
    </div>

    <aside class="fx-inspector" id="inspector" aria-label="Inspetor de tela selecionada">
      <div class="fx-insp-top">
        <div>
          <div class="fx-insp-meta" id="inspMeta"></div>
          <h2 id="inspTitle" style="font-size:17px;margin-top:3px;"></h2>
        </div>
        <div style="display:flex;gap:6px;align-items:center;">
          <button type="button" class="da-btn da-btn--sm" id="btnIsolate">Isolar (I)</button>
          <button type="button" class="da-btn da-btn--sm" id="btnToggleInsp" aria-label="Recolher inspetor">Recolher</button>
        </div>
      </div>
      <div class="fx-insp-body">
        <p class="fx-insp-desc" id="inspDesc"></p>
        <div id="inspOutWrap"><strong style="font-size:11.5px;color:var(--text-muted)">Vai para</strong><div class="fx-hop-list" id="inspOut"></div></div>
        <div id="inspInWrap"><strong style="font-size:11.5px;color:var(--text-muted)">Vem de</strong><div class="fx-hop-list" id="inspIn"></div></div>
        <div class="fx-insp-btns">
          <button type="button" class="da-btn da-btn--primary" id="btnModalPreview">Abrir Modal</button>
          <a class="da-btn" id="btnOpenFull" href="#">Tela Cheia</a>
        </div>
      </div>
    </aside>

    <div class="fx-hintbar">Arraste: mover · Scroll: zoom · Clique: inspecionar/isolar · Duplo clique: modal · F: enquadrar · E: setas · T: tema</div>

    <div class="fx-hud">
      <div class="fx-minimap" id="minimap" title="Clique para navegar no mapa">
        <div id="miniNodes"></div>
        <div class="fx-mini-vp" id="miniVp"></div>
      </div>
      <div class="fx-zoombar">
        <button type="button" class="da-btn da-btn--icon" id="btnZoomOut" aria-label="Diminuir zoom"></button>
        <span class="fx-zoom-val tabular-nums" id="zoomVal">55%</span>
        <button type="button" class="da-btn da-btn--icon" id="btnZoomIn" aria-label="Aumentar zoom"></button>
        <button type="button" class="da-btn da-btn--sm" id="btnFit" title="Ajustar tudo (F)">Fit</button>
      </div>
    </div>
  </main>
</div>

<div class="fx-modal" id="previewModal" hidden>
  <div class="fx-modal-box">
    <div class="fx-modal-bar">
      <div><strong id="modalTitle">Tela</strong> <span id="modalFile" style="font-family:var(--da-font-mono);font-size:12px;opacity:0.8;margin-left:8px;"></span></div>
      <div style="display:flex;gap:8px;align-items:center;">
        <a class="da-btn da-btn--sm" id="modalNewTab" href="#" target="_blank" rel="noopener">Abrir em nova aba</a>
        <button type="button" class="da-btn da-btn--icon" id="btnCloseModal" aria-label="Fechar modal"></button>
      </div>
    </div>
    <div class="fx-modal-stage">
      <div class="fx-modal-wrap" id="modalWrap">
        <iframe class="fx-modal-iframe" id="modalIframe" title="Preview interativo"></iframe>
      </div>
    </div>
  </div>
</div>

<script>
{ICONS_JS}
{THEME_TOGGLE_JS}
(function() {{
  var MANIFEST = {manifest_json};
  var SECTIONS = MANIFEST.sections || [];
  var NODES = MANIFEST.screens || [];
  var EDGES = MANIFEST.edges || [];
  var WORLD_W = {world_w};
  var WORLD_H = {world_h};
  var START_ID = '{html.escape(start_id)}';
  var nodeMap = {{}};
  NODES.forEach(function(n) {{ nodeMap[n.id] = n; }});

  var state = {{
    x: 32, y: 32, scale: 0.55,
    activeFlow: 'all',
    selectedId: START_ID,
    isolate: false,
    showAllEdges: EDGES.length <= 22,
    livePreview: true
  }};

  document.getElementById('btnThemeToggle').innerHTML = daGetTheme() === 'dark' ? DA_ICONS.sun : DA_ICONS.moon;
  document.getElementById('btnZoomOut').innerHTML = DA_ICONS.minus;
  document.getElementById('btnZoomIn').innerHTML = DA_ICONS.plus;
  document.getElementById('btnCloseModal').innerHTML = DA_ICONS.close;

  var stage = document.getElementById('stage');
  var world = document.getElementById('world');
  var sectionsLayer = document.getElementById('sectionsLayer');
  var nodesLayer = document.getElementById('nodesLayer');
  var badgesLayer = document.getElementById('badgesLayer');
  var edgesSvg = document.getElementById('edgesSvg');
  var zoomVal = document.getElementById('zoomVal');
  var miniNodes = document.getElementById('miniNodes');
  var miniVp = document.getElementById('miniVp');
  var minimap = document.getElementById('minimap');
  var btnEdgesMode = document.getElementById('btnEdgesMode');

  function esc(str) {{
    return String(str == null ? '' : str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}

  function anchorPoint(node, side) {{
    if (side === 'r') return {{ x: node.x + node.w, y: node.y + node.h * 0.5 }};
    if (side === 'l') return {{ x: node.x, y: node.y + node.h * 0.5 }};
    if (side === 'b') return {{ x: node.x + node.w * 0.5, y: node.y + node.h }};
    return {{ x: node.x + node.w * 0.5, y: node.y }};
  }}

  function buildBezier(p1, s1, p2, s2, factor) {{
    var d = Math.max(44, Math.min(180, (Math.abs(p2.x - p1.x) + Math.abs(p2.y - p1.y)) * (factor || 0.34)));
    var c1 = {{ x: p1.x, y: p1.y }}, c2 = {{ x: p2.x, y: p2.y }};
    if (s1 === 'r') c1.x += d; if (s1 === 'l') c1.x -= d; if (s1 === 'b') c1.y += d; if (s1 === 't') c1.y -= d;
    if (s2 === 'r') c2.x += d; if (s2 === 'l') c2.x -= d; if (s2 === 'b') c2.y += d; if (s2 === 't') c2.y -= d;
    var mx = 0.125 * p1.x + 0.375 * c1.x + 0.375 * c2.x + 0.125 * p2.x;
    var my = 0.125 * p1.y + 0.375 * c1.y + 0.375 * c2.y + 0.125 * p2.y;
    return {{ d: 'M ' + p1.x + ' ' + p1.y + ' C ' + c1.x + ' ' + c1.y + ', ' + c2.x + ' ' + c2.y + ', ' + p2.x + ' ' + p2.y, mx: mx, my: my }};
  }}

  function renderSections() {{
    sectionsLayer.innerHTML = SECTIONS.map(function(s) {{
      var cls = 'fx-section' + (s.isStart ? ' is-start' : '') + (s.isMobileSection ? ' is-mobile-sec' : '');
      return '<div class="' + cls + '" data-sec="' + esc(s.id) + '" data-flow="' + esc(s.flow) + '" ' +
        'style="left:' + s.x + 'px;top:' + s.y + 'px;width:' + s.w + 'px;height:' + s.h + 'px;--sec-accent:' + esc(s.accent || '#38BDF8') + '">' +
        '<span class="fx-sec-label">' + esc(s.label) + '</span></div>';
    }}).join('');
  }}

  function renderNodes() {{
    nodesLayer.innerHTML = NODES.map(function(n) {{
      var vw = n.vw || (n.platform === 'mobile' ? 390 : 1440);
      var vh = n.vh || (n.platform === 'mobile' ? 844 : 900);
      var previewW = n.w - 16;
      var previewH = n.h - 86;
      var scale = previewW / vw;
      var iframeH = Math.ceil(previewH / scale);
      var isStart = n.isStart || n.id === START_ID;
      var pill = isStart ? '★ Início' : (n.badge || n.platform || 'desktop');
      return '<article class="fx-node' + (isStart ? ' is-start' : '') + '" data-id="' + esc(n.id) + '" data-flow="' + esc(n.flow) + '" ' +
        'style="left:' + n.x + 'px;top:' + n.y + 'px;width:' + n.w + 'px;height:' + n.h + 'px">' +
        '<div class="fx-node-head">' +
          '<div class="fx-node-titles">' +
            '<span class="fx-node-name">' + esc(n.title) + '</span>' +
            '<span class="fx-node-file">' + esc(n.file) + '</span>' +
          '</div>' +
          '<a class="da-btn da-btn--icon" style="min-height:30px;width:30px" href="' + esc(n.file) + '" title="Abrir tela" onclick="event.stopPropagation()">' + DA_ICONS.arrowUpRight + '</a>' +
        '</div>' +
        '<div class="fx-preview" data-preview="' + esc(n.id) + '" data-src="' + esc(n.file) + '" data-vw="' + vw + '" data-vh="' + iframeH + '" data-scale="' + scale.toFixed(4) + '">' +
          '<div class="fx-schematic">' +
            '<span style="font-family:var(--da-font-mono);font-size:11.5px;color:var(--text-muted)">' + esc(n.group) + '</span>' +
            '<strong class="tabular-nums" style="font-size:13px">' + esc(n.metric) + '</strong>' +
          '</div>' +
        '</div>' +
        '<div class="fx-node-foot">' +
          '<span class="fx-node-metric tabular-nums">' + esc(n.metric) + '</span>' +
          '<span class="fx-node-pill">' + esc(pill) + '</span>' +
        '</div>' +
      '</article>';
    }}).join('');

    var mxS = 204 / WORLD_W, myS = 132 / WORLD_H;
    miniNodes.innerHTML = NODES.map(function(n) {{
      return '<div class="fx-mini-node" style="left:' + (n.x * mxS) + 'px;top:' + (n.y * myS) + 'px;width:' + Math.max(5, n.w * mxS) + 'px;height:' + Math.max(4, n.h * myS) + 'px;background:' + esc(n.accent || '#38BDF8') + '"></div>';
    }}).join('');
  }}

  function renderEdges() {{
    var colors = {{}};
    EDGES.forEach(function(e) {{ colors[e.color || '#38BDF8'] = true; }});
    var defs = '<defs>' + Object.keys(colors).map(function(c) {{
      var id = 'arr-' + c.replace(/[^a-zA-Z0-9]/g, '');
      return '<marker id="' + id + '" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M1,1.2 L7.8,4.5 L1,7.8 L2.6,4.5 Z" fill="' + c + '"></path></marker>';
    }}).join('') + '</defs>';
    var paths = defs, badges = '';
    EDGES.forEach(function(e) {{
      var n1 = nodeMap[e.from], n2 = nodeMap[e.to];
      if (!n1 || !n2) return;
      var col = e.color || '#38BDF8';
      var tier = e.tier || 'primary';
      var bz = buildBezier(anchorPoint(n1, e.fromSide || 'r'), e.fromSide || 'r', anchorPoint(n2, e.toSide || 'l'), e.toSide || 'l', e.curve);
      paths += '<path class="fx-edge-path' + (e.dashed ? ' is-dashed' : '') + '" data-edge="' + esc(e.id) + '" data-tier="' + esc(tier) + '" data-from="' + esc(e.from) + '" data-to="' + esc(e.to) + '" data-flow="' + esc(e.flow) + '" d="' + bz.d + '" stroke="' + col + '" marker-end="url(#arr-' + col.replace(/[^a-zA-Z0-9]/g, '') + ')"></path>';
      if (e.label) {{
        badges += '<button type="button" class="fx-edge-badge" data-edge-badge="' + esc(e.id) + '" data-tier="' + esc(tier) + '" data-from="' + esc(e.from) + '" data-to="' + esc(e.to) + '" data-target="' + esc(e.to) + '" style="left:' + bz.mx + 'px;top:' + bz.my + 'px;--edge-color:' + col + '">' + esc(e.label) + '</button>';
      }}
    }});
    edgesSvg.innerHTML = paths;
    badgesLayer.innerHTML = badges;
  }}

  var previewTimer = null;
  function syncLivePreviews() {{
    if (previewTimer) {{ clearTimeout(previewTimer); previewTimer = null; }}
    var boxes = Array.prototype.slice.call(document.querySelectorAll('.fx-preview'));
    if (!state.livePreview) {{
      boxes.forEach(function(b) {{ var f = b.querySelector('iframe'); if (f) f.remove(); }});
      return;
    }}
    var idx = 0;
    function nextBatch() {{
      if (!state.livePreview || idx >= boxes.length) return;
      for (var k = 0; k < 2 && idx < boxes.length; k++, idx++) {{
        var box = boxes[idx];
        if (box.querySelector('iframe')) continue;
        var ifr = document.createElement('iframe');
        ifr.className = 'fx-preview-frame';
        ifr.setAttribute('tabindex', '-1');
        ifr.setAttribute('aria-hidden', 'true');
        ifr.setAttribute('loading', 'lazy');
        ifr.style.width = box.dataset.vw + 'px';
        ifr.style.height = box.dataset.vh + 'px';
        ifr.style.transform = 'scale(' + box.dataset.scale + ')';
        ifr.addEventListener('load', (function(el) {{
          return function() {{
            el.classList.add('is-loaded');
            try {{
              if (el.contentDocument && el.contentDocument.documentElement) {{
                el.contentDocument.documentElement.setAttribute('data-theme', daGetTheme());
              }}
            }} catch (err) {{}}
          }};
        }})(ifr));
        ifr.src = box.dataset.src;
        box.appendChild(ifr);
      }}
      previewTimer = setTimeout(nextBatch, 90);
    }}
    nextBatch();
  }}

  function applyTransform() {{
    world.style.transform = 'translate(' + state.x + 'px, ' + state.y + 'px) scale(' + state.scale + ')';
    zoomVal.textContent = Math.round(state.scale * 100) + '%';
    var rect = stage.getBoundingClientRect();
    var mxS = 204 / WORLD_W, myS = 132 / WORLD_H;
    miniVp.style.left = Math.max(0, Math.min(194, (-state.x / state.scale) * mxS)) + 'px';
    miniVp.style.top = Math.max(0, Math.min(122, (-state.y / state.scale) * myS)) + 'px';
    miniVp.style.width = Math.max(12, Math.min(204, (rect.width / state.scale) * mxS)) + 'px';
    miniVp.style.height = Math.max(10, Math.min(132, (rect.height / state.scale) * myS)) + 'px';
  }}

  function fitBox(minX, minY, maxX, maxY, minScale) {{
    var rect = stage.getBoundingClientRect();
    var bw = Math.max(400, maxX - minX), bh = Math.max(300, maxY - minY);
    var leftReserve = rect.width > 1100 ? 344 : 24;
    var rightReserve = rect.width > 1100 ? 228 : 24;
    var availW = Math.max(260, rect.width - leftReserve - rightReserve);
    var availH = Math.max(240, rect.height - 84);
    var s = Math.max(minScale || 0.25, Math.min(1.05, Math.min(availW / bw, availH / bh)));
    state.scale = s;
    state.x = Math.round(leftReserve + (availW - bw * s) / 2 - minX * s);
    state.y = Math.round((rect.height - bh * s) / 2 - minY * s);
    applyTransform();
  }}

  function fitAll() {{
    var minX = Infinity, minY = Infinity, maxX = 0, maxY = 0;
    NODES.forEach(function(n) {{
      minX = Math.min(minX, n.x - 40); minY = Math.min(minY, n.y - 40);
      maxX = Math.max(maxX, n.x + n.w + 40); maxY = Math.max(maxY, n.y + n.h + 40);
    }});
    fitBox(minX, minY, maxX, maxY, 0.24);
  }}

  function fitFlow(flow) {{
    var targets = flow === 'all' ? NODES : NODES.filter(function(n) {{ return n.flow === flow; }});
    if (!targets.length) return fitAll();
    var minX = Infinity, minY = Infinity, maxX = 0, maxY = 0;
    targets.forEach(function(n) {{
      minX = Math.min(minX, n.x - 40); minY = Math.min(minY, n.y - 40);
      maxX = Math.max(maxX, n.x + n.w + 40); maxY = Math.max(maxY, n.y + n.h + 40);
    }});
    fitBox(minX, minY, maxX, maxY, 0.32);
  }}

  function centerNode(id, targetScale) {{
    var n = nodeMap[id];
    if (!n) return;
    var rect = stage.getBoundingClientRect();
    state.scale = targetScale || Math.max(state.scale, 0.74);
    state.x = Math.round(rect.width * 0.56 - (n.x + n.w * 0.5) * state.scale);
    state.y = Math.round(rect.height * 0.46 - (n.y + n.h * 0.5) * state.scale);
    applyTransform();
  }}

  function updateHighlights() {{
    var flow = state.activeFlow, sel = state.selectedId, iso = state.isolate;
    var conn = {{}}, hl = {{}}, selEdge = {{}};
    if (sel) {{
      EDGES.forEach(function(e) {{ if (e.from === sel || e.to === sel) selEdge[e.id] = true; }});
    }}
    if (flow !== 'all') {{
      NODES.forEach(function(n) {{ if (n.flow === flow) conn[n.id] = true; }});
      EDGES.forEach(function(e) {{ if (e.flow === flow || (conn[e.from] && conn[e.to])) hl[e.id] = true; }});
    }} else if (sel && iso) {{
      conn[sel] = true;
      EDGES.forEach(function(e) {{ if (e.from === sel || e.to === sel) {{ hl[e.id] = true; conn[e.from] = true; conn[e.to] = true; }} }});
    }}
    var dimMode = flow !== 'all' || (!!sel && iso);
    document.querySelectorAll('.fx-section').forEach(function(el) {{
      el.classList.toggle('is-dim', flow !== 'all' && el.dataset.flow !== flow);
    }});
    document.querySelectorAll('.fx-node').forEach(function(el) {{
      el.classList.toggle('is-selected', el.dataset.id === sel);
      el.classList.toggle('is-dim', dimMode && !conn[el.dataset.id]);
    }});
    document.querySelectorAll('.fx-edge-path').forEach(function(el) {{
      var eid = el.dataset.edge;
      var isPrimary = el.dataset.tier !== 'secondary';
      var visible = state.showAllEdges || isPrimary || !!hl[eid] || (!!sel && iso && !!selEdge[eid]);
      el.classList.toggle('is-hidden', !visible);
      el.classList.toggle('is-hl', !!hl[eid]);
      el.classList.toggle('is-dim', dimMode && !hl[eid]);
    }});
    document.querySelectorAll('.fx-edge-badge').forEach(function(el) {{
      var eid = el.dataset.edgeBadge;
      var isPrimary = el.dataset.tier !== 'secondary';
      var showBadge = (state.isolate && !!hl[eid]) || (flow !== 'all' && !!hl[eid]) || (state.showAllEdges && EDGES.length <= 24) || (isPrimary && !dimMode && NODES.length <= 24);
      el.classList.toggle('is-hidden', !showBadge);
      el.classList.toggle('is-dim', dimMode && !hl[eid]);
    }});
    document.getElementById('btnIsolate').classList.toggle('is-on', state.isolate);
    if (btnEdgesMode) {{
      btnEdgesMode.classList.toggle('is-on', state.showAllEdges);
      btnEdgesMode.textContent = state.showAllEdges ? 'Todas setas' : 'Setas';
    }}
  }}

  function updateInspector(id) {{
    var n = nodeMap[id] || NODES[0];
    if (!n) return;
    document.getElementById('inspMeta').textContent = (n.group || '') + ' · ' + (n.platform || 'desktop');
    document.getElementById('inspTitle').textContent = n.title;
    document.getElementById('inspDesc').textContent = n.desc || '';
    var outE = EDGES.filter(function(e) {{ return e.from === n.id && nodeMap[e.to]; }});
    var inE = EDGES.filter(function(e) {{ return e.to === n.id && nodeMap[e.from]; }});
    document.getElementById('inspOutWrap').style.display = outE.length ? '' : 'none';
    document.getElementById('inspInWrap').style.display = inE.length ? '' : 'none';
    document.getElementById('inspOut').innerHTML = outE.map(function(e) {{
      var d = nodeMap[e.to];
      return '<button type="button" class="fx-hop" data-jump="' + esc(d.id) + '"><span>' + esc(d.title) + '</span><small>' + esc(e.label) + '</small></button>';
    }}).join('');
    document.getElementById('inspIn').innerHTML = inE.map(function(e) {{
      var s = nodeMap[e.from];
      return '<button type="button" class="fx-hop" data-jump="' + esc(s.id) + '"><span>' + esc(s.title) + '</span><small>' + esc(e.label) + '</small></button>';
    }}).join('');
    document.getElementById('btnOpenFull').href = n.file;
    document.getElementById('btnModalPreview').dataset.id = n.id;
  }}

  function selectNode(id, center, iso) {{
    state.selectedId = id;
    if (typeof iso === 'boolean') state.isolate = iso;
    updateInspector(id);
    updateHighlights();
    if (center) centerNode(id);
  }}

  function openModal(id) {{
    var n = nodeMap[id] || NODES[0];
    if (!n) return;
    var m = document.getElementById('previewModal');
    var wrap = document.getElementById('modalWrap');
    var ifr = document.getElementById('modalIframe');
    document.getElementById('modalTitle').textContent = n.title;
    document.getElementById('modalFile').textContent = n.file;
    document.getElementById('modalNewTab').href = n.file;
    wrap.classList.toggle('is-mobile', n.platform === 'mobile');
    ifr.src = n.file;
    m.hidden = false;
  }}

  function closeModal() {{
    document.getElementById('previewModal').hidden = true;
    document.getElementById('modalIframe').src = 'about:blank';
  }}

  var panning = false, moved = false, sx = 0, sy = 0, ox = 0, oy = 0;
  stage.addEventListener('pointerdown', function(e) {{
    if (e.target.closest('.fx-inspector, .fx-hud, .fx-edge-badge, .fx-node')) return;
    panning = true; moved = false; sx = e.clientX; sy = e.clientY; ox = state.x; oy = state.y;
    stage.classList.add('is-panning'); stage.setPointerCapture(e.pointerId);
  }});
  stage.addEventListener('pointermove', function(e) {{
    if (!panning) return;
    var dx = e.clientX - sx, dy = e.clientY - sy;
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) moved = true;
    state.x = ox + dx; state.y = oy + dy; applyTransform();
  }});
  stage.addEventListener('pointerup', function() {{ panning = false; stage.classList.remove('is-panning'); }});
  stage.addEventListener('wheel', function(e) {{
    if (e.target.closest('.fx-inspector')) return;
    e.preventDefault();
    var rect = stage.getBoundingClientRect(), cx = e.clientX - rect.left, cy = e.clientY - rect.top;
    var next = Math.max(0.22, Math.min(1.5, state.scale * (e.deltaY < 0 ? 1.1 : 0.91)));
    var ratio = next / state.scale;
    state.x = cx - (cx - state.x) * ratio; state.y = cy - (cy - state.y) * ratio; state.scale = next;
    applyTransform();
  }}, {{ passive: false }});

  nodesLayer.addEventListener('click', function(e) {{
    var card = e.target.closest('.fx-node');
    if (!card) return;
    selectNode(card.dataset.id, false, state.selectedId === card.dataset.id ? !state.isolate : true);
  }});
  nodesLayer.addEventListener('dblclick', function(e) {{
    var card = e.target.closest('.fx-node');
    if (card) openModal(card.dataset.id);
  }});
  badgesLayer.addEventListener('click', function(e) {{
    var b = e.target.closest('.fx-edge-badge');
    if (b) selectNode(b.dataset.target, true, true);
  }});
  document.getElementById('inspector').addEventListener('click', function(e) {{
    var hop = e.target.closest('[data-jump]');
    if (hop) selectNode(hop.dataset.jump, true, true);
  }});
  document.querySelectorAll('.fx-flow-btn').forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      state.activeFlow = btn.dataset.flow; state.isolate = false;
      document.querySelectorAll('.fx-flow-btn').forEach(function(b) {{ b.classList.toggle('is-active', b === btn); }});
      updateHighlights();
      fitFlow(state.activeFlow);
    }});
  }});
  document.getElementById('btnJumpStart').addEventListener('click', function() {{
    state.activeFlow = 'all'; state.isolate = false;
    document.querySelectorAll('.fx-flow-btn').forEach(function(b) {{ b.classList.toggle('is-active', b.dataset.flow === 'all'); }});
    selectNode(START_ID, false, false);
    centerNode(START_ID, 0.72);
  }});
  var btnMob = document.getElementById('btnJumpMobile');
  if (btnMob) {{
    btnMob.addEventListener('click', function() {{
      var mobNodes = NODES.filter(function(n) {{ return n.platform === 'mobile'; }});
      if (!mobNodes.length) return;
      var minX = Infinity, minY = Infinity, maxX = 0, maxY = 0;
      mobNodes.forEach(function(n) {{
        minX = Math.min(minX, n.x - 40); minY = Math.min(minY, n.y - 40);
        maxX = Math.max(maxX, n.x + n.w + 40); maxY = Math.max(maxY, n.y + n.h + 40);
      }});
      state.activeFlow = mobNodes[0].flow; state.isolate = false;
      document.querySelectorAll('.fx-flow-btn').forEach(function(b) {{ b.classList.toggle('is-active', b.dataset.flow === state.activeFlow); }});
      updateHighlights();
      fitBox(minX, minY, maxX, maxY, 0.38);
    }});
  }}
  if (btnEdgesMode) {{
    btnEdgesMode.addEventListener('click', function() {{ state.showAllEdges = !state.showAllEdges; updateHighlights(); }});
  }}
  document.getElementById('btnIsolate').addEventListener('click', function() {{ state.isolate = !state.isolate; updateHighlights(); }});
  document.getElementById('btnToggleInsp').addEventListener('click', function() {{
    var c = document.getElementById('inspector').classList.toggle('is-collapsed');
    this.textContent = c ? 'Expandir' : 'Recolher';
  }});
  document.getElementById('btnModalPreview').addEventListener('click', function() {{ openModal(this.dataset.id || state.selectedId); }});
  document.getElementById('btnCloseModal').addEventListener('click', closeModal);
  document.getElementById('btnLive').addEventListener('click', function() {{
    state.livePreview = !state.livePreview; this.classList.toggle('is-on', state.livePreview); syncLivePreviews();
  }});
  document.getElementById('btnZoomIn').addEventListener('click', function() {{ state.scale = Math.min(1.5, state.scale * 1.18); applyTransform(); }});
  document.getElementById('btnZoomOut').addEventListener('click', function() {{ state.scale = Math.max(0.22, state.scale * 0.84); applyTransform(); }});
  document.getElementById('btnFit').addEventListener('click', fitAll);
  minimap.addEventListener('click', function(e) {{
    var r = minimap.getBoundingClientRect(), sr = stage.getBoundingClientRect();
    var wx = ((e.clientX - r.left) / 204) * WORLD_W, wy = ((e.clientY - r.top) / 132) * WORLD_H;
    state.x = sr.width / 2 - wx * state.scale; state.y = sr.height / 2 - wy * state.scale; applyTransform();
  }});
  document.addEventListener('designaura:themechange', function(e) {{
    var th = e.detail && e.detail.theme ? e.detail.theme : 'dark';
    document.querySelectorAll('iframe').forEach(function(ifr) {{
      try {{ if (ifr.contentDocument && ifr.contentDocument.documentElement) ifr.contentDocument.documentElement.setAttribute('data-theme', th); }} catch (err) {{}}
    }});
  }});
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape' && !document.getElementById('previewModal').hidden) closeModal();
    if (e.key === 'f' || e.key === 'F') fitAll();
    if (e.key === 'h' || e.key === 'H') centerNode(START_ID, 0.72);
    if (e.key === 'e' || e.key === 'E') {{ state.showAllEdges = !state.showAllEdges; updateHighlights(); }}
    if (e.key === 'i' || e.key === 'I') {{ state.isolate = !state.isolate; updateHighlights(); }}
    if (e.key === 't' || e.key === 'T') daToggleTheme();
  }});

  renderSections(); renderNodes(); renderEdges();
  updateInspector(state.selectedId); updateHighlights();
  if (window.innerWidth <= 768) {{
    document.getElementById('inspector').classList.add('is-collapsed');
    document.getElementById('btnToggleInsp').textContent = 'Expandir';
    centerNode(state.selectedId, 0.78);
  }} else {{
    fitAll();
  }}
  syncLivePreviews();
}})();
</script>
</body>
</html>
"""


def render_preview_html(manifest: dict, tokens_link: str, parsed_tokens: dict[str, dict[str, str]] | None = None) -> str:
    proj = manifest.get("project", {})
    name = html.escape(proj.get("name", "Projeto Design Aura"))
    default_theme = html.escape(proj.get("defaultTheme", "dark"))
    start_id = proj.get("startScreenId") or manifest["screens"][0]["id"]
    head_css = build_base_css(manifest, tokens_link, parsed_tokens)
    manifest_json = json.dumps(manifest, ensure_ascii=False)

    journeys = manifest.get("journeys") or [
        {"id": "padrao", "name": "Fluxo Geral", "steps": [{"screenId": s["id"], "short": s["title"], "title": s["title"], "tip": s.get("desc", "")} for s in manifest["screens"][:5]]}
    ]
    use_select = len(journeys) >= 4 or sum(len(str(j.get("name", ""))) for j in journeys) > 54
    if use_select:
        opts = []
        for idx, j in enumerate(journeys):
            sel = " selected" if idx == 0 else ""
            opts.append(f'<option value="{idx}" data-journey="{html.escape(j["id"])}"{sel}>{html.escape(j["name"])}</option>')
        journeys_control = (
            '<div class="pv-journey-picker">'
            '  <label class="pv-jlabel" for="journeySelect">Jornada</label>'
            f'  <select class="pv-jselect" id="journeySelect" aria-label="Selecionar jornada">{"".join(opts)}</select>'
            '</div>'
        )
    else:
        j_buttons = []
        for idx, j in enumerate(journeys):
            cls = "pv-jbtn is-active" if idx == 0 else "pv-jbtn"
            j_buttons.append(f'<button type="button" class="{cls}" data-journey="{html.escape(j["id"])}">{html.escape(j["name"])}</button>')
        journeys_control = f'<div class="pv-journeys" role="group" aria-label="Jornadas">{"".join(j_buttons)}</div>'

    return f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="{default_theme}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preview Guiado · {name}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap">
<script>{THEME_BOOT_JS}</script>
{head_css}
<style>
  html, body {{ height: 100%; overflow: hidden; }}
  .pv-app {{ display: flex; flex-direction: column; height: 100dvh; width: 100vw; overflow: hidden; background: var(--surface-z0); }}
  .pv-top {{
    display: flex; align-items: center; justify-content: space-between; gap: 10px; min-height: 56px; padding: 6px 14px;
    background: var(--surface-glass); border-bottom: 1.25px solid var(--border-card);
  }}
  .pv-left, .pv-right {{ display: flex; align-items: center; gap: 6px; flex: none; }}
  .pv-crumb {{
    display: inline-flex; align-items: center; gap: 6px; height: 36px; max-width: 260px; padding: 0 12px; border-radius: 9px;
    background: var(--surface-z0); border: 1px solid var(--border-card); font-family: var(--da-font-mono); font-size: 12px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .pv-crumb strong {{ color: var(--text-strong); overflow: hidden; text-overflow: ellipsis; }}
  .pv-journeys {{
    display: flex; align-items: center; gap: 4px; padding: 3px; border-radius: 10px;
    background: var(--surface-z0); border: 1px solid var(--border-card); flex: 0 1 auto; min-width: 0;
    overflow-x: auto; scrollbar-width: none; justify-content: flex-start;
  }}
  .pv-journeys::-webkit-scrollbar {{ display: none; }}
  .pv-jbtn {{
    min-height: 34px; padding: 0 11px; border-radius: 7px; border: 1px solid transparent; background: transparent;
    color: var(--text-body); font-family: var(--da-font-ui); font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; flex: none;
  }}
  .pv-jbtn.is-active {{ background: var(--surface-z2); color: var(--text-strong); border-color: var(--border-strong); box-shadow: var(--shadow-z1); }}
  .pv-journey-picker {{
    display: inline-flex; align-items: center; gap: 8px; flex: 0 1 420px; min-width: 0;
    padding: 3px 4px 3px 12px; border-radius: 10px; background: var(--surface-z0); border: 1px solid var(--border-card);
  }}
  .pv-jlabel {{ font-family: var(--da-font-mono); font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; flex: none; }}
  .pv-jselect {{
    flex: 1 1 auto; min-width: 0; height: 34px; padding: 0 28px 0 10px; border-radius: 7px;
    border: 1px solid var(--border-strong); background: var(--surface-z2); color: var(--text-strong);
    font-family: var(--da-font-ui); font-size: 12.5px; font-weight: 600; cursor: pointer;
    box-shadow: var(--shadow-z1); text-overflow: ellipsis;
  }}
  .pv-stage {{ flex: 1 1 auto; min-height: 0; display: flex; align-items: center; justify-content: center; padding: 0; background: var(--surface-z0); overflow: hidden; }}
  .pv-frame-wrap {{ width: 100%; height: 100%; overflow: hidden; background: var(--surface-z1); isolation: isolate; }}
  .pv-frame-wrap.is-mobile {{
    width: 390px; height: min(844px, calc(100% - 20px)); border-radius: 40px; border: 8px solid #141923;
    outline: 1.5px solid var(--border-strong); box-shadow: 0 24px 60px -12px rgba(0, 0, 0, 0.55);
    overflow: hidden; clip-path: inset(0 round 32px); transform: translateZ(0);
  }}
  .pv-iframe {{ width: 100%; height: 100%; display: block; border: 0; background: var(--surface-z1); }}
  .pv-guide {{
    display: flex; flex-direction: column; gap: 10px; padding: 12px 16px;
    background: var(--surface-glass); border-top: 1.25px solid var(--border-strong);
  }}
  .pv-guide.is-min .pv-guide-main {{ display: none; }}
  .pv-steps-row {{ display: flex; align-items: center; gap: 6px; overflow-x: auto; scrollbar-width: none; }}
  .pv-steps-row::-webkit-scrollbar {{ display: none; }}
  .pv-step-pill {{
    display: inline-flex; align-items: center; gap: 6px; min-height: 36px; padding: 0 13px; border-radius: 999px;
    border: 1px solid var(--border-card); background: var(--surface-z2); color: var(--text-body); font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap;
  }}
  .pv-step-pill.is-now {{ background: var(--da-accent-deep); border-color: var(--da-accent-deep); color: #FFFFFF; }}
  .pv-guide-main {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
  @media (max-width: 768px) {{
    .pv-top {{ flex-wrap: wrap; gap: 6px; padding: 8px 10px; }}
    .pv-crumb {{ display: none; }}
    .pv-journeys, .pv-journey-picker {{ order: 3; flex: 1 0 100%; }}
    .pv-jbtn, .pv-jselect, .pv-step-pill {{ min-height: 44px; }}
    .pv-right {{ margin-left: auto; }}
  }}
</style>
</head>
<body>
<div class="pv-app">
  <header class="pv-top">
    <div class="pv-left">
      <button type="button" class="da-btn da-btn--icon" id="btnBack" aria-label="Voltar" disabled></button>
      <button type="button" class="da-btn da-btn--icon" id="btnHome" aria-label="Início"></button>
      <span class="pv-crumb" id="breadcrumb"></span>
    </div>
    {journeys_control}
    <div class="pv-right">
      <a class="da-btn" id="btnPure" href="#">Abrir Pura</a>
      <a class="da-btn" href="fluxo.html">Mapa Figma</a>
      <a class="da-btn" href="index.html">Galeria</a>
      <button type="button" class="da-btn da-btn--icon" id="btnThemeToggle" aria-label="Alternar tema" onclick="daToggleTheme()"></button>
    </div>
  </header>

  <main class="pv-stage">
    <div class="pv-frame-wrap" id="stageWrap">
      <iframe class="pv-iframe" id="stageFrame" title="Tela do sistema"></iframe>
    </div>
  </main>

  <footer class="pv-guide" id="guideDock">
    <div class="pv-steps-row" id="stepsRow"></div>
    <div class="pv-guide-main">
      <div>
        <strong id="narTitle" style="color:var(--text-strong);font-size:14px;"></strong>
        <p id="narDesc" style="margin:4px 0 0;font-size:13px;color:var(--text-body);"></p>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        <button type="button" class="da-btn" id="btnPrev">Anterior</button>
        <button type="button" class="da-btn da-btn--primary" id="btnNext">Próximo</button>
      </div>
    </div>
  </footer>
</div>

<script>
{ICONS_JS}
{THEME_TOGGLE_JS}
(function() {{
  var MANIFEST = {manifest_json};
  var SCREENS = MANIFEST.screens || [];
  var JOURNEYS = {json.dumps(journeys, ensure_ascii=False)};
  var screenMap = {{}};
  SCREENS.forEach(function(s) {{ screenMap[s.id] = s; }});

  document.getElementById('btnBack').innerHTML = DA_ICONS.arrowLeft;
  document.getElementById('btnHome').innerHTML = DA_ICONS.home;
  document.getElementById('btnThemeToggle').innerHTML = daGetTheme() === 'dark' ? DA_ICONS.sun : DA_ICONS.moon;

  var state = {{ journeyIdx: 0, stepIdx: 0, history: ['{html.escape(start_id)}'], currentId: '{html.escape(start_id)}', minimized: false }};
  var frameWrap = document.getElementById('stageWrap');
  var frame = document.getElementById('stageFrame');
  var journeySelect = document.getElementById('journeySelect');

  function esc(str) {{
    return String(str == null ? '' : str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}

  function loadScreen(id, push) {{
    var s = screenMap[id] || SCREENS[0];
    state.currentId = s.id;
    if (push !== false && state.history[state.history.length - 1] !== s.id) state.history.push(s.id);
    frameWrap.classList.toggle('is-mobile', s.platform === 'mobile');
    frame.src = s.file;
    document.getElementById('breadcrumb').innerHTML = '<span>' + esc(s.group) + '</span> <strong>' + esc(s.title) + '</strong>';
    document.getElementById('btnPure').href = s.file;
    document.getElementById('btnBack').disabled = state.history.length <= 1;
    renderGuide();
  }}

  function renderGuide() {{
    var j = JOURNEYS[state.journeyIdx];
    var steps = j.steps || [];
    var cur = steps[state.stepIdx] || steps[0] || {{ title: '', tip: '' }};
    var htmlStr = steps.map(function(st, i) {{
      return '<button type="button" class="pv-step-pill' + (i === state.stepIdx ? ' is-now' : '') + '" data-step="' + i + '"><span class="tabular-nums">' + (i + 1) + '.</span> ' + esc(st.short) + '</button>';
    }}).join('') + '<button type="button" class="da-btn da-btn--sm" id="btnMin" style="margin-left:auto">' + (state.minimized ? 'Mostrar roteiro' : 'Recolher') + '</button>';
    document.getElementById('stepsRow').innerHTML = htmlStr;
    document.getElementById('narTitle').textContent = 'Passo ' + (state.stepIdx + 1) + '/' + steps.length + ' · ' + cur.title;
    document.getElementById('narDesc').textContent = cur.tip || '';
    document.getElementById('btnPrev').disabled = state.stepIdx <= 0;
    document.getElementById('btnNext').textContent = state.stepIdx >= steps.length - 1 ? 'Voltar ao Início' : 'Próximo: ' + steps[state.stepIdx + 1].short;
    document.querySelectorAll('.pv-jbtn').forEach(function(b, i) {{ b.classList.toggle('is-active', i === state.journeyIdx); }});
    if (journeySelect) journeySelect.value = String(state.journeyIdx);
  }}

  frame.addEventListener('load', function() {{
    try {{
      var th = daGetTheme();
      if (frame.contentDocument && frame.contentDocument.documentElement) {{
        frame.contentDocument.documentElement.setAttribute('data-theme', th);
      }}
      var path = frame.contentWindow.location.pathname.split('/').pop();
      var found = SCREENS.find(function(s) {{ return s.file === path; }});
      if (found && found.id !== state.currentId) {{
        state.currentId = found.id;
        frameWrap.classList.toggle('is-mobile', found.platform === 'mobile');
        document.getElementById('breadcrumb').innerHTML = '<span>' + esc(found.group) + '</span> <strong>' + esc(found.title) + '</strong>';
        document.getElementById('btnPure').href = found.file;
      }}
    }} catch (err) {{}}
  }});

  document.addEventListener('designaura:themechange', function(e) {{
    try {{ if (frame.contentDocument && frame.contentDocument.documentElement) frame.contentDocument.documentElement.setAttribute('data-theme', e.detail.theme); }} catch (err) {{}}
  }});

  document.querySelectorAll('.pv-jbtn').forEach(function(btn, idx) {{
    btn.addEventListener('click', function() {{
      state.journeyIdx = idx; state.stepIdx = 0;
      loadScreen(JOURNEYS[idx].steps[0].screenId, true);
    }});
  }});
  if (journeySelect) {{
    journeySelect.addEventListener('change', function() {{
      var idx = Number(this.value) || 0;
      state.journeyIdx = idx; state.stepIdx = 0;
      loadScreen(JOURNEYS[idx].steps[0].screenId, true);
    }});
  }}

  document.getElementById('stepsRow').addEventListener('click', function(e) {{
    if (e.target.closest('#btnMin')) {{
      state.minimized = !state.minimized;
      document.getElementById('guideDock').classList.toggle('is-min', state.minimized);
      renderGuide();
      return;
    }}
    var p = e.target.closest('[data-step]');
    if (!p) return;
    state.stepIdx = Number(p.dataset.step);
    loadScreen(JOURNEYS[state.journeyIdx].steps[state.stepIdx].screenId, true);
  }});

  document.getElementById('btnBack').addEventListener('click', function() {{
    if (state.history.length <= 1) return;
    state.history.pop();
    loadScreen(state.history[state.history.length - 1], false);
  }});
  document.getElementById('btnHome').addEventListener('click', function() {{ loadScreen('{html.escape(start_id)}', true); }});
  document.getElementById('btnPrev').addEventListener('click', function() {{
    if (state.stepIdx > 0) {{ state.stepIdx--; loadScreen(JOURNEYS[state.journeyIdx].steps[state.stepIdx].screenId, true); }}
  }});
  document.getElementById('btnNext').addEventListener('click', function() {{
    var steps = JOURNEYS[state.journeyIdx].steps;
    if (state.stepIdx < steps.length - 1) {{ state.stepIdx++; loadScreen(steps[state.stepIdx].screenId, true); }}
    else {{ state.stepIdx = 0; loadScreen(steps[0].screenId, true); }}
  }});

  var params = new URLSearchParams(location.search);
  var journeyKey = params.get('j');
  if (journeyKey) {{
    var journeyIdx = JOURNEYS.findIndex(function(j) {{ return j.id === journeyKey; }});
    if (journeyIdx >= 0) state.journeyIdx = journeyIdx;
  }}
  var initialId = JOURNEYS[state.journeyIdx].steps[0].screenId;
  if (params.get('screen') && screenMap[params.get('screen')]) initialId = params.get('screen');
  loadScreen(initialId, false);
}})();
</script>
</body>
</html>
"""


def _resolve_thumbnails(screens: list[dict], thumbs_dir: Path | None, out_dir: Path) -> dict[str, dict[str, str]]:
    """Localiza miniaturas PNG (dark/light) opcionais para cada tela na Galeria."""
    thumbs: dict[str, dict[str, str]] = {}
    for s in screens:
        sid = s["id"]
        if s.get("thumbnail"):
            thumbs[sid] = {"dark": str(s["thumbnail"]), "light": str(s.get("thumbnailLight") or s["thumbnail"])}
            continue
        if not thumbs_dir or not thumbs_dir.exists():
            continue
        stem = Path(s.get("file", "")).stem
        vp = "mobile" if s.get("platform") == "mobile" else "desktop"
        dark_cand = thumbs_dir / f"{stem}-{vp}-dark.png"
        light_cand = thumbs_dir / f"{stem}-{vp}-light.png"
        any_cand = thumbs_dir / f"{stem}.png"
        found_dark = dark_cand if dark_cand.exists() else (light_cand if light_cand.exists() else (any_cand if any_cand.exists() else None))
        found_light = light_cand if light_cand.exists() else found_dark
        if found_dark:
            try:
                d_rel = str(Path(os.path.relpath(found_dark, out_dir)).as_posix())
                l_rel = str(Path(os.path.relpath(found_light, out_dir)).as_posix())
            except ValueError:
                d_rel, l_rel = str(found_dark), str(found_light)
            thumbs[sid] = {"dark": d_rel, "light": l_rel}
    return thumbs


def render_index_html(
    manifest: dict,
    tokens_link: str,
    parsed_tokens: dict[str, dict[str, str]] | None = None,
    thumbs_map: dict[str, dict[str, str]] | None = None,
) -> str:
    proj = manifest.get("project", {})
    name = html.escape(proj.get("name", "Projeto Design Aura"))
    subtitle = html.escape(proj.get("subtitle", "Galeria de Telas e Navegação"))
    raw_version = str(proj.get("version") or "").strip()
    version_suffix = f" · v{html.escape(raw_version)}" if raw_version else ""
    default_theme = html.escape(proj.get("defaultTheme", "dark"))
    screens = manifest.get("screens", [])
    start_id = proj.get("startScreenId") or screens[0]["id"]
    start_screen = next((s for s in screens if s["id"] == start_id), screens[0])
    bible_link = proj.get("bibleLink", "")
    head_css = build_base_css(manifest, tokens_link, parsed_tokens)
    thumbs = thumbs_map or {}

    desktop_count = sum(1 for s in screens if s.get("platform") != "mobile")
    mobile_count = sum(1 for s in screens if s.get("platform") == "mobile")
    groups = []
    seen = set()
    for s in screens:
        g = s.get("flow", "geral")
        if g not in seen:
            seen.add(g)
            groups.append(g)

    filter_chips = [f'<button type="button" class="da-chip is-active" data-filter="all">Todas <span class="tabular-nums">{len(screens)}</span></button>']
    for g in groups:
        cnt = sum(1 for s in screens if s.get("flow") == g)
        lbl = _format_flow_label(g, manifest)
        filter_chips.append(f'<button type="button" class="da-chip" data-filter="{html.escape(g)}">{html.escape(lbl)} <span class="tabular-nums">{cnt}</span></button>')

    cards_html = []
    for s in screens:
        plat = "Mobile" if s.get("platform") == "mobile" else "Desktop"
        accent_bar = html.escape(s.get("accent") or "#38BDF8")
        tb = thumbs.get(s["id"])
        thumb_html = ""
        if tb:
            init_src = tb["light"] if default_theme == "light" else tb["dark"]
            mob_cls = " is-mobile-thumb" if s.get("platform") == "mobile" else ""
            thumb_html = (
                f'  <a class="g-card-thumb{mob_cls}" href="{html.escape(s["file"])}" tabindex="-1">'
                f'    <img src="{html.escape(init_src)}" data-thumb-dark="{html.escape(tb["dark"])}" data-thumb-light="{html.escape(tb["light"])}" '
                f'alt="Prévia de {html.escape(s["title"])}" loading="lazy">'
                f'  </a>'
            )
        cards_html.append(
            f'<article class="g-card" id="screen-{html.escape(s["id"])}" data-flow="{html.escape(s.get("flow", "geral"))}" data-title="{html.escape(s["title"].lower())}" style="--card-accent:{accent_bar}">'
            f'{thumb_html}'
            f'  <div class="g-card-body">'
            f'    <div class="g-card-top"><span class="g-card-group">{html.escape(s.get("group", ""))}</span><span class="g-badge">{html.escape(plat)}</span></div>'
            f'    <h3 class="g-card-title">{html.escape(s["title"])}</h3>'
            f'    <p class="g-card-desc">{html.escape(s.get("desc", ""))}</p>'
            f'    <div class="g-card-foot">'
            f'      <span class="g-metric tabular-nums">{html.escape(s.get("metric", ""))}</span>'
            f'      <a class="da-btn da-btn--sm" href="{html.escape(s["file"])}">Abrir tela</a>'
            f'    </div>'
            f'  </div>'
            f'</article>'
        )

    bible_btn = f'<a class="da-btn" href="{html.escape(bible_link)}">Bíblia de Design</a>' if bible_link else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="{default_theme}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Galeria de Telas · {name}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap">
<script>{THEME_BOOT_JS}</script>
{head_css}
<style>
  .g-shell {{ min-height: 100dvh; display: flex; flex-direction: column; }}
  .g-topbar {{
    position: sticky; top: 0; z-index: 30; display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 10px 20px; background: var(--surface-glass); border-bottom: 1.25px solid var(--border-card);
  }}
  .g-brand {{ display: flex; align-items: center; gap: 12px; text-decoration: none; }}
  .g-brand-text {{ display: flex; flex-direction: column; }}
  .g-brand-text strong {{ font-family: var(--da-font-display); font-size: 15px; color: var(--text-strong); }}
  .g-brand-text span {{ font-family: var(--da-font-mono); font-size: 12px; color: var(--text-muted); }}
  .g-top-actions {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .g-main {{ max-width: 1320px; width: 100%; margin: 0 auto; padding: 24px 20px 48px; display: flex; flex-direction: column; gap: 24px; }}
  .g-hero {{
    border-radius: 20px; padding: 24px; background-color: var(--da-navy);
    background-image: linear-gradient(150deg, var(--da-navy) 0%, #163E70 100%); color: #F3F6FA;
    border: 1.5px solid var(--border-strong); box-shadow: var(--shadow-z2);
    display: flex; flex-direction: column; gap: 16px;
  }}
  .g-hero h1 {{ font-size: 32px; line-height: 1.15; color: #FFFFFF; max-width: 24ch; }}
  .g-hero p {{ margin: 0; max-width: 64ch; color: #D3DEEC; font-size: 15px; }}
  .g-hero-actions {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
  .g-hero-stats {{ display: flex; flex-wrap: wrap; gap: 20px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.16); }}
  .g-stat b {{ display: block; font-size: 20px; font-family: var(--da-font-mono); color: #FFFFFF; }}
  .g-stat span {{ font-size: 12px; color: #C2D4EA; }}

  .g-filters {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
  .da-chip {{
    display: inline-flex; align-items: center; gap: 6px; min-height: 44px; padding: 0 14px; border-radius: 999px;
    border: 1.25px solid var(--border-card); background: var(--surface-z2); color: var(--text-body);
    font-size: 13px; font-weight: 600; cursor: pointer;
    transition-property: background-color, border-color, color; transition-duration: 150ms;
  }}
  .da-chip.is-active {{ background: var(--da-accent-deep); border-color: var(--da-accent-deep); color: #FFFFFF; }}

  .g-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
  .g-card {{
    display: flex; flex-direction: column; border-radius: 16px; overflow: hidden;
    background: var(--surface-z2); border: 1.25px solid var(--border-card);
    border-top: 3px solid var(--card-accent, var(--da-navy)); box-shadow: var(--shadow-z1);
  }}
  .g-card[hidden] {{ display: none; }}
  .g-card-thumb {{
    display: block; aspect-ratio: 16 / 10; background: var(--surface-z0); border-bottom: 1px solid var(--border-card);
    overflow: hidden; position: relative;
  }}
  .g-card-thumb img {{ width: 100%; height: 100%; object-fit: cover; object-position: top center; display: block; }}
  .g-card-thumb.is-mobile-thumb {{ display: flex; align-items: center; justify-content: center; padding: 10px; }}
  .g-card-thumb.is-mobile-thumb img {{ width: auto; max-width: 100%; height: 100%; object-fit: contain; border-radius: 12px; box-shadow: var(--shadow-z1); }}
  .g-card-body {{ display: flex; flex-direction: column; gap: 12px; padding: 16px; flex: 1 1 auto; }}
  .g-card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
  .g-card-group {{ font-family: var(--da-font-mono); font-size: 12px; color: var(--text-muted); }}
  .g-badge {{ padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; background: var(--surface-z0); border: 1px solid var(--border-card); color: var(--text-strong); }}
  .g-card-title {{ font-size: 18px; line-height: 1.25; }}
  .g-card-desc {{ margin: 0; font-size: 14px; color: var(--text-body); flex: 1 1 auto; }}
  .g-card-foot {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-top: 8px; border-top: 1px solid var(--border-card); }}
  .g-metric {{ font-family: var(--da-font-mono); font-size: 12px; color: var(--text-muted); }}

  .cmdk-backdrop {{
    position: fixed; inset: 0; z-index: 80; display: flex; align-items: flex-start; justify-content: center;
    padding: 80px 16px 16px; background: rgba(8, 16, 24, 0.72);
  }}
  .cmdk-backdrop[hidden] {{ display: none !important; }}
  .cmdk-box {{
    width: 100%; max-width: 560px; border-radius: 16px; background: var(--surface-z2);
    border: 1.5px solid var(--border-strong); box-shadow: var(--shadow-z2); overflow: hidden;
  }}
  .cmdk-input-wrap {{ padding: 12px 16px; border-bottom: 1px solid var(--border-card); display: flex; align-items: center; gap: 10px; }}
  .cmdk-input {{
    flex: 1; border: 0; background: transparent; color: var(--text-strong); font-family: var(--da-font-ui); font-size: 15px;
  }}
  .cmdk-list {{ max-height: 360px; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 4px; }}
  .cmdk-item {{
    display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 10px 12px; min-height: 44px;
    border-radius: 8px; text-decoration: none; color: var(--text-strong); border: 1px solid transparent;
  }}
  .cmdk-item:hover, .cmdk-item.is-focus {{ background: var(--surface-z0); border-color: var(--border-strong); }}
</style>
</head>
<body>
<div class="g-shell">
  <header class="g-topbar">
    <a class="g-brand" href="index.html">
      <div class="g-brand-text">
        <strong>{name}</strong>
        <span>{subtitle}{version_suffix}</span>
      </div>
    </a>
    <div class="g-top-actions">
      <button type="button" class="da-btn" id="btnCmdk">Buscar telas <kbd style="font-family:var(--da-font-mono);font-size:12px;">Cmd+K</kbd></button>
      <a class="da-btn" href="fluxo.html">Mapa Figma</a>
      {bible_btn}
      <button type="button" class="da-btn da-btn--icon" id="btnThemeToggle" aria-label="Alternar tema" onclick="daToggleTheme()"></button>
    </div>
  </header>

  <main class="g-main">
    <section class="g-hero">
      <h1>{name}: arquitetura navegável e telas conectadas.</h1>
      <p>Navegue pelo mapa infinito estilo Figma, percorra as jornadas guiadas de uso real ou abra diretamente cada tela em Desktop e Mobile.</p>
      <div class="g-hero-actions">
        <a class="da-btn da-btn--primary" href="preview.html">Iniciar Preview Guiado</a>
        <a class="da-btn" style="background:rgba(255,255,255,0.12);color:#FFFFFF;border-color:rgba(255,255,255,0.28)" href="fluxo.html">Mapa de Fluxo (Figma)</a>
        <a class="da-btn" style="background:rgba(255,255,255,0.12);color:#FFFFFF;border-color:rgba(255,255,255,0.28)" href="{html.escape(start_screen['file'])}">Abrir {html.escape(start_screen['title'])}</a>
      </div>
      <div class="g-hero-stats tabular-nums">
        <div class="g-stat"><b>{len(screens)}</b><span>Telas totais</span></div>
        <div class="g-stat"><b>{desktop_count}</b><span>Desktop / Sistema</span></div>
        <div class="g-stat"><b>{mobile_count}</b><span>Mobile</span></div>
        <div class="g-stat"><b>{len(manifest.get("edges", []))}</b><span>Conexões de fluxo</span></div>
      </div>
    </section>

    <div class="g-filters" role="group" aria-label="Filtrar telas">
      {"".join(filter_chips)}
    </div>

    <section class="g-grid" id="screenGrid" aria-label="Lista de telas">
      {"".join(cards_html)}
    </section>
  </main>
</div>

<div class="cmdk-backdrop" id="cmdkModal" hidden>
  <div class="cmdk-box" role="dialog" aria-label="Busca rápida de telas">
    <div class="cmdk-input-wrap">
      <label for="cmdkInput" style="font-size:12px;font-weight:600;color:var(--text-muted)">Ir para</label>
      <input class="cmdk-input" id="cmdkInput" type="search" placeholder="Digite o nome da tela ou módulo...">
      <button type="button" class="da-btn da-btn--sm" id="btnCmdkClose">Esc</button>
    </div>
    <div class="cmdk-list" id="cmdkList"></div>
  </div>
</div>

<script>
{ICONS_JS}
{THEME_TOGGLE_JS}
(function() {{
  var SCREENS = {json.dumps(screens, ensure_ascii=False)};
  document.getElementById('btnThemeToggle').innerHTML = daGetTheme() === 'dark' ? DA_ICONS.sun : DA_ICONS.moon;

  function syncThumbs(th) {{
    document.querySelectorAll('.g-card-thumb img[data-thumb-dark]').forEach(function(img) {{
      var next = th === 'light' ? img.dataset.thumbLight : img.dataset.thumbDark;
      if (next && img.getAttribute('src') !== next) img.setAttribute('src', next);
    }});
  }}
  syncThumbs(daGetTheme());
  document.addEventListener('designaura:themechange', function(e) {{
    syncThumbs(e.detail && e.detail.theme ? e.detail.theme : daGetTheme());
  }});

  document.querySelectorAll('.da-chip').forEach(function(chip) {{
    chip.addEventListener('click', function() {{
      var f = chip.dataset.filter;
      document.querySelectorAll('.da-chip').forEach(function(c) {{ c.classList.toggle('is-active', c === chip); }});
      document.querySelectorAll('.g-card').forEach(function(card) {{
        card.hidden = (f !== 'all' && card.dataset.flow !== f);
      }});
    }});
  }});

  var cmdkModal = document.getElementById('cmdkModal');
  var cmdkInput = document.getElementById('cmdkInput');
  var cmdkList = document.getElementById('cmdkList');

  var cmdkIndex = 0;
  function esc(str) {{
    return String(str == null ? '' : str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}
  function renderCmdk(q) {{
    var term = (q || '').toLowerCase().trim();
    var matches = SCREENS.filter(function(s) {{
      return !term || s.title.toLowerCase().includes(term) || (s.group || '').toLowerCase().includes(term);
    }});
    cmdkIndex = 0;
    cmdkList.innerHTML = matches.map(function(s, i) {{
      return '<a class="cmdk-item' + (i === 0 ? ' is-focus' : '') + '" href="' + esc(s.file) + '"><span>' + esc(s.title) + '</span><small style="font-family:var(--da-font-mono);color:var(--text-muted)">' + esc(s.group) + '</small></a>';
    }}).join('') || '<p style="padding:12px;margin:0;color:var(--text-muted)">Nenhuma tela encontrada.</p>';
  }}
  function visibleCmdk() {{ return Array.prototype.slice.call(cmdkList.querySelectorAll('.cmdk-item')); }}
  function moveCmdk(delta) {{
    var items = visibleCmdk();
    if (!items.length) return;
    cmdkIndex = (cmdkIndex + delta + items.length) % items.length;
    items.forEach(function(el, i) {{ el.classList.toggle('is-focus', i === cmdkIndex); }});
    items[cmdkIndex].scrollIntoView({{ block: 'nearest' }});
  }}
  function openCmdk() {{ cmdkModal.hidden = false; cmdkInput.value = ''; renderCmdk(''); cmdkInput.focus(); }}
  function closeCmdk() {{ cmdkModal.hidden = true; }}

  document.getElementById('btnCmdk').addEventListener('click', openCmdk);
  document.getElementById('btnCmdkClose').addEventListener('click', closeCmdk);
  cmdkModal.addEventListener('click', function(e) {{ if (e.target === cmdkModal) closeCmdk(); }});
  cmdkInput.addEventListener('input', function() {{ renderCmdk(cmdkInput.value); }});
  cmdkInput.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowDown') {{ e.preventDefault(); moveCmdk(1); }}
    else if (e.key === 'ArrowUp') {{ e.preventDefault(); moveCmdk(-1); }}
    else if (e.key === 'Enter') {{
      e.preventDefault();
      var items = visibleCmdk();
      if (items[cmdkIndex]) window.location.href = items[cmdkIndex].getAttribute('href');
    }}
  }});
  document.addEventListener('keydown', function(e) {{
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {{ e.preventDefault(); openCmdk(); }}
    if (e.key === 'Escape' && !cmdkModal.hidden) closeCmdk();
  }});
  var deep = new URLSearchParams(location.search).get('screen');
  if (deep) {{
    var card = document.getElementById('screen-' + deep);
    if (card) {{
      card.style.outline = '2px solid var(--accent, #EA580C)';
      card.scrollIntoView({{ block: 'center' }});
    }}
  }}
}})();
</script>
</body>
</html>
"""


def render_entrega_html(
    manifest: dict,
    tokens_link: str,
    parsed_tokens: dict[str, dict[str, str]] | None = None,
    out_dir: Path | None = None,
    app_url: str = "",
) -> str:
    """Gera o Hub Unificado de Link Unico (entrega.html)."""
    proj = manifest.get("project", {})
    name = html.escape(proj.get("name", "Projeto Design Aura"))
    subtitle = html.escape(proj.get("subtitle", "Entrega Unificada"))
    default_theme = html.escape(proj.get("defaultTheme", "dark"))
    head_css = build_base_css(manifest, tokens_link, parsed_tokens)

    live_app_url = (app_url or proj.get("appUrl") or "").strip()
    if not live_app_url:
        start_id = proj.get("startScreenId") or manifest["screens"][0]["id"]
        start_screen = next((s for s in manifest["screens"] if s["id"] == start_id), manifest["screens"][0])
        if start_screen.get("isSpaRoute"):
            live_app_url = start_screen.get("file", "")

    bible_html_href = ""
    bible_pdf_href = ""
    if out_dir is not None:
        for cand in ("DESIGN-BIBLE.html", "../DESIGN-BIBLE.html"):
            if (out_dir / cand).exists():
                bible_html_href = cand
                break
        for cand in ("DESIGN-BIBLE.pdf", "../DESIGN-BIBLE.pdf"):
            if (out_dir / cand).exists():
                bible_pdf_href = cand
                break

    tabs = [
        {"id": "figma", "label": "Mapa Figma", "src": "fluxo.html"},
    ]
    if live_app_url:
        tabs.append({"id": "app", "label": "App ao Vivo", "src": live_app_url})
    tabs.extend([
        {"id": "preview", "label": "Preview Guiado", "src": "preview.html"},
        {"id": "galeria", "label": "Galeria", "src": "index.html"},
    ])
    if bible_html_href:
        tabs.append({"id": "biblia", "label": "Bíblia Visual", "src": bible_html_href})

    tabs_html = "".join(
        f'<button type="button" class="hub-tab" data-tab="{html.escape(t["id"])}" data-src="{html.escape(t["src"])}">{html.escape(t["label"])}</button>'
        for t in tabs
    )
    pdf_btn = (
        f'<a class="da-btn da-btn--sm hub-hide-xs" href="{html.escape(bible_pdf_href)}" target="_blank" rel="noopener">PDF</a>'
        if bible_pdf_href
        else ""
    )
    default_mobile_tab = "app" if live_app_url else "preview"

    return f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="{default_theme}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} · Entrega Unificada</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap">
<script>{THEME_BOOT_JS}</script>
{head_css}
<style>
  html, body {{ height: 100%; overflow: hidden; margin: 0; }}
  .da-hub {{ display: flex; flex-direction: column; height: 100dvh; width: 100vw; overflow: hidden; background: var(--surface-z1); }}
  .hub-bar {{
    position: relative; z-index: 50; display: flex; align-items: center; justify-content: space-between; gap: 10px;
    min-height: 54px; padding: 6px 14px; background: var(--da-navy); color: #F8FAFC;
    border-bottom: 1px solid rgba(148, 197, 255, 0.22); box-shadow: var(--shadow-z1);
  }}
  .hub-brand {{ display: flex; flex-direction: column; min-width: 0; max-width: 240px; flex: 0 1 auto; }}
  .hub-brand strong {{ font-family: var(--da-font-display); font-size: 13.5px; font-weight: 700; color: #FFFFFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .hub-brand span {{ font-family: var(--da-font-mono); font-size: 11px; color: #C2D6EE; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .hub-tabs {{
    display: flex; align-items: center; gap: 4px; padding: 3px; border-radius: 10px;
    background: rgba(6, 15, 32, 0.48); border: 1px solid rgba(148, 197, 255, 0.22);
    overflow-x: auto; scrollbar-width: none;
  }}
  .hub-tabs::-webkit-scrollbar {{ display: none; }}
  .hub-tab {{
    display: inline-flex; align-items: center; justify-content: center; min-height: 34px; padding: 0 12px;
    border-radius: 7px; border: 1px solid transparent; background: transparent; color: #D7E5F7;
    font-family: var(--da-font-ui); font-size: 12.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
    transition-property: background-color, border-color, color; transition-duration: 150ms; transition-timing-function: ease-out;
  }}
  .hub-tab:hover {{ color: #FFFFFF; background: rgba(255, 255, 255, 0.08); }}
  .hub-tab.is-active {{
    background: var(--da-accent-deep); color: #FFFFFF; border-color: rgba(255, 255, 255, 0.24);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.20), 0 2px 8px rgba(0, 0, 0, 0.28);
  }}
  .hub-actions {{ display: flex; align-items: center; gap: 6px; flex: none; }}
  .hub-actions .da-btn {{
    background: rgba(255, 255, 255, 0.10); color: #FFFFFF; border-color: rgba(194, 214, 238, 0.28); box-shadow: none;
  }}
  .hub-actions .da-btn:hover {{ background: rgba(255, 255, 255, 0.18); border-color: rgba(255, 255, 255, 0.45); }}
  .hub-stage {{ position: relative; flex: 1 1 auto; min-height: 0; background: var(--surface-z0); }}
  .hub-frame {{ width: 100%; height: 100%; display: block; border: 0; background: var(--surface-z1); }}

  @media (max-width: 768px) {{
    .hub-bar {{ flex-wrap: wrap; padding: 8px 10px; gap: 8px; }}
    .hub-brand {{ max-width: calc(100% - 110px); }}
    .hub-tabs {{ order: 3; width: 100%; display: grid; grid-template-columns: repeat(auto-fit, minmax(112px, 1fr)); gap: 4px; }}
    .hub-tab {{ min-height: 44px; padding: 0 8px; font-size: 12.5px; }}
    .hub-hide-xs {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="da-hub" data-hub="true">
  <header class="hub-bar">
    <div class="hub-brand">
      <strong>{name}</strong>
      <span>{subtitle}</span>
    </div>
    <nav class="hub-tabs" id="hubTabs" aria-label="Navegação da entrega">
      {tabs_html}
    </nav>
    <div class="hub-actions">
      {pdf_btn}
      <a class="da-btn da-btn--sm hub-hide-xs" id="btnOpenDirect" href="fluxo.html" target="_blank" rel="noopener">Abrir aba</a>
      <button type="button" class="da-btn da-btn--icon" id="btnThemeToggle" aria-label="Alternar tema" onclick="daToggleTheme()"></button>
    </div>
  </header>
  <main class="hub-stage">
    <iframe class="hub-frame" id="hubFrame" title="Visualizador unificado de entrega" src="fluxo.html"></iframe>
  </main>
</div>
<script>
{ICONS_JS}
{THEME_TOGGLE_JS}
(function() {{
  var frame = document.getElementById('hubFrame');
  var openDirect = document.getElementById('btnOpenDirect');
  var tabBtns = Array.prototype.slice.call(document.querySelectorAll('.hub-tab'));
  var defaultMobileTab = {json.dumps(default_mobile_tab)};

  function syncFrameTheme(theme) {{
    try {{ localStorage.setItem('design-aura:theme', theme); }} catch (e) {{}}
    try {{
      if (frame && frame.contentWindow) {{
        frame.contentWindow.postMessage({{ type: 'designaura:theme', theme: theme }}, '*');
      }}
    }} catch (e) {{}}
    try {{
      if (frame && frame.contentDocument && frame.contentDocument.documentElement) {{
        frame.contentDocument.documentElement.setAttribute('data-theme', theme);
      }}
    }} catch (e) {{}}
  }}

  function activateTab(tabId, pushUrl) {{
    var target = tabBtns.find(function(b) {{ return b.dataset.tab === tabId; }}) || tabBtns[0];
    if (!target) return;
    tabBtns.forEach(function(b) {{
      var on = b === target;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-current', on ? 'page' : 'false');
    }});
    var src = target.dataset.src;
    if (frame.getAttribute('src') !== src) frame.setAttribute('src', src);
    if (openDirect) openDirect.setAttribute('href', src);
    if (pushUrl) {{
      try {{
        var u = new URL(window.location.href);
        u.searchParams.set('tab', target.dataset.tab);
        window.history.replaceState(null, '', u.toString());
      }} catch (e) {{}}
    }}
  }}

  tabBtns.forEach(function(btn) {{
    btn.addEventListener('click', function() {{ activateTab(btn.dataset.tab, true); }});
  }});

  frame.addEventListener('load', function() {{
    syncFrameTheme(daGetTheme());
  }});

  document.addEventListener('designaura:themechange', function(e) {{
    syncFrameTheme(e.detail && e.detail.theme ? e.detail.theme : daGetTheme());
  }});

  document.getElementById('btnThemeToggle').innerHTML = daGetTheme() === 'dark' ? DA_ICONS.sun : DA_ICONS.moon;

  var qTab = new URLSearchParams(window.location.search).get('tab');
  var initialTab = qTab || (window.innerWidth <= 768 ? defaultMobileTab : 'figma');
  activateTab(initialTab, false);
}})();
</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Gerador de vitrine estilo Figma (fluxo.html, preview.html, index.html, entrega.html).")
    parser.add_argument("manifest", help="Caminho para screen-manifest.json")
    parser.add_argument("--tokens", default="", help="Caminho opcional para tokens.css relativo ao --out ou absoluto")
    parser.add_argument("--out", default=".", help="Diretorio de saida")
    parser.add_argument("--thumbs", default="", help="Diretorio opcional com PNGs de auditoria para miniaturas na Galeria (index.html)")
    parser.add_argument("--app-base", default="", help="Prefixo/URL base para telas SPA ('route') e aba 'App ao Vivo' em entrega.html (ex.: /app ou http://127.0.0.1:4188/app)")
    parser.add_argument("--verify-files", action="store_true", help="Falha se alguma tela do manifesto ou href local nao existir")
    parser.add_argument("--relayout", action="store_true", help="Forca reorganizacao panoramica Hub-and-Spoke ignorando x/y antigos")
    args = parser.parse_args()

    mpath = Path(args.manifest).resolve()
    if not mpath.exists():
        print(f"Manifesto nao encontrado: {mpath}", file=sys.stderr)
        sys.exit(1)

    try:
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
        _normalize_screen_targets(manifest, app_base=args.app_base)
        for note in apply_auto_layout(manifest, force_relayout=args.relayout):
            print(f"[layout] {note}")
        validate_manifest(manifest)
        if args.verify_files:
            missing = verify_screen_files(manifest, mpath, Path(args.out).resolve())
            if missing:
                for item in missing:
                    print(f"[BLOCK] {item}", file=sys.stderr)
                sys.exit(1)
    except Exception as exc:
        print(f"Erro no screen-manifest.json: {exc}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    tokens_link = ""
    parsed_tokens: dict[str, dict[str, str]] = {"light": {}, "dark": {}}
    if args.tokens:
        tpath = Path(args.tokens).resolve()
        if tpath.exists():
            parsed_tokens = extract_tokens_from_css(tpath)
            try:
                tokens_link = str(tpath.relative_to(out_dir))
            except ValueError:
                tokens_link = tpath.name
                (out_dir / tpath.name).write_text(tpath.read_text(encoding="utf-8"), encoding="utf-8")

    thumbs_dir = Path(args.thumbs).resolve() if args.thumbs else None
    thumbs_map = _resolve_thumbnails(manifest.get("screens", []), thumbs_dir, out_dir)

    (out_dir / "fluxo.html").write_text(render_fluxo_html(manifest, tokens_link, parsed_tokens), encoding="utf-8")
    (out_dir / "preview.html").write_text(render_preview_html(manifest, tokens_link, parsed_tokens), encoding="utf-8")
    (out_dir / "index.html").write_text(render_index_html(manifest, tokens_link, parsed_tokens, thumbs_map), encoding="utf-8")
    (out_dir / "entrega.html").write_text(
        render_entrega_html(manifest, tokens_link, parsed_tokens, out_dir=out_dir, app_url=args.app_base),
        encoding="utf-8",
    )

    print(f"Vitrine estilo Figma + Hub Unificado gerados em: {out_dir}")
    print(f"  - {out_dir / 'entrega.html'}")
    print(f"  - {out_dir / 'fluxo.html'}")
    print(f"  - {out_dir / 'preview.html'}")
    print(f"  - {out_dir / 'index.html'}")
    if args.verify_files:
        broken = verify_generated_links(out_dir)
        if broken:
            for item in broken:
                print(f"[BLOCK] {item}", file=sys.stderr)
            sys.exit(1)
        print("Links locais da vitrine conferidos.")


if __name__ == "__main__":
    main()
