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


class BiblePaperTests(unittest.TestCase):
    def test_paper_has_no_fixed_board(self):
        sample = "# Biblia\n\n## 8. Arsenal\n\n| Peça | Caminho |\n|---|---|\n| Tabela | `npm install @tanstack/react-table` |\n"
        page = build_html(sample, "Biblia")
        self.assertNotIn("overflow: hidden", page)
        self.assertNotIn("height: 210mm", page)
        self.assertIn("<table>", page)
        self.assertIn("npm install", page)


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


if __name__ == "__main__":
    unittest.main()
