#!/usr/bin/env python3
"""Casa uma necessidade de interacao com componentes free/OSS e referencias visuais.

Modo offline: BM25 em registries_oss.json + components_oss.json.
Modo --online: completa com a API publica do GitHub e o registry do npm,
aceitando so licenca permissiva (MIT, Apache-2.0, BSD, ISC).
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from design_intel import BM25, match_platform, normalize_text  # noqa: E402

DATA_DIR = SCRIPT_DIR.parent / "data"
PERMISSIVE = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "0BSD",
    "Unlicense",
}
STACK_ALIASES = {
    "react": {"react", "tailwind", "all"},
    "vue": {"vue", "all"},
    "svelte": {"svelte", "all"},
    "solid": {"solid", "all"},
    "rn": {"rn", "expo", "react-native", "all"},
    "expo": {"rn", "expo", "all"},
    "flutter": {"flutter", "dart", "all"},
    "ios": {"ios", "swiftui", "all"},
    "swiftui": {"ios", "swiftui", "all"},
    "android": {"android", "compose", "all"},
    "compose": {"android", "compose", "all"},
    "electron": {"electron", "react", "desktop", "all"},
    "tauri": {"tauri", "react", "desktop", "all"},
    "html": {"html", "css", "tailwind", "all"},
    "all": {"all"},
}


def load_catalog() -> list[dict]:
    registries = json.loads((DATA_DIR / "registries_oss.json").read_text(encoding="utf-8"))
    components = json.loads((DATA_DIR / "components_oss.json").read_text(encoding="utf-8"))
    items = []
    for raw in registries:
        items.append(normalize_item(raw, "registries_oss.json"))
    for raw in components:
        items.append(normalize_item(raw, "components_oss.json"))
    return items


def normalize_item(raw: dict, catalog: str) -> dict:
    stacks = raw.get("stack", "all")
    if isinstance(stacks, str):
        stacks = [stacks]
    license_name = str(raw.get("license") or "")
    license_ok = raw.get("license_ok")
    if license_ok is None:
        license_ok = license_name in PERMISSIVE
    kind = raw.get("kind") or "library"
    modes = raw.get("modes") or ["operate", "read", "persuade"]
    return {
        "id": raw.get("id") or raw.get("name"),
        "name": raw.get("name", ""),
        "kind": kind,
        "stack": stacks,
        "platforms": raw.get("platforms") or ["system"],
        "category": raw.get("category", ""),
        "license": license_name,
        "license_ok": bool(license_ok),
        "url": raw.get("url", ""),
        "repo": raw.get("repo", ""),
        "needs": raw.get("needs") or [],
        "modes": modes,
        "flashy": bool(raw.get("flashy", False)),
        "install": raw.get("install", ""),
        "usage": raw.get("usage") or ("reference" if kind in {"gallery", "license-trap"} else "dependency"),
        "use_case": raw.get("use_case", ""),
        "a11y_notes": raw.get("a11y_notes", ""),
        "catalog": catalog,
    }


def stack_ok(item: dict, stack: str) -> bool:
    if stack == "all":
        return True
    wanted = STACK_ALIASES.get(stack, {stack, "all"})
    have = {s.lower() for s in item.get("stack", [])}
    return bool(wanted & have) or "all" in have


def mode_ok(item: dict, mode: str) -> bool:
    if mode == "all":
        return True
    modes = item.get("modes") or []
    if mode not in modes and "all" not in modes:
        return False
    if mode in {"operate", "read"} and item.get("flashy"):
        return False
    return True


def blob(item: dict) -> str:
    return " ".join([
        item["name"],
        item["category"],
        item["use_case"],
        " ".join(item.get("needs") or []),
        " ".join(item.get("stack") or []),
        item.get("usage", ""),
    ])


STOPWORDS = {
    "de", "da", "do", "das", "dos", "a", "o", "e", "em", "para", "com", "um", "uma",
    "que", "no", "na", "os", "as", "por", "the", "of", "and", "for", "to", "with",
}


def query_tokens(text: str) -> list[str]:
    tokens = [tok for tok in normalize_text(text) if tok not in STOPWORDS and len(tok) > 2]
    return tokens or normalize_text(text)


def rank_matching(items: list[dict], query: str, platform: str, extra_filter, top: int) -> list[dict]:
    filtered = [
        item for item in items
        if match_platform(item.get("platforms", []), platform) and extra_filter(item)
    ]
    if not filtered:
        return []
    docs = [normalize_text(blob(item)) for item in filtered]
    engine = BM25(docs)
    tokens = query_tokens(query)
    scored = []
    for index, item in enumerate(filtered):
        score = engine.score(tokens, index)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:top]]


def search_local(need: str, stack: str, platform: str, mode: str, top: int) -> dict:
    items = load_catalog()

    def adopt_filter(item: dict) -> bool:
        if item["kind"] in {"gallery", "license-trap"} or not item["license_ok"]:
            return False
        return stack_ok(item, stack) and mode_ok(item, mode)

    def gallery_filter(item: dict) -> bool:
        return item["kind"] == "gallery" and stack_ok(item, stack)

    def trap_filter(item: dict) -> bool:
        return item["kind"] == "license-trap"

    return {
        "adopt": rank_matching(items, need, platform, adopt_filter, top),
        "reference": rank_matching(items, need, platform, gallery_filter, 4),
        "traps": rank_matching(items, need, "all", trap_filter, 3),
    }


def _get_json(url: str, timeout: float = 12) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "design-aura", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def search_github(need: str, stack: str) -> list[dict]:
    found = []
    seen = set()
    query_base = f"{need} {stack if stack != 'all' else ''}".strip()
    for license_name in ("mit", "apache-2.0", "bsd-3-clause", "isc"):
        q = urllib.parse.quote(f"{query_base} license:{license_name}")
        url = f"https://api.github.com/search/repositories?q={q}&sort=stars&per_page=4"
        try:
            payload = _get_json(url)
        except Exception as exc:
            return [{"error": f"GitHub indisponivel: {exc}"}]
        for repo in payload.get("items") or []:
            spdx = ((repo.get("license") or {}).get("spdx_id") or "").strip()
            if spdx not in PERMISSIVE or repo["full_name"] in seen:
                continue
            seen.add(repo["full_name"])
            found.append({
                "name": repo["full_name"],
                "license": spdx,
                "license_ok": True,
                "url": repo.get("html_url"),
                "repo": repo.get("html_url"),
                "stars": repo.get("stargazers_count"),
                "pushed_at": repo.get("pushed_at"),
                "use_case": (repo.get("description") or "")[:220],
                "usage": "dependency",
                "install": f"ver README em {repo.get('html_url')}",
                "source": "github",
            })
    return found[:8]


def _npm_license(meta: dict) -> str:
    lic = meta.get("license")
    if isinstance(lic, dict):
        return str(lic.get("type") or "")
    if isinstance(lic, list):
        return " OR ".join(str(x) for x in lic)
    return str(lic or "")


def search_npm(need: str, stack: str) -> list[dict]:
    text = urllib.parse.quote(f"{need} {stack if stack != 'all' else ''}".strip())
    try:
        payload = _get_json(f"https://registry.npmjs.org/-/v1/search?text={text}&size=6")
    except Exception as exc:
        return [{"error": f"npm indisponivel: {exc}"}]
    found = []
    for row in payload.get("objects") or []:
        pkg = row.get("package") or {}
        name = pkg.get("name")
        if not name:
            continue
        try:
            meta = _get_json(f"https://registry.npmjs.org/{urllib.parse.quote(name)}")
        except Exception:
            continue
        latest = (meta.get("dist-tags") or {}).get("latest")
        version_meta = (meta.get("versions") or {}).get(latest) or {}
        license_name = _npm_license(version_meta) or _npm_license(meta)
        if license_name not in PERMISSIVE:
            continue
        found.append({
            "name": name,
            "license": license_name,
            "license_ok": True,
            "url": (pkg.get("links") or {}).get("repository") or (pkg.get("links") or {}).get("npm"),
            "repo": (pkg.get("links") or {}).get("repository") or "",
            "use_case": (pkg.get("description") or "")[:220],
            "usage": "dependency",
            "install": f"npm install {name}",
            "source": "npm",
            "version": latest,
        })
    return found[:5]


def format_markdown(need: str, mode: str, stack: str, platform: str, local: dict, online: dict | None) -> str:
    lines = [
        f"# Descoberta de componentes — `{need}`",
        f"- **Modo de superficie:** `{mode}` · **stack:** `{stack}` · **plataforma:** `{platform}`",
        "- Parta da interacao. Re-tematize tudo pela `DESIGN-BIBLE.md`. Codigo publico sem licenca permissiva nao entra.",
        "",
        "## Portao antes de adotar",
        "Para cada candidato: adequacao, stack, acessibilidade real, adaptacao aos tokens, estados, manutencao, peso e licenca MIT / Apache-2.0 / BSD / ISC.",
        "Declare o uso: **Referencia**, **Dependencia** ou **Codigo copiado via registry**.",
        "",
        "## Adotar (licenca permissiva, compativel com o modo)",
    ]
    if not local["adopt"]:
        lines.append("- Nenhum candidato local passou nos filtros. Alargue `--stack all` ou descreva a interacao com outras palavras.")
    for item in local["adopt"]:
        install = f" · `{item['install']}`" if item.get("install") else ""
        lines.append(
            f"- **{item['name']}** ({item['usage']} · {item['license']} · {item['url']}){install}: {item['use_case']}"
        )
        if item.get("a11y_notes"):
            lines.append(f"  - A11y: {item['a11y_notes']}")
    lines.extend(["", "## So referencia visual (nao copie codigo)"])
    if not local["reference"]:
        lines.append("- Nenhuma galeria local casou com esta busca.")
    for item in local["reference"]:
        lines.append(f"- **{item['name']}** ({item['url']}): {item['use_case']}")
    if local["traps"]:
        lines.extend(["", "## Nao tratar como open source"])
        for item in local["traps"]:
            lines.append(f"- **{item['name']}** [{item['license']}]: {item['use_case']}")
    if online is not None:
        lines.extend(["", "## Pesquisa ao vivo"])
        gh = online.get("github") or []
        npm = online.get("npm") or []
        if gh and gh[0].get("error"):
            lines.append(f"- {gh[0]['error']}")
        else:
            for item in gh:
                lines.append(
                    f"- GitHub **{item['name']}** ({item['license']} · {item.get('stars')} stars · push {item.get('pushed_at')}): {item['url']}"
                )
                lines.append(f"  - {item['use_case']}")
        if npm and npm[0].get("error"):
            lines.append(f"- {npm[0]['error']}")
        else:
            for item in npm:
                lines.append(f"- npm `{item['install']}` ({item['license']} · {item.get('version')}): {item['use_case']}")
        lines.append("- Confirme o arquivo LICENSE no commit exato. Estrelas nao provam adequacao.")
    lines.extend([
        "",
        "## Registro na Biblia (secao 8)",
        "| Papel | Fonte | Licenca | Uso | O que aproveitar |",
        "|---|---|---|---|---|",
    ])
    for item in local["adopt"][:5]:
        lines.append(f"| {item['category'] or 'componente'} | {item['name']} | {item['license']} | {item['usage']} | {item['use_case']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Descobre componentes free/OSS para uma necessidade real de UI.")
    parser.add_argument("--need", required=True, help="Interacao necessaria, ex.: 'tabela com edicao inline'")
    parser.add_argument("--stack", default="all", help="react, vue, svelte, solid, rn, flutter, ios, android, electron, tauri, all")
    parser.add_argument("--platform", default="all", choices=["all", "desktop", "mobile", "system", "ios", "android"])
    parser.add_argument("--mode", default="operate", choices=["operate", "read", "persuade", "all"])
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--online", action="store_true", help="Consulta GitHub e npm e filtra licenca permissiva")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = parser.parse_args()

    try:
        local = search_local(args.need, args.stack, args.platform, args.mode, max(1, args.top))
    except Exception as exc:
        print(f"Erro no catalogo local: {exc}", file=sys.stderr)
        sys.exit(1)

    online = None
    if args.online:
        online = {"github": search_github(args.need, args.stack), "npm": search_npm(args.need, args.stack)}

    if args.format == "json":
        print(json.dumps({"local": local, "online": online}, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(args.need, args.mode, args.stack, args.platform, local, online))


if __name__ == "__main__":
    main()
