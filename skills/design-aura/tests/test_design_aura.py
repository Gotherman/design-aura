#!/usr/bin/env python3
"""Regressao da Design Aura. Rode: python3 tests/test_design_aura.py"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_contrast import color_to_opaque_rgb, evaluate_pair  # noqa: E402
from build_figma_canvas import apply_auto_layout  # noqa: E402
from discover_oss_components import search_local  # noqa: E402
from render_design_bible import build_html  # noqa: E402
from lint_design_aura import scan_file  # noqa: E402


def run_py(script: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True)


class ContrastTests(unittest.TestCase):
    def test_oklch_hsl_rgb_and_alpha(self):
        dark = color_to_opaque_rgb("oklch(25% 0.03 250)")
        paper = color_to_opaque_rgb("oklch(97% 0.01 95)")
        self.assertIsNotNone(dark)
        self.assertLess(dark[0], 80)
        self.assertGreater(paper[0], 220)

        pair = evaluate_pair("oklch(22% 0.03 250)", "oklch(97% 0.008 95)", "body", "oklch", theme="light")
        self.assertGreaterEqual(pair["wcag"], 4.5)
        self.assertNotIn("nao resolvida", pair["reason"])

        hsl = evaluate_pair("hsl(220, 28%, 14%)", "hsl(40, 24%, 96%)", "body", "hsl", theme="light")
        self.assertGreaterEqual(hsl["wcag"], 4.5)

        rgb = evaluate_pair("rgb(16, 24, 34)", "rgb(243, 246, 250)", "body", "rgb", theme="light")
        self.assertGreaterEqual(rgb["wcag"], 4.5)

        mid = color_to_opaque_rgb("rgba(255, 255, 255, 0.5)", backdrop=(0, 0, 0))
        self.assertAlmostEqual(mid[0], 128, delta=2)

        weak = evaluate_pair("oklch(88% 0.01 90)", "oklch(94% 0.01 90)", "body", "fraco", theme="light")
        self.assertEqual(weak["severity"], "BLOCK")

    def test_css_var_chain(self):
        css = """
        :root {
          --ink: #101822;
          --text-strong: var(--ink);
          --surface-z1: oklch(97% 0.006 95);
        }
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tokens.css"
            path.write_text(css, encoding="utf-8")
            proc = run_py("audit_contrast.py", [str(path), "--format", "json"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = json.loads(proc.stdout)
        self.assertTrue(rows)
        self.assertTrue(all(r["wcag"] >= 4.5 for r in rows))
        self.assertTrue(all(r["fg"].startswith("#") for r in rows))


class TokenExportTests(unittest.TestCase):
    def test_all_formats_share_hex(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = run_py(
                "generate_tokens.py",
                [str(ROOT / "assets" / "tokens.example.json"), "--format", "all", "--out", str(out / "tokens.css"), "--check-contrast"],
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            for name in ("tokens.css", "tokens.tailwind.css", "tokens.ts", "DesignTokens.swift", "DesignTokens.kt", "design_tokens.dart"):
                self.assertTrue((out / name).exists(), name)
            swift = (out / "DesignTokens.swift").read_text(encoding="utf-8")
            kotlin = (out / "DesignTokens.kt").read_text(encoding="utf-8")
            dart = (out / "design_tokens.dart").read_text(encoding="utf-8")
            theme = (out / "tokens.tailwind.css").read_text(encoding="utf-8")
            self.assertIn("pageIos", swift)
            self.assertIn("Color(0xFF", kotlin)
            self.assertIn("Color(0xFF", dart)
            self.assertIn("@theme", theme)
            self.assertIn("--color-surface-z1", theme)


class LintTests(unittest.TestCase):
    def _scan(self, name: str, text: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            return scan_file(path, Path(tmp))

    def test_structural_and_allow(self):
        nested = self._scan("nested.html", '<div class="card"><div class="card">Rota 12</div></div>')
        self.assertIn("DA-B2-01", {f["rule"] for f in nested})

        radius = self._scan("radius.html", '<div class="rounded-xl p-2"><div class="rounded-xl">Rota</div></div>')
        self.assertIn("DA-B7-01", {f["rule"] for f in radius})

        shadow = self._scan(
            "dark.css",
            '[data-theme="dark"] .panel { box-shadow: 0 24px 40px rgba(0, 0, 0, 0.62); }',
        )
        self.assertIn("DA-B7-03", {f["rule"] for f in shadow})

        avatar = self._scan("ava.html", '<img class="avatar" alt="Ana Costa" src="ana.jpg">')
        self.assertIn("DA-B10-04", {f["rule"] for f in avatar})

        loop = self._scan("orb.css", ".blob { animation: drift 8s infinite; }")
        self.assertIn("DA-B6-04", {f["rule"] for f in loop})

        wait = self._scan("wait.css", ".skeleton { animation: shimmer 1.2s infinite; }")
        self.assertNotIn("DA-B6-04", {f["rule"] for f in wait})

        allowed = self._scan(
            "brand.html",
            "<!-- design-aura-allow: DA-B1-01 marca oficial da empresa -->\n"
            '<div class="bg-gradient-to-r from-purple-500 to-indigo-500"></div>',
        )
        self.assertNotIn("DA-B1-01", {f["rule"] for f in allowed})

        bare = self._scan("bare.html", '<div class="bg-gradient-to-r from-purple-500 to-indigo-500"></div>')
        self.assertIn("DA-B1-01", {f["rule"] for f in bare})

    def test_v2_craft_floor_rules(self):
        # Dev-leak copy / stub excuse
        leak = self._scan("desktop-pagar.html", "<p>Os outros titulos em aberto nao estao nesta amostra.</p>")
        self.assertIn("DA-B2-08A", {f["rule"] for f in leak})

        seed = self._scan("desktop-editais.html", "<p>A grade e a semente do funil.</p>")
        self.assertIn("DA-B2-08A", {f["rule"] for f in seed})

        # Editorial serif in operational screen
        serif = self._scan("desktop-pagar.html", "<table><tbody><tr><td>1</td></tr></tbody></table><style>h1{font-family:'Source Serif 4', serif;}</style>")
        rules = {f["rule"] for f in serif}
        self.assertIn("DA-B4-04", rules)
        self.assertIn("DA-B2-08B", rules)

        # Allowed serif with explicit opt-in
        serif_ok = self._scan("desktop-report.html", '<html data-allow-serif="true"><table><tbody><tr><td>1</td></tr><tr><td>2</td></tr><tr><td>3</td></tr></tbody></table><style>h1{font-family:Georgia, serif;}</style></html>')
        self.assertNotIn("DA-B4-04", {f["rule"] for f in serif_ok})
        self.assertNotIn("DA-B2-08B", {f["rule"] for f in serif_ok})

        # Unstyled raw textarea
        ta = self._scan("desktop-chat.html", '<label for="m">Msg</label><textarea id="m"></textarea>')
        self.assertIn("DA-B9-05", {f["rule"] for f in ta})

    def test_v21_pragmatic_rules_no_false_positives_on_good_ui(self):
        # 1. BEM card sub-elements (card-head, card-title, card-body) MUST NOT trigger DA-B2-01
        bem_card = self._scan(
            "bem.html",
            '<article class="h-card"><div class="h-card-head"><h2 class="h-card-title">Resumo</h2><p class="h-card-sub">30d</p></div><div class="h-card-body">OK</div></article>',
        )
        self.assertNotIn("DA-B2-01", {f["rule"] for f in bem_card})
        # Genuine card-inside-card STILL triggers DA-B2-01 BLOCK
        bad_card = self._scan("bad.html", '<div class="h-card"><div class="kpi-card">Aninhado</div></div>')
        self.assertIn("DA-B2-01", {f["rule"] for f in bad_card})

        # 2. Real context label with .eyebrow/.kicker passes; cliche FEATURES or "01 //" blocks
        real_label = self._scan("cal.html", '<p class="cal-eyebrow">Novembro 2026</p><span class="rail-kicker">Histórico</span>')
        self.assertNotIn("DA-B1-05", {f["rule"] for f in real_label})
        slop_label = self._scan("slop.html", '<span class="eyebrow">FEATURES</span><h3>01 // Plataforma</h3>')
        self.assertIn("DA-B1-05", {f["rule"] for f in slop_label})

        # 3. Composite search input with :focus-within passes DA-B9-02
        search_css = self._scan("search.css", ".box:focus-within { outline: 2px solid #EA580C; } .box input { outline: none; }")
        self.assertNotIn("DA-B9-02", {f["rule"] for f in search_css})

        # 4. Optical spacing 7px/9px/11px and font-weight 800 on display pass; 13px is only MEDIUM (not BLOCK)
        opt_css = self._scan("opt.css", ".btn { gap: 7px; padding: 9px 14px; font-weight: 800; } .odd { margin: 13px; }")
        self.assertFalse(any(f["severity"] == "BLOCK" for f in opt_css))
        self.assertTrue(any(f["rule"] == "DA-B7-02" and f["severity"] == "MEDIUM" for f in opt_css))

        # 5. Chat typing dots and dark inset well shadow pass; decorative drift loop still flags
        good_anim = self._scan("good.css", ".typing span { animation: blink 1.2s infinite; } [data-theme='dark'] .well { box-shadow: inset 0 2px 6px rgba(0,0,0,0.5); }")
        self.assertNotIn("DA-B6-04", {f["rule"] for f in good_anim})
        self.assertNotIn("DA-B7-03", {f["rule"] for f in good_anim})

        # 6. Callout with left accent bar passes DA-B1-06B; subtle score ring passes DA-B1-02
        callout = self._scan("note.html", '<div class="callout border-l-4 rounded-lg">Aviso importante</div><style>.score{box-shadow:0 0 18px rgba(255,86,30,0.22);}</style>')
        self.assertNotIn("DA-B1-06B", {f["rule"] for f in callout})
        self.assertNotIn("DA-B1-02", {f["rule"] for f in callout})


class BiblePaperTests(unittest.TestCase):
    def test_paper_has_no_fixed_board_and_renders_specimens(self):
        sample = "# Biblia\n\n## 8. Arsenal\n\n| Peça | Caminho |\n|---|---|\n| Tabela | `npm install @tanstack/react-table` |\n"
        page = build_html(
            sample,
            "Biblia",
            tokens_light={"--surface-z1": "#F1F5F9", "--surface-z2": "#FFFFFF", "--accent": "#EA580C"},
            tokens_dark={"--surface-z1": "#0E1724", "--surface-z2": "#152336", "--accent": "#FF6B38"},
        )
        self.assertNotIn("overflow: hidden", page)
        self.assertNotIn("height: 210mm", page)
        self.assertNotIn("Palatino", page)
        self.assertIn("<table>", page)
        self.assertIn("npm install", page)
        self.assertIn("specimen-sheet", page)
        self.assertIn("#FF6B38", page)
        self.assertIn('class="swatch"', build_html("# T\n\nCor `#EA580C`.\n", "T"))


class DiscoverTests(unittest.TestCase):
    def test_filters_mode_license_and_gallery(self):
        operate = search_local("marquee hero landing", "react", "system", "operate", 8)
        self.assertFalse(any(item["name"] == "Magic UI" for item in operate["adopt"]))
        self.assertTrue(all(item["license_ok"] for item in operate["adopt"]))

        persuade = search_local("marquee hero landing", "react", "system", "persuade", 8)
        self.assertTrue(any(item["name"] == "Magic UI" for item in persuade["adopt"]))

        gantt = search_local("gantt timeline", "react", "system", "operate", 6)
        self.assertTrue(any("Kibo" in item["name"] for item in gantt["adopt"]))

        traps = search_local("aceternity spotlight", "react", "system", "persuade", 4)
        self.assertTrue(any("Aceternity" in item["name"] for item in traps["traps"]))
        self.assertFalse(any("Aceternity" in item["name"] for item in traps["adopt"]))

        refs = search_local("referencia fluxo onboarding ios", "ios", "ios", "operate", 4)
        self.assertTrue(any(item["usage"] == "reference" for item in refs["reference"]))

    def test_anatomy_is_reference_not_a_dependency(self):
        ios = search_local("tab bar safe area", "ios", "ios", "operate", 4)
        self.assertTrue(any("Human Interface" in item["name"] for item in ios["reference"]))
        self.assertFalse(any("Human Interface" in item["name"] for item in ios["adopt"]))

        admin = search_local("shopify admin polaris", "react", "system", "operate", 4)
        self.assertTrue(any(item["name"] == "Shopify Polaris" for item in admin["reference"]))
        self.assertFalse(any(item["name"] == "Shopify Polaris" for item in admin["adopt"]))

        gantt = search_local("gantt timeline", "react", "system", "operate", 6)
        self.assertFalse(any(item["kind"] in {"official", "anatomy"} for item in gantt["reference"]))

    def test_real_products_are_study_not_a_skin(self):
        calendar = search_local("calendario agendamento", "react", "system", "operate", 4)
        self.assertTrue(any(item["name"] == "Cal.com" for item in calendar["reference"]))
        self.assertFalse(any(item["name"] == "Cal.com" for item in calendar["adopt"]))
        gantt = search_local("gantt timeline", "react", "system", "operate", 6)
        names = {item["name"] for item in gantt["reference"] + gantt["adopt"]}
        self.assertNotIn("Cal.com", names)
        self.assertNotIn("Grafana", names)

    def test_no_duplicates_and_html_ios_coverage_and_no_operate_serif_collision(self):
        # 1. Sem duplicatas entre registries_oss e components_oss
        tbl = search_local("tabela densa com filtros", "react", "system", "operate", 8)
        adopt_names = [it["name"].lower() for it in tbl["adopt"]]
        self.assertEqual(len(adopt_names), len(set(adopt_names)))

        # 2. Stack HTML/vanilla devolve ECharts e Tabulator
        html_res = search_local("grafico financeiro e tabela", "html", "system", "operate", 6)
        html_names = {it["name"] for it in html_res["adopt"]}
        self.assertIn("Apache ECharts", html_names)
        self.assertIn("Tabulator", html_names)

        # 3. Stack iOS devolve SwiftUI para bottom sheet e lista
        ios_res = search_local("bottom sheet e lista", "ios", "ios", "operate", 6)
        ios_names = {it["name"] for it in ios_res["adopt"]}
        self.assertIn("SwiftUI", ios_names)

        # 4. Zero colisao entre dominios Operate e tipografia serifada editorial
        domains = json.loads((ROOT / "data" / "domains.json").read_text(encoding="utf-8"))
        serif_ids = {"source-sans-serif", "newsreader-instrument", "fraunces-dm", "lora-plusjakarta"}
        for dom in domains:
            if dom.get("surface_mode", "").lower() == "operate":
                self.assertFalse(set(dom.get("typography_ids", [])) & serif_ids, dom["id"])


class CanvasTests(unittest.TestCase):
    def test_auto_layout_and_vitrine(self):
        manifest = {
            "project": {"name": "Teste", "startScreenId": "a"},
            "screens": [
                {"id": "a", "title": "Alpha <b>", "file": "a.html", "platform": "desktop", "flow": "op", "group": "Ops"},
                {"id": "b", "title": "Beta", "file": "b.html", "platform": "desktop", "flow": "op", "group": "Ops", "x": 70, "y": 100, "w": 360, "h": 350},
            ],
            "edges": [],
            "journeys": [{"id": "j1", "name": "Uso", "color": "#EA580C", "steps": [{"screenId": "a", "short": "Abrir", "title": "Abrir", "tip": "Olhar"}]}],
        }
        notes = apply_auto_layout(manifest)
        self.assertIsNotNone(manifest["screens"][0].get("x"))
        self.assertTrue(notes)

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a.html").write_text("<!doctype html><title>A</title>", encoding="utf-8")
            (folder / "b.html").write_text("<!doctype html><title>B</title>", encoding="utf-8")
            broken = dict(manifest)
            broken["screens"] = [dict(s) for s in manifest["screens"]]
            broken["screens"][0]["file"] = "ausente.html"
            missing_path = folder / "missing.json"
            missing_path.write_text(json.dumps(broken), encoding="utf-8")
            bad = run_py("build_figma_canvas.py", [str(missing_path), "--out", str(folder), "--verify-files"])
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("ausente.html", bad.stderr)

            good_path = folder / "screen-manifest.json"
            good_path.write_text(json.dumps(manifest), encoding="utf-8")
            good = run_py("build_figma_canvas.py", [str(good_path), "--out", str(folder), "--verify-files"])
            self.assertEqual(good.returncode, 0, good.stderr + good.stdout)
            index = (folder / "index.html").read_text(encoding="utf-8")
            preview = (folder / "preview.html").read_text(encoding="utf-8")
            self.assertIn("ArrowDown", index)
            self.assertIn("function esc(", index)
            self.assertIn("function esc(", preview)
            self.assertIn("params.get('screen')", preview)
            self.assertIn("Alpha &lt;b&gt;", index)
            fluxo = (folder / "fluxo.html").read_text(encoding="utf-8")
            self.assertIn("btnJumpStart", fluxo)
            self.assertIn("btnEdgesMode", fluxo)
            self.assertIn("Todas setas", fluxo)

    def test_hub_and_spoke_relayout_and_edge_tiers(self):
        # Simula uma torre vertical degenerada de 14 telas e 30 arestas
        screens = [
            {"id": "login", "title": "Entrada", "file": "login.html", "platform": "desktop", "flow": "conta", "group": "Conta", "x": 40, "y": 40, "w": 360, "h": 350},
            {"id": "portal", "title": "Portal", "file": "portal.html", "platform": "desktop", "flow": "inicio", "group": "Portal", "x": 40, "y": 420, "w": 360, "h": 350},
        ]
        for i in range(6):
            screens.append({"id": f"fin-{i}", "title": f"Fin {i}", "file": f"fin-{i}.html", "platform": "desktop", "flow": "financeiro", "sectionId": "sec-fin", "group": "Fin", "x": 40 + (i % 2) * 380, "y": 820 + (i // 2) * 380, "w": 360, "h": 350})
        for i in range(6):
            screens.append({"id": f"mob-{i}", "title": f"Mob {i}", "file": f"mob-{i}.html", "platform": "mobile", "flow": "mobile", "sectionId": "sec-mob", "group": "Mobile", "x": 40 + (i % 2) * 300, "y": 2100 + (i // 2) * 400, "w": 260, "h": 360})

        edges = [{"id": "e0", "from": "login", "to": "portal", "label": "Entrar", "flow": "inicio", "color": "#B53C0C"}]
        for i in range(6):
            edges.append({"id": f"ef-{i}", "from": "portal", "to": f"fin-{i}", "label": f"F{i}", "flow": "financeiro", "color": "#B53C0C"})
            edges.append({"id": f"ef-back-{i}", "from": f"fin-{i}", "to": "portal", "label": "Voltar", "flow": "financeiro", "color": "#B53C0C"})
        for i in range(5):
            edges.append({"id": f"ef-seq-{i}", "from": f"fin-{i}", "to": f"fin-{i+1}", "label": "Prox", "flow": "financeiro", "color": "#B53C0C"})
            edges.append({"id": f"em-seq-{i}", "from": f"mob-{i}", "to": f"mob-{i+1}", "label": "Prox", "flow": "mobile", "color": "#B53C0C"})
            edges.append({"id": f"em-back-{i}", "from": f"mob-{i+1}", "to": "mob-0", "label": "Inicio", "flow": "mobile", "color": "#B53C0C"})
        edges.append({"id": "em-hub", "from": "portal", "to": "mob-0", "label": "Mobile", "flow": "mobile", "color": "#B53C0C"})

        manifest = {"project": {"name": "Grande", "startScreenId": "login"}, "screens": screens, "edges": edges}
        notes = apply_auto_layout(manifest)
        self.assertTrue(any("hub-and-spoke" in n for n in notes))
        # Proporcao deve ficar panoramica (largura >= altura ou proxima, nao torre)
        self.assertGreater(manifest["project"]["worldWidth"], manifest["project"]["worldHeight"] * 0.9)
        tiers = [e.get("tier") for e in manifest["edges"]]
        self.assertIn("primary", tiers)
        self.assertIn("secondary", tiers)
        # Re-coloriu setas monocromaticas por fluxo
        colors = {e.get("color") for e in manifest["edges"]}
        self.assertGreater(len(colors), 1)


if __name__ == "__main__":
    unittest.main()
