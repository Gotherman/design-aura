#!/usr/bin/env python3
"""Mantem a base de componentes viva sem mudar nada sozinho.

Para cada entrada com repositorio GitHub (ou pacote npm no campo install), consulta a licenca atual,
se o repositorio foi arquivado e a data do ultimo push. Gera um relatorio de diferencas para revisao
humana. Com --mark-checked, grava license_checked_at apenas nas entradas cuja licenca confere.

    python3 refresh_catalog.py --category charts --limit 20
    GITHUB_TOKEN=... python3 refresh_catalog.py --mark-checked      # sem token, o GitHub limita a 60 consultas/hora
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "data" / "catalog"
SPDX_EQUIV = {"MIT": "MIT", "Apache-2.0": "Apache-2.0", "ISC": "ISC", "BSD-3-Clause": "BSD-3-Clause", "BSD-2-Clause": "BSD-2-Clause",
              "MPL-2.0": "MPL-2.0", "CC0-1.0": "CC0-1.0", "Unlicense": "Unlicense", "AGPL-3.0": "AGPL-3.0", "GPL-3.0": "GPL-3.0"}


def get_json(url: str) -> dict:
    headers = {"User-Agent": "design-aura-catalog-refresh", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as res:
        return json.loads(res.read().decode("utf-8"))


def github_slug(entry: dict) -> str | None:
    for field in ("repo", "url"):
        m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", entry.get(field) or "")
        if m:
            return f"{m.group(1)}/{m.group(2).removesuffix('.git')}"
    return None


def npm_name(entry: dict) -> str | None:
    m = re.search(r"(?:npm install|npx expo install)(?: -D)? (?!https?:)(@?[a-z0-9][a-z0-9._/-]*)", entry.get("install") or "")
    return m.group(1) if m else None


def license_family(text: str) -> str:
    for spdx in SPDX_EQUIV:
        if spdx.lower() in (text or "").lower():
            return spdx
    return (text or "").strip()


def check(entry: dict) -> dict:
    out = {"id": entry["id"], "name": entry["name"], "catalog_license": entry.get("license", ""), "sources": []}
    slug = github_slug(entry)
    if slug:
        try:
            repo = get_json(f"https://api.github.com/repos/{slug}")
            spdx = ((repo.get("license") or {}).get("spdx_id") or "").strip()
            out["sources"].append({"github": slug, "license": spdx, "archived": repo.get("archived"), "pushed_at": repo.get("pushed_at")})
        except Exception as exc:  # noqa: BLE001
            out["sources"].append({"github": slug, "error": str(exc)[:120]})
    pkg = npm_name(entry)
    if pkg:
        try:
            meta = get_json(f"https://registry.npmjs.org/{urllib.parse.quote(pkg, safe='@/')}")
            latest = (meta.get("dist-tags") or {}).get("latest")
            vmeta = (meta.get("versions") or {}).get(latest) or {}
            lic = vmeta.get("license") or meta.get("license") or ""
            lic = lic.get("type", "") if isinstance(lic, dict) else str(lic)
            out["sources"].append({"npm": pkg, "version": latest, "license": lic, "modified": (meta.get("time") or {}).get("modified")})
        except Exception as exc:  # noqa: BLE001
            out["sources"].append({"npm": pkg, "error": str(exc)[:120]})
    flags = []
    cat_family = license_family(entry.get("license", ""))
    for src in out["sources"]:
        lic = src.get("license")
        if lic and lic not in ("NOASSERTION", "") and cat_family and license_family(lic) != cat_family:
            flags.append(f"licenca mudou? catalogo={entry.get('license')} fonte={lic}")
        if src.get("archived"):
            flags.append("repositorio arquivado")
        stamp = src.get("pushed_at") or src.get("modified")
        if stamp:
            age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))).days
            if age > 540:
                flags.append(f"sem atividade ha {age} dias")
    out["flags"] = flags
    # Licenca confirmada e atividade sao coisas separadas: um projeto parado continua com a licenca conferida,
    # mas sai marcado como stale e perde posicao no ranking.
    license_flags = [f for f in flags if f.startswith("licenca")]
    out["archived"] = any(s.get("archived") for s in out["sources"])
    out["stale"] = out["archived"] or any(f.startswith("sem atividade") for f in flags)
    out["confirmed"] = bool(out["sources"]) and not license_flags and any(s.get("license") for s in out["sources"])
    return out


def main():
    ap = argparse.ArgumentParser(description="Confere licencas e atividade da base de componentes.")
    ap.add_argument("--category", default="", help="Arquivo da base (ex.: charts)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--mark-checked", action="store_true", help="Grava license_checked_at nas entradas confirmadas")
    ap.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = ap.parse_args()

    files = [CATALOG / f"{args.category}.json"] if args.category else sorted(CATALOG.glob("*.json"))
    results, today = [], dt.date.today().isoformat()
    for path in files:
        entries = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for entry in entries:
            if entry.get("use") == "reference" and entry.get("kind") != "license-trap":
                continue
            if args.limit and len(results) >= args.limit:
                break
            if not (github_slug(entry) or npm_name(entry)):
                continue
            res = check(entry)
            results.append(res)
            if args.mark_checked and res["confirmed"]:
                entry["license_checked_at"] = today
                if res["stale"]:
                    entry["stale"] = True
                else:
                    entry.pop("stale", None)
                changed = True
        if changed:
            path.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    flagged = [r for r in results if r["flags"]]
    print(f"# Atualizacao da base: {len(results)} conferidas, {len(flagged)} com alerta")
    for r in flagged:
        print(f"- **{r['name']}** (`{r['id']}`): {'; '.join(r['flags'])}")
    errors = [r for r in results if any("error" in s for s in r["sources"])]
    if errors:
        print(f"\n{len(errors)} consulta(s) falharam (limite do GitHub sem GITHUB_TOKEN ou rede).")
    print("\nRevise cada alerta antes de mudar license_status no JSON. Nada foi alterado sem --mark-checked.")


if __name__ == "__main__":
    sys.exit(main())
