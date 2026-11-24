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
    kind = frag.get("kind", "app")
    if kind == "site":
        return fragment_site(frag)
    if kind == "mobile":
        return fragment_mobile(frag)
    return fragment_app(frag)


def badge(r: dict) -> str:
    tone = TONES.get(r.get("tone", "neutro"), "primary")
    return (f'<span class="badge" style="--tone-s: var(--{tone}-surface); --tone-b: var(--{tone}-border); --tone-t: var(--{tone}-text)">'
            f'{esc(r.get("status", ""))}</span>')


def fragment_site(frag: dict) -> str:
    links = "".join(f"<span>{esc(n)}</span>" for n in frag.get("nav", [])[:4])
    proof = "".join(f'<li><strong class="num">{esc(p.get("value", ""))}</strong><span>{esc(p.get("label", ""))}</span></li>' for p in frag.get("proof", [])[:3])
    feats = "".join(f'<article class="feat"><h4>{esc(f.get("title", ""))}</h4><p>{esc(f.get("text", ""))}</p></article>' for f in frag.get("features", [])[:3])
    return f"""
      <div class="site">
        <header class="site-nav"><strong class="brand">{esc(frag.get('product', 'Produto'))}</strong><nav>{links}</nav>
          <button class="btn primary">{esc(frag.get('primary', 'Agendar'))}</button></header>
        <section class="site-hero"><h3 class="display">{esc(frag.get('headline', ''))}</h3><p class="lede">{esc(frag.get('lede', ''))}</p>
          <div class="actions"><button class="btn primary">{esc(frag.get('primary', 'Agendar'))}</button><button class="btn ghost">{esc(frag.get('secondary', 'Ver mais'))}</button></div>
          <ul class="proof">{proof}</ul></section>
        <section class="site-feats">{feats}</section>
      </div>"""


def fragment_mobile(frag: dict) -> str:
    rows = "".join(f'<div class="m-row"><div class="row-main"><span class="row-name">{esc(r["name"])}</span>'
                   f'<span class="row-meta">{esc(r.get("meta", ""))}</span></div>{badge(r)}</div>' for r in frag.get("rows", [])[:4])
    tabs = "".join(f'<span class="{"is-active" if i == 0 else ""}">{esc(n)}</span>' for i, n in enumerate(frag.get("nav", [])[:4]))
    kpi = frag.get("kpi", {})
    return f"""
      <div class="phone">
        <div class="m-top"><span class="m-title">{esc(frag.get('title', ''))}</span><span class="m-sub">{esc(frag.get('subtitle', ''))}</span></div>
        <div class="m-summary"><span class="label">{esc(kpi.get('label', ''))}</span><span class="value num">{esc(kpi.get('value', ''))}</span></div>
        <div class="m-list">{rows}</div>
        <div class="m-cta"><button class="btn primary">{esc(frag.get('primary', 'Confirmar'))}</button></div>
        <nav class="m-tabs">{tabs}</nav>
      </div>"""


def fragment_app(frag: dict) -> str:
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
.site{background:var(--surface-z1);container-type:inline-size} @container (max-width:760px){.site .site-nav nav{display:none}} .site-nav{display:flex;align-items:center;justify-content:space-between;gap:var(--space-4);padding:var(--space-4) var(--space-6);border-bottom:1px solid var(--border-subtle)}
.site-nav nav{display:flex;flex-wrap:wrap;gap:var(--space-4);color:var(--text-muted)} .site-nav .brand,.btn{white-space:nowrap} .site-hero{padding:var(--space-10) var(--space-6) var(--space-8);max-width:64ch}
.display{margin:0;font-family:var(--font-display);font-size:clamp(28px,3vw,40px);line-height:1.08;color:var(--text-strong);letter-spacing:var(--tracking-display);text-wrap:balance}
.lede{margin:var(--space-3) 0 var(--space-5);color:var(--text-body);font-size:calc(var(--text-base) * 1.1);max-width:56ch;text-wrap:pretty}
.proof{display:flex;gap:var(--space-6);list-style:none;padding:0;margin:var(--space-6) 0 0;color:var(--text-muted)} .proof li{display:grid} .proof strong{color:var(--text-strong);font-size:20px}
.site-feats{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-5);padding:0 var(--space-6) var(--space-8)}
.feat{border-top:2px solid var(--primary-strong, var(--primary));padding-top:var(--space-3)} .feat h4{margin:0 0 var(--space-1);color:var(--text-strong)} .feat p{margin:0;color:var(--text-muted)}
.phone{width:360px;max-width:100%;margin:var(--space-4) auto;border-radius:28px;overflow:hidden;border:1px solid var(--border-subtle);background:var(--surface-z1);display:flex;flex-direction:column;min-height:620px}
.m-top{display:grid;padding:var(--space-4);background:var(--surface-z2);border-bottom:1px solid var(--border-subtle)} .m-title{font-family:var(--font-display);font-size:20px;font-weight:650;color:var(--text-strong)} .m-sub{color:var(--text-muted);font-size:13px}
.m-summary{display:flex;justify-content:space-between;align-items:baseline;padding:var(--space-3) var(--space-4)} .m-summary .value{font-size:22px;font-weight:700;color:var(--text-strong)}
.m-list{display:grid;grid-template-columns:minmax(0,1fr);gap:var(--space-2);padding:0 var(--space-4)} .m-row .row-main{min-width:0} .m-row .row-name{white-space:normal} .m-row{display:flex;justify-content:space-between;align-items:center;gap:var(--space-3);min-height:var(--row-h, 44px);padding:var(--space-2) var(--space-3);background:var(--surface-z2);border:1px solid var(--border-subtle);border-radius:var(--radius-card-sm)}
.m-cta{padding:var(--space-4)} .m-cta .btn{width:100%;min-height:var(--touch-min, 44px)}
.m-tabs{margin-top:auto;display:grid;grid-template-columns:repeat(4,1fr);background:var(--surface-z2);border-top:1px solid var(--border-subtle)} .m-tabs span{min-height:var(--touch-min, 44px);display:grid;place-items:center;font-size:12px;font-weight:600;color:var(--text-muted)} .m-tabs .is-active{color:var(--primary-text)}
.frag-tag{margin:var(--space-5, 20px) 0 8px;font:600 12px system-ui;color:#8e8e96;text-transform:uppercase;letter-spacing:.04em}
.form input{min-height:var(--control-h, 36px);border-radius:var(--radius-control-md);border:1px solid var(--border-strong);background:var(--surface-z0);color:var(--text-strong);padding:0 10px;font:inherit}
@media (max-width:1100px){.pair{grid-template-columns:1fr}.dir-meta{grid-template-columns:1fr}.grid{grid-template-columns:1fr}}
"""


def render(spec: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    frags = spec.get("fragments") or [spec["fragment"]]
    sections, font_links = [], []
    for i, d in enumerate(spec["directions"][:3], 1):
        fonts = d.get("fonts", {})
        tokens = build_tokens(d["seed"], d.get("accent"), d.get("harmony", "complementar"), d.get("depth_style", "hairline"),
                              d.get("neutral_tint", 0.012), spec.get("project", "Projeto"), d.get("default_theme", "light"),
                              fonts, d.get("density", "regular"), d.get("motion", "subtle"))
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
        kinds = {"app": "Sistema", "site": "Site", "mobile": "Mobile"}
        frames = "".join(
            (f'<p class="frag-tag">{esc(kinds.get(frag.get("kind", "app"), "Tela"))}</p>' if len(frags) > 1 else "")
            + '<div class="pair">' + "".join(
                f'<div class="frame"><div class="tag">{theme_label}</div><div class="app" style="{esc(scoped_vars(tokens, theme))}">{fragment(frag)}</div></div>'
                for theme, theme_label in (("light", "Light"), ("dark", "Dark"))) + "</div>"
            for frag in frags)
        sections.append(f"""
  <section class="direction" id="{slug}">
    <div class="dir-meta">
      <div><h2>{i}. {esc(d.get('name', ''))}</h2><p class="adj">{esc(' · '.join(d.get('adjectives', [])))}</p><p class="refuse">{esc(d.get('concept', ''))}</p>
        <div class="swatches">{swatches}</div></div>
      <dl><dt>Semente</dt><dd>{esc(tokens['meta']['seed'])} (matiz {hue}°) + {esc(tokens['meta']['accent'])}</dd><dt>Harmonia</dt><dd>{esc(d.get('harmony', 'complementar'))}</dd>
        <dt>Profundidade</dt><dd>{esc(tokens['meta']['depth_style'])}</dd><dt>Forma</dt><dd>{esc(d.get('shape', 'soft'))}</dd>
        <dt>Densidade</dt><dd>{esc(d.get('density', 'regular'))}</dd><dt>Motion</dt><dd>{esc(d.get('motion', 'subtle'))}</dd><dt>Tipografia</dt><dd>{esc(fonts.get('name', fonts.get('ui', 'sistema')))}</dd></dl>
      <div class="refuse"><strong>Recusa</strong><ul>{refuse}</ul></div>
    </div>
    {frames}
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
