#!/usr/bin/env python3
"""Estudio de Direcao: renderiza 2-3 direcoes visuais sobre o MESMO fragmento real do projeto.

Entrada: um JSON (veja assets/direction-board.example.json) com o fragmento (dados reais do projeto)
e as direcoes (semente de cor, acento, harmonia, profundidade, forma, densidade, fontes, adjetivos e o
que cada uma recusa). Saida: direction-board.html + tokens.json de cada direcao, prontos para a Biblia.

    python3 render_direction_board.py direcoes.json --out design/direcao/
"""
import argparse
import html
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from color_engine import build_tokens, hex_to_oklch, parse_color, wcag  # noqa: E402
from generate_tokens import SHAPE_RADII, build_css, elevation_lines  # noqa: E402

TONES = {"ok": "success", "atencao": "warning", "falha": "danger", "info": "info", "neutro": "primary"}


def esc(v) -> str:
    return html.escape(str(v))


def scoped_vars(tokens: dict, theme: str) -> str:
    lines = [f"--{k}: {v};" for k, v in tokens["semantic"][theme].items()]
    lines += [f"--radius-{k}: {v};" for k, v in tokens["radii"].items()]
    lines += [f"--{k}: {v};" for k, v in tokens["typography"].items()]
    lines += [f"--space-{k}: {v};" for k, v in tokens["spacing"].items()]
    lines += [f"--{k}: {v};" for k, v in tokens.get("sizing", {}).items()]
    lines += [ln.strip() for ln in elevation_lines(tokens["meta"]["depth_style"], theme)]
    return " ".join(lines)


def fragment(frag: dict) -> str:
    rows = []
    for r in frag.get("rows", [])[:5]:
        tone = TONES.get(r.get("tone", "neutro"), "primary")
        rows.append(
            f'<div class="row"><div class="row-main"><span class="row-name">{esc(r["name"])}</span>'
            f'<span class="row-meta">{esc(r.get("meta", ""))}</span></div>'
            f'<span class="badge" style="--tone-s: var(--{tone}-surface); --tone-b: var(--{tone}-border); --tone-t: var(--{tone}-text)">{esc(r.get("status", ""))}</span>'
            f'<span class="row-val num">{esc(r.get("value", ""))}</span></div>'
        )
    bars = "".join(f'<i style="height:{h}%; background: var(--chart-{i % 6 + 1})"></i>' for i, h in enumerate(frag.get("bars", [42, 68, 55, 80, 61, 74])))
    nav = "".join(f'<span class="nav-item{" is-active" if i == 0 else ""}">{esc(n)}</span>' for i, n in enumerate(frag.get("nav", [])[:4]))
    kpi = frag.get("kpi", {})
    return f"""
      <div class="appbar"><strong class="brand">{esc(frag.get('product', 'Produto'))}</strong><nav>{nav}</nav></div>
      <div class="content">
        <div class="head"><div><h3>{esc(frag.get('title', ''))}</h3><p class="sub">{esc(frag.get('subtitle', ''))}</p></div>
          <div class="actions"><button class="btn ghost">{esc(frag.get('secondary', 'Exportar'))}</button><button class="btn primary">{esc(frag.get('primary', 'Confirmar'))}</button></div></div>
        <div class="grid">
          <section class="card kpi"><span class="label">{esc(kpi.get('label', ''))}</span><span class="value num">{esc(kpi.get('value', ''))}</span>
            <span class="delta">{esc(kpi.get('delta', ''))}</span><div class="bars">{bars}</div></section>
          <section class="card list">{''.join(rows)}</section>
        </div>
        <div class="form"><label>{esc(frag.get('field_label', 'Buscar'))}<input value="{esc(frag.get('field_value', ''))}" aria-label="{esc(frag.get('field_label', 'Buscar'))}"></label></div>
      </div>"""


BOARD_CSS = """
*{box-sizing:border-box} body{margin:0;background:#0d0d0f;color:#f2f2f2;font:14px/1.5 system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.board-head{padding:32px 40px 8px} .board-head h1{margin:0 0 4px;font-size:22px} .board-head p{margin:0;color:#b5b5bb;max-width:80ch}
.direction{padding:24px 40px 40px;border-top:1px solid #26262b}
.dir-meta{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:24px;margin-bottom:16px}
.dir-meta h2{margin:0;font-size:20px} .adj{color:#c9c9cf} .dir-meta dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:2px 12px;color:#c9c9cf;font-size:13px}
.dir-meta dt{color:#8e8e96} .refuse{color:#c9c9cf;font-size:13px} .swatches{display:flex;gap:4px;margin-top:8px} .swatches i{width:22px;height:22px;border-radius:4px;display:block;border:1px solid #ffffff22}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.frame{border-radius:14px;overflow:hidden;border:1px solid #2a2a30}
.frame .tag{font:600 11px system-ui;letter-spacing:.04em;text-transform:uppercase;color:#8e8e96;padding:8px 12px;background:#141417}
.app{background:var(--surface-z1);color:var(--text-body);font-family:var(--font-ui);font-size:var(--text-base)}
.appbar{display:flex;align-items:center;gap:var(--space-6);padding:var(--space-3) var(--space-5);background:var(--surface-z2);border-bottom:1px solid var(--border-subtle)}
.brand{font-family:var(--font-display);color:var(--text-strong);letter-spacing:var(--tracking-display)}
.appbar nav{display:flex;gap:var(--space-1)} .nav-item{padding:var(--space-2) var(--space-3);border-radius:var(--radius-control-md);color:var(--text-muted)}
.nav-item.is-active{background:var(--primary-surface);color:var(--primary-text);font-weight:600}
.content{padding:var(--space-5)} .head{display:flex;justify-content:space-between;align-items:flex-end;gap:var(--space-4);margin-bottom:var(--space-4)}
h3{margin:0;font-family:var(--font-display);font-size:22px;color:var(--text-strong);letter-spacing:var(--tracking-display);text-wrap:balance}
.sub{margin:2px 0 0;color:var(--text-muted)} .actions{display:flex;gap:var(--space-2)}
.btn{min-height:var(--control-h, 36px);padding:0 var(--space-4);border-radius:var(--radius-control-md);font:600 13px var(--font-ui);border:1px solid transparent;cursor:pointer}
.btn.primary{background:var(--primary);color:var(--on-primary)} .btn.ghost{background:transparent;color:var(--text-body);border-color:var(--border-subtle)}
.grid{display:grid;grid-template-columns:240px 1fr;gap:var(--space-3)}
.card{background:var(--surface-z2);border:1px solid var(--border-subtle);border-radius:var(--radius-card-md);box-shadow:var(--shadow-z1), var(--rim-highlight)}
.kpi{padding:var(--space-4);display:flex;flex-direction:column;gap:2px} .label{color:var(--text-muted);font-size:12px}
.value{font-family:var(--font-display);font-size:28px;color:var(--text-strong);font-weight:650} .delta{color:var(--success-text);font-size:12px;font-weight:600}
.bars{display:flex;align-items:flex-end;gap:6px;height:56px;margin-top:10px} .bars i{flex:1;border-radius:3px 3px 0 0;display:block}
.list{padding:4px 0} .row{display:grid;grid-template-columns:1fr auto 96px;align-items:center;gap:var(--space-3);min-height:var(--row-h, 44px);padding:var(--space-1) var(--space-4);border-bottom:1px solid var(--border-subtle)}
.row:last-child{border-bottom:0} .row-main{display:flex;flex-direction:column;min-width:0} .row-name{color:var(--text-strong);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.row-meta{color:var(--text-muted);font-size:12px} .row-val{text-align:right;color:var(--text-strong)}
.badge{font-size:12px;font-weight:600;padding:2px 8px;border-radius:var(--radius-control-sm);background:var(--tone-s);border:1px solid var(--tone-b);color:var(--tone-t);white-space:nowrap}
.num{font-variant-numeric:tabular-nums}
.form{margin-top:var(--space-3)} .form label{display:grid;gap:4px;color:var(--text-muted);font-size:12px;max-width:360px}
.form input{min-height:var(--control-h, 36px);border-radius:var(--radius-control-md);border:1px solid var(--border-strong);background:var(--surface-z0);color:var(--text-strong);padding:0 10px;font:inherit}
@media (max-width:1100px){.pair{grid-template-columns:1fr}.dir-meta{grid-template-columns:1fr}.grid{grid-template-columns:1fr}}
"""


def render(spec: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    frag = spec["fragment"]
    sections, font_links = [], []
    for i, d in enumerate(spec["directions"][:3], 1):
        fonts = d.get("fonts", {})
        tokens = build_tokens(d["seed"], d.get("accent"), d.get("harmony", "complementar"), d.get("depth_style", "hairline"),
                              d.get("neutral_tint", 0.012), spec.get("project", "Projeto"), d.get("default_theme", "light"),
                              fonts, d.get("density", "regular"))
        tokens["radii"] = SHAPE_RADII.get(d.get("shape", "soft"), SHAPE_RADII["soft"])
        tokens["meta"].update({"shape": d.get("shape", "soft"), "direction": d.get("name", f"Direcao {i}")})
        slug = f"direcao-{i}"
        # A direcao em si (para generate_tokens.py --direction e discover_oss_components.py --direction)
        (out_dir / f"{slug}.json").write_text(json.dumps({**d, "project": spec.get("project", "Projeto"), "index": i},
                                                         ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (out_dir / f"{slug}.tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (out_dir / f"{slug}.tokens.css").write_text(build_css(tokens), encoding="utf-8")
        if fonts.get("url"):
            font_links.append(fonts["url"])
        sem_l = tokens["semantic"]["light"]
        swatches = "".join(f'<i title="{k}" style="background:{sem_l[k]}"></i>' for k in
                           ("surface-z1", "surface-z2", "border-subtle", "text-muted", "text-strong", "primary", "accent", "success", "warning", "danger", "chart-2", "chart-3"))
        refuse = "".join(f"<li>{esc(r)}</li>" for r in d.get("refuses", []))
        hue = round(hex_to_oklch(parse_color(tokens["meta"]["seed"]))[2])
        frames = "".join(
            f'<div class="frame"><div class="tag">{theme_label}</div><div class="app" style="{esc(scoped_vars(tokens, theme))}">{fragment(frag)}</div></div>'
            for theme, theme_label in (("light", "Light"), ("dark", "Dark")))
        sections.append(f"""
  <section class="direction" id="{slug}">
    <div class="dir-meta">
      <div><h2>{i}. {esc(d.get('name', ''))}</h2><p class="adj">{esc(' · '.join(d.get('adjectives', [])))}</p><p class="refuse">{esc(d.get('concept', ''))}</p>
        <div class="swatches">{swatches}</div></div>
      <dl><dt>Semente</dt><dd>{esc(tokens['meta']['seed'])} (matiz {hue}°) + {esc(tokens['meta']['accent'])}</dd><dt>Harmonia</dt><dd>{esc(d.get('harmony', 'complementar'))}</dd>
        <dt>Profundidade</dt><dd>{esc(tokens['meta']['depth_style'])}</dd><dt>Forma</dt><dd>{esc(d.get('shape', 'soft'))}</dd>
        <dt>Densidade</dt><dd>{esc(d.get('density', 'regular'))}</dd><dt>Tipografia</dt><dd>{esc(fonts.get('name', fonts.get('ui', 'sistema')))}</dd></dl>
      <div class="refuse"><strong>Recusa</strong><ul>{refuse}</ul></div>
    </div>
    <div class="pair">{frames}</div>
  </section>""")
    links = "".join(f'<link rel="stylesheet" href="{esc(u)}">' for u in dict.fromkeys(font_links))
    page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Estúdio de Direção — {esc(spec.get('project', 'Projeto'))}</title>{links}<style>{BOARD_CSS}</style></head>
<body class="da-board">
  <header class="board-head"><h1>Estúdio de Direção — {esc(spec.get('project', 'Projeto'))}</h1>
  <p>O mesmo trecho real do produto em cada direção. Escolha uma, misture eixos (por exemplo, a cor da 1 com a forma da 2) ou peça outra rodada. A escolha e o motivo vão para a Bíblia.</p></header>
  {''.join(sections)}
</body></html>
"""
    path = out_dir / "direction-board.html"
    path.write_text(page, encoding="utf-8")
    return path


def divergence(spec: dict) -> list[str]:
    """Aponta direcoes parecidas demais (mesma matiz, mesma profundidade e mesma forma)."""
    notes = []
    dirs = spec["directions"]
    for a in range(len(dirs)):
        for b in range(a + 1, len(dirs)):
            la, ca, ha = hex_to_oklch(parse_color(dirs[a]["seed"]))
            lb, cb, hb = hex_to_oklch(parse_color(dirs[b]["seed"]))
            if ca < 0.03 or cb < 0.03:  # semente sem matiz: compara luminosidade e croma, nao o angulo
                hue_gap = 0.0 if (ca < 0.03 and cb < 0.03 and abs(la - lb) < 0.25) else 90.0
            else:
                hue_gap = abs(((ha - hb + 540) % 360) - 180)
            same = [k for k in ("depth_style", "shape", "density") if dirs[a].get(k) == dirs[b].get(k)]
            same_font = dirs[a].get("fonts", {}).get("ui") == dirs[b].get("fonts", {}).get("ui")
            if hue_gap < 25 and len(same) >= 2 and same_font:
                notes.append(f"Direcoes {a + 1} e {b + 1} sao parecidas demais (matiz {round(hue_gap)}°, iguais em {', '.join(same)} e fonte).")
    return notes


def main():
    ap = argparse.ArgumentParser(description="Renderiza o Estudio de Direcao (2-3 direcoes sobre o mesmo fragmento real).")
    ap.add_argument("spec", help="JSON com fragment e directions")
    ap.add_argument("--out", default="direcao", help="Pasta de saida")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    if not 2 <= len(spec.get("directions", [])) <= 3:
        print("Use de 2 a 3 direcoes.", file=sys.stderr)
        sys.exit(1)
    path = render(spec, Path(args.out))
    print(f"Estudio de Direcao: {path}")
    for note in divergence(spec):
        print(f"[REVIEW] {note}")


if __name__ == "__main__":
    main()
