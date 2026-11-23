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

from audit_contrast import audit_file, color_to_opaque_rgb, evaluate_pair  # noqa: E402
from build_figma_canvas import apply_auto_layout  # noqa: E402
from discover_oss_components import scan_project_categories, search_local  # noqa: E402
from render_design_bible import build_html, sync_markdown_token_tables  # noqa: E402
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


class V22UpgradeTests(unittest.TestCase):
    def test_v22_harmony_monochrome_dark_and_washed_out_light(self):
        # 1. Tokens v2.2.0 calibrados (65/20/10/5) passam com 0 BLOCK e 0 achados de monocromia/light-lavado
        good_rows = audit_file(ROOT / "assets" / "tokens.example.json")
        self.assertFalse(any(r["severity"] == "BLOCK" for r in good_rows))
        self.assertFalse(any("DA-DARK-MONOCHROME" in r["label"] for r in good_rows))
        self.assertFalse(any("DA-LIGHT-WASHED-OUT" in r["label"] for r in good_rows))

        # 2. Dark tudo-azul saturado (S > 45%) dispara DA-DARK-MONOCHROME; Light com borda lavada dispara DA-LIGHT-WASHED-OUT
        bad_css = """
        :root, [data-theme="light"] {
          --surface-z1: #F5F7FA;
          --surface-z2: #FFFFFF;
          --border-subtle: #EAEFF5;
          --primary: #1F5CB8;
          --text-strong: #101822;
        }
        [data-theme="dark"] {
          --surface-z1: #0B1522;
          --surface-z2: #122033;
          --border-subtle: #243852;
          --primary: #76B8FA;
          --text-strong: #F3F6FA;
        }
        """
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.css"
            p.write_text(bad_css, encoding="utf-8")
            rows = audit_file(p)
        labels = [r["label"] for r in rows]
        self.assertTrue(any("DA-DARK-MONOCHROME" in lb for lb in labels), labels)
        self.assertTrue(any("DA-LIGHT-WASHED-OUT" in lb for lb in labels), labels)

    def test_v22_categorical_project_scanner_and_icon_recipes(self):
        # Escaneia um mini projeto simulando financeiro + licitacoes + whatsapp bot + mobile
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "CONCEPCAO.md").write_text(
                "Sistema ERP financeiro com contas a pagar, fluxo de caixa 45 dias, grafico DRE cascata, "
                "radar de editais PNCP, funil kanban arrastavel, agenda de prazos .ics, inbox WhatsApp SLA 24h com bot e transbordo, "
                "importacao PDF/OFX e app mobile executivo para socios.",
                encoding="utf-8",
            )
            rep = scan_project_categories(scan_path=proj, stack="html", platform="all", mode="operate")
        cat_ids = {c["id"] for c in rep["categories"]}
        for expected in (
            "shell-navigation",
            "icons-emblems-avatars",
            "badges-chips-timers-status",
            "charts-telemetry-financial",
            "data-tables-lists-progressive",
            "kanban-drag-drop-workflows",
            "calendar-gantt-timelines",
            "inbox-chat-omnichannel-ai",
            "mobile-native-pwa-touch",
        ):
            self.assertIn(expected, cat_ids)

        # Verifica presenca de bibliotecas sofisticadas e receitas de icones/badges
        chart_cat = next(c for c in rep["categories"] if c["id"] == "charts-telemetry-financial")
        chart_names = {it["name"] for it in chart_cat["adopt_oss"]}
        self.assertTrue(any("Lightweight Charts" in n or "ECharts" in n for n in chart_names), chart_names)

        badge_cat = next(c for c in rep["categories"] if c["id"] == "badges-chips-timers-status")
        recipe_ids = {r["id"] for r in badge_cat["studio_recipes"]}
        self.assertIn("sla-progress-ring-pill", recipe_ids)
        self.assertIn("halo-status-vector-chip", recipe_ids)

    def test_v22_lint_generic_icons_flat_chart_and_bible_hex_sync(self):
        # 1. Repeticao de ph-bank >= 5x dispara DA-ICON-GENERIC-REPEAT; yAxis min: 0 sem bar dispara DA-FLAT-CHART-AXIS
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "desktop-caixa.html"
            p.write_text(
                "<div>" + '<i class="ph ph-bank"></i>' * 6 + "</div>"
                "<script>echarts.init(el).setOption({ yAxis: { type: 'value', min: 0 }, series: [{ type: 'line', data: [3400, 3350] }] });</script>",
                encoding="utf-8",
            )
            findings = scan_file(p, Path(tmp))
        rules = {f["rule"] for f in findings}
        self.assertIn("DA-ICON-GENERIC-REPEAT", rules)
        self.assertIn("DA-FLAT-CHART-AXIS", rules)

        # 2. render_design_bible sincroniza hexes defasados na tabela 8.1 contra tokens.css
        stale_md = "| `--surface-z1` | `#0B1522` | `#F1F4F8` |\n"
        synced, vars_changed = sync_markdown_token_tables(
            stale_md,
            tokens_light={"--surface-z1": "#E6ECF3"},
            tokens_dark={"--surface-z1": "#0E131D"},
        )
        self.assertIn("--surface-z1", vars_changed)
        self.assertIn("#0E131D", synced)
        self.assertIn("#E6ECF3", synced)
        self.assertNotIn("#0B1522", synced)

    def test_v221_mobile_flex_clip_and_preview_bezel_and_brand_light_tokens(self):
        # 1. CSS .mob-scroll flex-column sem flex-shrink: 0 dispara DA-MOBILE-FLEX-CLIP
        with tempfile.TemporaryDirectory() as tmp:
            bad_css = Path(tmp) / "shell.css"
            bad_css.write_text(".mob-scroll { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }", encoding="utf-8")
            bad_findings = scan_file(bad_css, Path(tmp))
            self.assertIn("DA-MOBILE-FLEX-CLIP", {f["rule"] for f in bad_findings})

            good_css = Path(tmp) / "shell-ok.css"
            good_css.write_text(
                ".mob-scroll { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }\n"
                ".mob-scroll > * { flex-shrink: 0; }",
                encoding="utf-8",
            )
            good_findings = scan_file(good_css, Path(tmp))
            self.assertNotIn("DA-MOBILE-FLEX-CLIP", {f["rule"] for f in good_findings})

        # 2. preview.html usa wrapper .pv-frame-wrap.is-mobile com clip-path (nunca iframe pelado vazando canto quadrado)
        manifest = {
            "project": {"name": "Mob", "startScreenId": "m1"},
            "screens": [{"id": "m1", "title": "Pulso", "file": "m1.html", "platform": "mobile", "flow": "mobile", "group": "Mobile"}],
            "edges": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "m1.html").write_text("<!doctype html><title>M1</title>", encoding="utf-8")
            mpath = folder / "screen-manifest.json"
            mpath.write_text(json.dumps(manifest), encoding="utf-8")
            proc = run_py("build_figma_canvas.py", [str(mpath), "--out", str(folder), "--verify-files"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            preview = (folder / "preview.html").read_text(encoding="utf-8")
            self.assertIn("pv-frame-wrap", preview)
            self.assertIn("clip-path: inset(0 round 32px)", preview)

        # 3. tokens.example.json inclui tokens de Modo Claro Ancorado pela Marca e passa 30/30 sem BLOCK/HIGH/MEDIUM
        tok = json.loads((ROOT / "assets" / "tokens.example.json").read_text(encoding="utf-8"))
        self.assertIn("surface-brand-dark", tok["semantic"]["light"])
        self.assertIn("surface-tint-soft", tok["semantic"]["light"])
        self.assertIn("surface-brand-dark", tok["semantic"]["dark"])
        rows = audit_file(ROOT / "assets" / "tokens.example.json")
        self.assertFalse(any(r["severity"] in ("BLOCK", "HIGH", "MEDIUM") for r in rows), [r for r in rows if r["severity"] != "PASS"])

    def test_v23_vitrine_hub_grouping_accented_labels_preview_picker_and_lint_rules(self):
        # 1. Hub-and-Spoke nao rouba Contas a Pagar nem Bot/Ajustes para coluna Acesso & Conta
        manifest = {
            "project": {"name": "Sistema Demo", "startScreenId": "entrada"},
            "screens": [
                {"id": "entrada", "title": "Entrada & 2FA", "file": "entrada.html", "platform": "desktop", "flow": "nucleo", "group": "Acesso"},
                {"id": "portal", "title": "Portal Central", "file": "portal.html", "platform": "desktop", "flow": "nucleo", "group": "Hub"},
                {"id": "pref", "title": "Preferencias", "file": "pref.html", "platform": "desktop", "flow": "nucleo", "group": "Conta"},
                {"id": "pagar", "title": "Contas a Pagar", "file": "pagar.html", "platform": "desktop", "flow": "financeiro", "sectionId": "sec-fin", "group": "Financeiro"},
                {"id": "receber", "title": "Contas a Receber", "file": "receber.html", "platform": "desktop", "flow": "financeiro", "sectionId": "sec-fin", "group": "Financeiro"},
                {"id": "bot", "title": "Bot · Simulador e Ajustes", "file": "bot.html", "platform": "desktop", "flow": "atendimento", "sectionId": "sec-atend", "group": "Atendimento"},
                {"id": "editais", "title": "Radar de Editais", "file": "editais.html", "platform": "desktop", "flow": "licitacoes", "sectionId": "sec-lic", "group": "Licitacoes"},
                {"id": "mob1", "title": "Pulso Mobile", "file": "mob1.html", "platform": "mobile", "flow": "socios-mobile", "sectionId": "sec-mob", "group": "Mobile"},
            ],
            "edges": [
                {"id": "e1", "from": "entrada", "to": "portal", "label": "Entrar", "flow": "nucleo"},
                {"id": "e2", "from": "portal", "to": "pagar", "label": "Pagar", "flow": "financeiro"},
                {"id": "e3", "from": "portal", "to": "editais", "label": "Editais", "flow": "licitacoes"},
                {"id": "e4", "from": "portal", "to": "bot", "label": "Atendimento", "flow": "atendimento"},
            ],
            "journeys": [
                {"id": "j1", "name": "Diretoria · Rotina Financeira Completa", "steps": [{"screenId": "entrada", "short": "Acesso", "title": "Acesso", "tip": "Entrar"}]},
                {"id": "j2", "name": "Analista · Licitações e Certidões", "steps": [{"screenId": "editais", "short": "Editais", "title": "Editais", "tip": "Filtrar"}]},
                {"id": "j3", "name": "Operação · Atendimento Omnichannel", "steps": [{"screenId": "bot", "short": "Bot", "title": "Bot", "tip": "Testar"}]},
                {"id": "j4", "name": "Sócios · App Executivo Mobile", "steps": [{"screenId": "mob1", "short": "Pulso", "title": "Pulso", "tip": "Conferir"}]},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            thumbs = folder / "shots"
            thumbs.mkdir()
            for s in manifest["screens"]:
                (folder / s["file"]).write_text("<!doctype html><title>T</title>", encoding="utf-8")
            # Mini PNG placeholder para testar --thumbs em index.html
            (thumbs / "portal-desktop-dark.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            (thumbs / "portal-desktop-light.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            (folder / "tokens.css").write_text(
                ':root { --surface-z0: #CFDCEB; --surface-z1: #E1EAF4; --surface-z2: #FFFFFF; --surface-brand-dark: #0E294B; --accent: #C2410C; }\n'
                'html[data-theme="dark"] { --surface-z0: #080C12; --surface-z1: #0E131D; --surface-z2: #141C29; --accent: #FF945E; }\n',
                encoding="utf-8",
            )
            mpath = folder / "screen-manifest.json"
            mpath.write_text(json.dumps(manifest), encoding="utf-8")
            proc = run_py("build_figma_canvas.py", [str(mpath), "--tokens", str(folder / "tokens.css"), "--thumbs", str(thumbs), "--out", str(folder), "--verify-files"])
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

            fluxo = (folder / "fluxo.html").read_text(encoding="utf-8")
            preview = (folder / "preview.html").read_text(encoding="utf-8")
            index = (folder / "index.html").read_text(encoding="utf-8")

            # Sem fundo bege #D9D6CE; filtros acentuados; Contas a Pagar / Bot ficaram nas suas raias
            self.assertNotIn("#D9D6CE", fluxo)
            self.assertIn("Núcleo", fluxo)
            self.assertIn("Licitações", fluxo)
            self.assertIn("App Sócios", fluxo)
            self.assertIn("ACESSO & CONTA (2)", fluxo)  # somente entrada + pref, nunca pagar/receber/bot!
            # preview.html usa select limpo para 4 jornadas sem overflow horizontal
            self.assertIn('id="journeySelect"', preview)
            # index.html embutiu miniatura dark/light via --thumbs
            self.assertIn("portal-desktop-dark.png", index)
            self.assertIn("portal-desktop-light.png", index)

        # 2. Linter v2.3.0: DA-BRAND-DARK-SCOPE e DA-REF-COPY-LEAK
        with tempfile.TemporaryDirectory() as tmp:
            bad_css = Path(tmp) / "shell-bad.css"
            bad_css.write_text('html[data-theme="light"] .card-brand-hero { background: var(--surface-brand-dark); color: #fff; }', encoding="utf-8")
            self.assertIn("DA-BRAND-DARK-SCOPE", {f["rule"] for f in scan_file(bad_css, Path(tmp))})

            ok_css = Path(tmp) / "shell-ok.css"
            ok_css.write_text(
                'html[data-theme="light"] .card-brand-hero { background: var(--surface-brand-dark); --text-strong: #fff; --text-muted: #B8CCE5; }',
                encoding="utf-8",
            )
            self.assertNotIn("DA-BRAND-DARK-SCOPE", {f["rule"] for f in scan_file(ok_css, Path(tmp))})

            leak_html = Path(tmp) / "desktop-home.html"
            leak_html.write_text("<main><p>Painel estilo Linear com janelas TOTVS.</p></main>", encoding="utf-8")
            self.assertIn("DA-REF-COPY-LEAK", {f["rule"] for f in scan_file(leak_html, Path(tmp))})


class V24UpgradeTests(unittest.TestCase):
    def test_v24_semantic_hue_parity_dark_monolith_strict_light_and_enriched_tokens(self):
        # 1. tokens.example.json v2.4.0 gera superficies semanticas, cabecalho marca e sombras Dark/Light calibradas
        with tempfile.TemporaryDirectory() as tmp:
            out_css = Path(tmp) / "tokens.css"
            proc = run_py(
                "generate_tokens.py",
                [str(ROOT / "assets" / "tokens.example.json"), "--out", str(out_css), "--check-contrast"],
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            css_text = out_css.read_text(encoding="utf-8")
            for expected_tok in (
                "--danger-surface:",
                "--danger-border:",
                "--danger-text:",
                "--success-surface:",
                "--surface-brand-header:",
                "--rim-highlight:",
            ):
                self.assertIn(expected_tok, css_text)
            rows = audit_file(out_css)
            self.assertGreaterEqual(len(rows), 40)
            self.assertFalse(any(r["severity"] != "PASS" for r in rows), [r for r in rows if r["severity"] != "PASS"])

        # 2. Erro rosa pastel (#FDA4AF) no Dark -> BLOCK DA-SEMANTIC-HUE-PARITY;
        #    Light com borda 1.52:1 (< 1.85:1) -> HIGH DA-LIGHT-WASHED-OUT;
        #    Dark monobloco cinza chapado -> HIGH DA-DARK-FLAT-MONOLITH
        bad_css = """
        [data-theme="light"] {
          --surface-z1: #EFF3F8;
          --surface-z2: #FFFFFF;
          --border-subtle: #C8D3E0;
          --primary: #14427A;
          --on-primary: #FFFFFF;
          --danger: #B91C1C;
          --on-danger: #FFFFFF;
          --success: #15803D;
          --on-success: #FFFFFF;
          --text-strong: #0E1726;
        }
        [data-theme="dark"] {
          --surface-z1: #14181F;
          --surface-z2: #161B23;
          --border-subtle: #1D232E;
          --primary: #2563EB;
          --on-primary: #FFFFFF;
          --danger: #FDA4AF;
          --on-danger: #190808;
          --success: #2DD4BF;
          --on-success: #071510;
          --text-strong: #F3F6FB;
        }
        """
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad-v24.css"
            p.write_text(bad_css, encoding="utf-8")
            rows = audit_file(p)
        labels = [r["label"] for r in rows]
        self.assertTrue(any("DA-SEMANTIC-HUE-PARITY" in lb and r["severity"] == "BLOCK" for r, lb in zip(rows, labels)), rows)
        self.assertTrue(any("DA-LIGHT-WASHED-OUT" in lb for lb in labels), labels)
        self.assertTrue(any("DA-DARK-FLAT-MONOLITH" in lb for lb in labels), labels)

    def test_v24_lint_tech_jargon_and_badge_echo(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "desktop-fila.html"
            p.write_text(
                "<main><p>Fallback VLM ativo na Fila FIFO com deviceId.</p>"
                + '<span class="badge-status">Aguardando Mesa</span>' * 6
                + "</main>",
                encoding="utf-8",
            )
            findings = scan_file(p, Path(tmp))
        rules = {f["rule"] for f in findings}
        self.assertIn("DA-TECH-JARGON-UI", rules)
        self.assertIn("DA-BADGE-ECHO", rules)

    def test_v24_bible_squircle_specimens_and_entrega_hub_spa(self):
        # 1. Biblia PDF usa squircle 6px + barra de decisao + diff strip (sem .sp-pill 999px)
        page = build_html(
            "# Biblia v2.4\n\n## 1. Teste\n",
            "Biblia v2.4",
            tokens_light={"--surface-z1": "#D9E5F3", "--surface-z2": "#FFFFFF", "--danger": "#B91C1C"},
            tokens_dark={"--surface-z1": "#101620", "--surface-z2": "#17202E", "--danger": "#DC2626"},
        )
        self.assertIn("sp-squircle", page)
        self.assertIn("sp-diff-strip", page)
        self.assertIn("sp-tabs", page)
        self.assertNotIn("sp-pill", page)

        # 2. build_figma_canvas suporta SPA route + --app-base e gera entrega.html com Biblia/PDF e 3-channel sync
        manifest = {
            "project": {"name": "Portal Operacional", "startScreenId": "fila"},
            "screens": [
                {"id": "fila", "title": "Fila Operacional", "route": "/fila", "platform": "desktop", "flow": "operacao", "group": "Mesa"},
                {"id": "campo", "title": "App Campo", "route": "/campo", "platform": "mobile", "flow": "mobile", "group": "Campo"},
            ],
            "edges": [{"id": "e1", "from": "fila", "to": "campo", "label": "Ver Mobile", "flow": "mobile"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "DESIGN-BIBLE.html").write_text("<!doctype html><title>B</title>", encoding="utf-8")
            (folder / "DESIGN-BIBLE.pdf").write_bytes(b"%PDF-1.4\n")
            mpath = folder / "screen-manifest.json"
            mpath.write_text(json.dumps(manifest), encoding="utf-8")
            proc = run_py("build_figma_canvas.py", [str(mpath), "--app-base", "/app", "--out", str(folder), "--verify-files"])
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            entrega = (folder / "entrega.html").read_text(encoding="utf-8")
            self.assertIn('class="da-hub"', entrega)
            self.assertIn("App ao Vivo", entrega)
            self.assertIn("Bíblia Visual", entrega)
            self.assertIn("DESIGN-BIBLE.pdf", entrega)
            self.assertIn("designaura:theme", entrega)

    def test_v24_serve_entrega_and_workflow_probe_e2e(self):
        import socket
        import time
        import urllib.request

        # Escolhe porta livre
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            design_dir = base / "design"
            dist_dir = base / "dist"
            design_dir.mkdir()
            dist_dir.mkdir()
            (dist_dir / "index.html").write_text("<!doctype html><title>SPA</title><main>App SPA Vivo</main>", encoding="utf-8")
            (design_dir / "tela-fila.html").write_text(
                """<!doctype html><html lang="pt-BR" data-theme="dark"><head><meta charset="utf-8"><title>Fila</title>
                <style>
                  body { margin: 0; font-family: system-ui, sans-serif; background: #101620; color: #D6E1F0; }
                  main { padding: 24px; min-height: 100dvh; box-sizing: border-box; }
                  .list { display: grid; gap: 10px; }
                  .row { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-radius: 12px; background: #17202E; border: 1px solid #2C3E58; color: #F3F6FB; cursor: pointer; font-size: 14px; }
                  .conf { margin-top: 16px; padding: 20px; border-radius: 14px; background: #17202E; border: 1px solid #3B7CF0; }
                  .conf[hidden] { display: none; }
                  button { min-height: 44px; padding: 0 16px; border-radius: 8px; border: 1px solid #15803D; background: #15803D; color: #FFFFFF; font-weight: 700; cursor: pointer; }
                  #toast { margin-top: 12px; font-weight: 700; color: #4ADE80; }
                </style></head><body><main>
                  <h1 style="color:#F3F6FB;margin:0 0 14px;">Fila de Conferência</h1>
                  <div class="list">
                    <button type="button" class="row" data-da-open="1" onclick="document.getElementById('conf').hidden=false"><span>Ana Paula · Unidade Norte</span><span>Falta indevida</span></button>
                    <button type="button" class="row"><span>Carlos Lima · Unidade Sul</span><span>Horário</span></button>
                    <button type="button" class="row"><span>Marina Alves · Unidade Centro</span><span>Atestado</span></button>
                    <button type="button" class="row"><span>Pedro Souza · Unidade Leste</span><span>Falta</span></button>
                    <button type="button" class="row"><span>Lucia Dias · Unidade Oeste</span><span>Batida</span></button>
                  </div>
                  <section id="conf" class="conf" hidden>
                    <h2 style="color:#F3F6FB;margin:0 0 10px;">Conferência · Ana Paula</h2>
                    <label for="obs">Observação</label>
                    <input id="obs" type="text" placeholder="Motivo" style="display:block;margin:8px 0;padding:10px;min-height:44px;background:#090E16;color:#F3F6FB;border:1px solid #2C3E58;border-radius:8px;">
                    <button type="button" id="btnApprove" onclick="document.getElementById('toast').textContent='Solicitação aprovada com sucesso'">Aprovar solicitação</button>
                    <p id="toast"></p>
                  </section>
                </main></body></html>""",
                encoding="utf-8",
            )
            manifest = {
                "project": {"name": "E2E", "startScreenId": "fila"},
                "screens": [{"id": "fila", "title": "Fila", "file": "tela-fila.html", "platform": "desktop", "flow": "op", "group": "Op", "clickSelector": "[data-da-open]"}],
                "edges": [],
            }
            mpath = design_dir / "screen-manifest.json"
            mpath.write_text(json.dumps(manifest), encoding="utf-8")
            build = run_py("build_figma_canvas.py", [str(mpath), "--out", str(design_dir), "--verify-files"])
            self.assertEqual(build.returncode, 0, build.stderr)

            # 1. Testa serve_entrega.mjs em 1 porta combinando / + /design/* + /app/* SPA
            srv = subprocess.Popen(
                ["node", str(SCRIPTS / "serve_entrega.mjs"), "--design-dir", str(design_dir), "--app-dir", str(dist_dir), "--port", str(port), "--host", "127.0.0.1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                for _ in range(30):
                    try:
                        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=1) as resp:
                            if resp.status == 200:
                                break
                    except Exception:
                        time.sleep(0.1)
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2) as r_root:
                    self.assertIn("da-hub", r_root.read().decode("utf-8"))
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/app/rota-dinamica", timeout=2) as r_spa:
                    self.assertIn("App SPA Vivo", r_spa.read().decode("utf-8"))

                # 2. Testa run_workflow_probe.mjs (Fase 4.5) clicando no fluxo real via Chromium CDP
                scenario = {
                    "name": "Fluxo Resize e Aprovacao",
                    "viewport": "desktop",
                    "theme": "dark",
                    "steps": [
                        {"action": "goto", "url": "/design/tela-fila.html"},
                        {"action": "assertHidden", "selector": "#conf"},
                        {"action": "click", "selector": "[data-da-open]"},
                        {"action": "assertVisible", "selector": "#conf"},
                        {"action": "fill", "selector": "#obs", "value": "Conferido no cartao"},
                        {"action": "click", "selector": "#btnApprove"},
                        {"action": "assertText", "selector": "#toast", "contains": "aprovada com sucesso"},
                        {"action": "assertNoOverflow"},
                        {"action": "setTheme", "theme": "light"},
                        {"action": "screenshot", "name": "apos-aprovacao"},
                    ],
                }
                spath = base / "qa.json"
                spath.write_text(json.dumps(scenario), encoding="utf-8")
                qa_out = base / "qa-out"
                probe = subprocess.run(
                    ["node", str(SCRIPTS / "run_workflow_probe.mjs"), "--scenario", str(spath), "--base-url", f"http://127.0.0.1:{port}", "--out", str(qa_out), "--strict"],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(probe.returncode, 0, probe.stdout + probe.stderr)
                self.assertTrue((qa_out / "apos-aprovacao.png").exists())
                rep = json.loads((qa_out / "probe-report.json").read_text(encoding="utf-8"))
                self.assertTrue(rep["passed"])

                # 3. Testa capture_and_audit.mjs com entrega.html whitelisted + --smoke-interact + --base-url no servidor unificado
                audit_out = base / "audit-out"
                aud = subprocess.run(
                    ["node", str(SCRIPTS / "capture_and_audit.mjs"), "--manifest", str(mpath), "--base-url", f"http://127.0.0.1:{port}", "--out", str(audit_out), "--viewports", "desktop", "--themes", "dark", "--concurrency", "2", "--smoke-interact", "--strict"],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(aud.returncode, 0, aud.stdout + aud.stderr)
                self.assertTrue((audit_out / "fila-desktop-dark-interact.png").exists())
                self.assertTrue((audit_out / "entrega-desktop-dark.png").exists())
                aud_rep = json.loads((audit_out / "audit-report.json").read_text(encoding="utf-8"))
                entrega_row = next(r for r in aud_rep if r["target"] == "entrega")
                self.assertIn(f"127.0.0.1:{port}/entrega.html", entrega_row["url"])
            finally:
                srv.terminate()
                try:
                    srv.wait(timeout=3)
                except Exception:
                    srv.kill()
                if srv.stdout:
                    srv.stdout.close()
                if srv.stderr:
                    srv.stderr.close()

    def test_v241_bible_sync_respects_light_dark_column_header_for_dark_semantic_tokens(self):
        # Antes da v2.4.1, --danger (#B91C1C Light vs #DC2626 Dark) e --primary (#14427A Light vs #2563EB Dark)
        # tinham soma RGB < 380 nos dois modos e invertiam colunas Light|Dark!
        md = (
            "| Token | Light | Dark |\n"
            "|---|---|---|\n"
            "| `--danger` | `#AA0000` | `#FDA4AF` |\n"
            "| `--primary` | `#0F2942` | `#6EB5FF` |\n"
            "\n"
            "| Token | Escuro | Claro |\n"
            "|---|---|---|\n"
            "| `--danger` | `#FDA4AF` | `#AA0000` |\n"
        )
        synced, changed = sync_markdown_token_tables(
            md,
            tokens_light={"--danger": "#B91C1C", "--primary": "#14427A"},
            tokens_dark={"--danger": "#DC2626", "--primary": "#2563EB"},
        )
        self.assertIn("--danger", changed)
        self.assertIn("--primary", changed)
        lines = synced.splitlines()
        self.assertEqual(lines[2], "| `--danger` | `#B91C1C` | `#DC2626` |")
        self.assertEqual(lines[3], "| `--primary` | `#14427A` | `#2563EB` |")
        self.assertEqual(lines[7], "| `--danger` | `#DC2626` | `#B91C1C` |")


if __name__ == "__main__":
    unittest.main()
