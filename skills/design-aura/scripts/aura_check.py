#!/usr/bin/env python3
"""Um comando para todos os portoes da Design Aura.

    python3 aura_check.py --manifest design/screen-manifest.json --tokens design/tokens.css \\
        --bible design/DESIGN-BIBLE.md --shell design/SHELL-CONTRACT.md --project design/telas \\
        --out design/audit [--base-url http://127.0.0.1:4188] [--smoke-interact] [--baseline design/audit-antes] --strict

Roda, conforme os caminhos informados: contraste dos tokens, linter estatico, captura e auditoria no
navegador, completude da Biblia (com zonas do manifesto) e sincronia Biblia/shell/tokens. Grava
aura-check.json com o resultado de cada portao e imprime um resumo unico.
BLOCK e HIGH falham em --strict; REVIEW vai para a inspecao visual.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def count(findings: list[dict]) -> dict:
    out = {k: 0 for k in ("BLOCK", "HIGH", "REVIEW", "MEDIUM")}
    for f in findings:
        if f.get("severity") in out:
            out[f["severity"]] += 1
    return out


def main():
    ap = argparse.ArgumentParser(description="Roda todos os portoes da Design Aura de uma vez.")
    ap.add_argument("--manifest")
    ap.add_argument("--tokens")
    ap.add_argument("--bible")
    ap.add_argument("--shell")
    ap.add_argument("--project", action="append", default=[], help="Pasta ou arquivo para o linter (repita)")
    ap.add_argument("--out", default="audit")
    ap.add_argument("--base-url", default="")
    ap.add_argument("--viewports", default="desktop,mobile")
    ap.add_argument("--themes", default="dark,light")
    ap.add_argument("--mode", default="", help="operate, read ou persuade (padrao: o do manifesto)")
    ap.add_argument("--baseline", default="")
    ap.add_argument("--concurrency", default="4")
    ap.add_argument("--smoke-interact", action="store_true")
    ap.add_argument("--depth-style", default="")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    gates = []

    if args.tokens:
        cmd = [sys.executable, str(SCRIPTS / "audit_contrast.py"), args.tokens, "--format", "json"]
        if args.depth_style:
            cmd += ["--depth-style", args.depth_style]
        code, text = run(cmd)
        try:
            rows = json.loads(text)
        except json.JSONDecodeError:
            rows = [{"severity": "BLOCK", "label": "audit_contrast falhou", "reason": text[:400]}]
        gates.append({"gate": "contraste", "counts": count(rows), "details": [r for r in rows if r.get("severity") != "PASS"]})

    if args.project:
        code, text = run([sys.executable, str(SCRIPTS / "lint_design_aura.py"), *args.project, "--format", "json"])
        try:
            data = json.loads(text)
            findings = data["findings"]
        except (json.JSONDecodeError, KeyError):
            findings = [{"severity": "BLOCK", "rule": "lint", "message": text[:400]}]
        gates.append({"gate": "linter", "counts": count(findings), "details": findings})

    if args.manifest:
        cmd = ["node", str(SCRIPTS / "capture_and_audit.mjs"), "--manifest", args.manifest, "--out", str(out / "captures"),
               "--viewports", args.viewports, "--themes", args.themes, "--concurrency", args.concurrency, "--quiet"]
        if args.base_url:
            cmd += ["--base-url", args.base_url]
        if args.mode:
            cmd += ["--mode", args.mode]
        if args.baseline:
            cmd += ["--baseline", args.baseline]
        if args.smoke_interact:
            cmd += ["--smoke-interact"]
        code, text = run(cmd)
        report_path = out / "captures" / "audit-report.json"
        findings, rows = [], []
        if report_path.exists():
            rows = json.loads(report_path.read_text(encoding="utf-8"))
            for row in rows:
                for issue in row.get("issues", []):
                    findings.append({**issue, "where": f"{row.get('target')} · {row.get('viewport')} · {row.get('theme')}", "screenshot": row.get("screenshot")})
        else:
            findings.append({"severity": "BLOCK", "rule": "DA-AUDIT-COVERAGE", "detail": text[-600:]})
        gates.append({"gate": "navegador", "counts": count(findings), "details": findings, "captures": len(rows)})

    if args.bible:
        cmd = [sys.executable, str(SCRIPTS / "render_design_bible.py"), args.bible, "--check"]
        if args.tokens:
            cmd += ["--tokens", args.tokens]
        if args.manifest:
            cmd += ["--manifest", args.manifest]
        code, text = run(cmd)
        problems = [ln[2:] for ln in text.splitlines() if ln.startswith("- ")]
        gates.append({"gate": "biblia", "counts": {"BLOCK": 0, "HIGH": len(problems), "REVIEW": 0, "MEDIUM": 0},
                      "details": [{"severity": "HIGH", "message": p} for p in problems]})
        if args.tokens:
            cmd = [sys.executable, str(SCRIPTS / "render_design_bible.py"), args.bible, "--tokens", args.tokens, "--check-sync"]
            if args.shell:
                cmd += ["--shell", args.shell]
            code, text = run(cmd)
            drift = [] if code == 0 else [ln for ln in text.splitlines() if ln.strip()]
            gates.append({"gate": "sincronia", "counts": {"BLOCK": 0, "HIGH": len(drift), "REVIEW": 0, "MEDIUM": 0},
                          "details": [{"severity": "HIGH", "message": d} for d in drift]})

    total = {k: sum(g["counts"].get(k, 0) for g in gates) for k in ("BLOCK", "HIGH", "REVIEW", "MEDIUM")}
    (out / "aura-check.json").write_text(json.dumps({"total": total, "gates": gates}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("# Design Aura — verificação consolidada")
    print("| Portão | BLOCK | HIGH | REVIEW | MEDIUM |")
    print("|---|---:|---:|---:|---:|")
    for g in gates:
        c = g["counts"]
        print(f"| {g['gate']} | {c['BLOCK']} | {c['HIGH']} | {c['REVIEW']} | {c['MEDIUM']} |")
    print(f"| **total** | {total['BLOCK']} | {total['HIGH']} | {total['REVIEW']} | {total['MEDIUM']} |")
    for g in gates:
        top = [d for d in g["details"] if d.get("severity") in ("BLOCK", "HIGH")][:8]
        if top:
            print(f"\n## {g['gate']}: corrigir")
            for d in top:
                where = f" ({d['where']})" if d.get("where") else (f" ({d['location']})" if d.get("location") else "")
                print(f"- {d.get('severity')} {d.get('rule', '')} {d.get('detail') or d.get('message') or d.get('reason') or d.get('label', '')}{where}")
    reviews = [d for g in gates for d in g["details"] if d.get("severity") == "REVIEW"]
    if reviews:
        print(f"\n## REVIEW ({len(reviews)}): abrir a captura e confirmar ou dispensar com motivo")
        for d in reviews[:12]:
            print(f"- {d.get('rule', '')}: {d.get('detail') or d.get('message') or d.get('reason', '')}{' (' + d['where'] + ')' if d.get('where') else ''}")
    print(f"\nRelatório: {out / 'aura-check.json'}")
    if args.strict and (total["BLOCK"] or total["HIGH"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
