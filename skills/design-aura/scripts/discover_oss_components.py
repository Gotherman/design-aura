#!/usr/bin/env python3
"""Casa necessidades de interacao ou um repositorio/plano inteiro com componentes free/OSS,
receitas de micro-componentes de estudio e curadoria de iconografia nas 16 Categorias Canonicas.

Modos de uso:
1. Busca categorica automatica lendo o projeto/plano:
   python3 discover_oss_components.py --scan /caminho/do/projeto --stack html --platform system --mode operate
2. Busca por categoria canonica especifica (ou listar as 16 categorias):
   python3 discover_oss_components.py --category charts-telemetry-financial --stack html
   python3 discover_oss_components.py --list-categories
3. Busca pontual por interacao (BM25 local + opcional --online GitHub/npm):
   python3 discover_oss_components.py --need "grafico de fluxo de caixa com crosshair" --stack html
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
from collections import Counter
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
    "html": {"html", "css", "all"},
    "tailwind": {"tailwind", "html", "css", "all"},
    "all": {"all"},
}


def load_recipes_taxonomy() -> list[dict]:
    path = DATA_DIR / "ui_elements_recipes.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog() -> list[dict]:
    items = []
    seen_names: set[str] = set()
    # Carrega registries_oss primeiro (mais rico, com comando install e needs) e deduplica por nome normalizado
    for name in ("registries_oss.json", "components_oss.json", "study_references.json"):
        path = DATA_DIR / name
        if not path.exists():
            continue
        for raw in json.loads(path.read_text(encoding="utf-8")):
            item = normalize_item(raw, name)
            key = " ".join(normalize_text(item["name"]))
            if key and key in seen_names:
                continue
            if key:
                seen_names.add(key)
            items.append(item)
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
        "taxonomy_category": raw.get("taxonomy_category") or raw.get("category", ""),
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
        item["category"] if item.get("catalog") != "study_references.json" else "",
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


def match_recipes_for_query(query: str, platform: str, top: int = 3) -> list[dict]:
    cats = load_recipes_taxonomy()
    if not cats:
        return []
    flat_recipes = []
    for cat in cats:
        if not match_platform(cat.get("platforms", []), platform):
            continue
        for rec in cat.get("studio_recipes", []):
            flat_recipes.append({
                "category_id": cat["id"],
                "category_name": cat["name"],
                "id": rec["id"],
                "name": rec["name"],
                "anatomy": rec["anatomy"],
                "anti_slop": rec["anti_slop"],
                "icon_rule": (cat.get("icon_curation") or {}).get("rule", ""),
                "keywords": " ".join(cat.get("detect_keywords", [])),
            })
    if not flat_recipes:
        return []
    docs = [
        normalize_text(f"{r['name']} {r['anatomy']} {r['anti_slop']} {r['keywords']} {r['category_name']}")
        for r in flat_recipes
    ]
    engine = BM25(docs)
    tokens = query_tokens(query)
    scored = []
    for idx, rec in enumerate(flat_recipes):
        sc = engine.score(tokens, idx)
        if sc > 0:
            scored.append((sc, rec))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [r for _, r in scored[:top]]


def search_local(need: str, stack: str, platform: str, mode: str, top: int) -> dict:
    items = load_catalog()

    def adopt_filter(item: dict) -> bool:
        if item["kind"] in {"gallery", "anatomy", "official", "study", "license-trap"}:
            return False
        if item["kind"] != "platform" and not item["license_ok"]:
            return False
        return stack_ok(item, stack) and mode_ok(item, mode)

    def gallery_filter(item: dict) -> bool:
        return item["kind"] in {"gallery", "anatomy", "official", "study"} and stack_ok(item, stack)

    def trap_filter(item: dict) -> bool:
        return item["kind"] == "license-trap"

    return {
        "adopt": rank_matching(items, need, platform, adopt_filter, top),
        "reference": rank_matching(items, need, platform, gallery_filter, 4),
        "traps": rank_matching(items, need, "all", trap_filter, 3),
        "recipes": match_recipes_for_query(need, platform, 3),
    }


IGNORE_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next", "__pycache__", "audit", "telas-anteriores"}
SCAN_EXTS = {".md", ".txt", ".json", ".js", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".html"}


def collect_project_text(scan_path: Path, max_files: int = 45, max_bytes_per_file: int = 18000) -> tuple[str, list[str]]:
    if not scan_path.exists():
        raise FileNotFoundError(f"Caminho para --scan nao encontrado: {scan_path}")
    if scan_path.is_file():
        return scan_path.read_text(encoding="utf-8", errors="ignore")[:60000], [scan_path.name]

    priority_files: list[Path] = []
    other_files: list[Path] = []
    for p in sorted(scan_path.rglob("*")):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIRS or part.startswith(".") for part in p.relative_to(scan_path).parts):
            continue
        if p.suffix.lower() not in SCAN_EXTS:
            continue
        name_low = p.name.lower()
        if any(k in name_low for k in ("readme", "leiame", "concepcao", "plan", "prd", "spec", "estado", "exemplo", "dados", "package.json", "rotas", "index")):
            priority_files.append(p)
        else:
            other_files.append(p)

    chosen = (priority_files + other_files)[:max_files]
    chunks = []
    rel_names = []
    for f in chosen:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")[:max_bytes_per_file]
            chunks.append(f"{f.name} {txt}")
            rel_names.append(str(f.relative_to(scan_path)))
        except Exception:
            continue
    return "\n".join(chunks), rel_names


def scan_project_categories(
    scan_path: str | Path | None = None,
    blueprint_text: str = "",
    category_filter: str = "",
    stack: str = "all",
    platform: str = "all",
    mode: str = "operate",
    top_per_cat: int = 4,
) -> dict:
    cats = load_recipes_taxonomy()
    catalog = load_catalog()
    item_by_id = {it["id"]: it for it in catalog}

    scanned_files: list[str] = []
    raw_text = blueprint_text or ""
    if scan_path:
        proj_txt, scanned_files = collect_project_text(Path(scan_path))
        raw_text = f"{raw_text}\n{proj_txt}".strip()

    token_counts = Counter(normalize_text(raw_text))

    def can_adopt(it: dict) -> bool:
        if it["kind"] in {"gallery", "anatomy", "official", "study", "license-trap"}:
            return False
        if it["kind"] != "platform" and not it["license_ok"]:
            return False
        return match_platform(it.get("platforms", []), platform) and stack_ok(it, stack) and mode_ok(it, mode)

    matched_categories = []
    for cat in cats:
        if category_filter and cat["id"] != category_filter:
            continue
        if not match_platform(cat.get("platforms", []), platform):
            continue

        matched_kw = []
        score = 0
        for kw in cat.get("detect_keywords", []):
            kw_toks = normalize_text(kw)
            if not kw_toks:
                continue
            hits = min(token_counts.get(t, 0) for t in kw_toks)
            if hits > 0:
                matched_kw.append(kw)
                score += min(hits, 8)

        include = bool(category_filter) or cat.get("always_include", False) or score > 0 or not raw_text
        if not include:
            continue

        # Select top OSS libraries for this category
        chosen_oss = []
        seen_oss = set()
        for rid in cat.get("recommended_oss_ids", []):
            it = item_by_id.get(rid)
            if it and can_adopt(it) and it["id"] not in seen_oss:
                chosen_oss.append(it)
                seen_oss.add(it["id"])
        for it in catalog:
            if len(chosen_oss) >= top_per_cat:
                break
            if it.get("taxonomy_category") == cat["id"] and can_adopt(it) and it["id"] not in seen_oss:
                chosen_oss.append(it)
                seen_oss.add(it["id"])

        matched_categories.append({
            "id": cat["id"],
            "name": cat["name"],
            "always_include": bool(cat.get("always_include", False)),
            "score": score + (10 if cat.get("always_include") else 0),
            "matched_keywords": matched_kw[:8],
            "adopt_oss": chosen_oss[:top_per_cat],
            "studio_recipes": cat.get("studio_recipes", []),
            "icon_curation": cat.get("icon_curation", {}),
        })

    matched_categories.sort(key=lambda c: (not c["always_include"], -c["score"]))
    return {
        "scan_path": str(scan_path) if scan_path else None,
        "scanned_files_count": len(scanned_files),
        "scanned_files_sample": scanned_files[:12],
        "filters": {"stack": stack, "platform": platform, "mode": mode, "category": category_filter or "auto"},
        "categories": matched_categories,
    }


def format_scan_markdown(report: dict) -> str:
    flt = report["filters"]
    lines = [
        "# Design Aura — Mapeamento Categórico Inteligente de UI/UX & Componentes OSS",
        f"- **Stack:** `{flt['stack']}` · **Plataforma:** `{flt['platform']}` · **Modo:** `{flt['mode']}` · **Categorias ativadas:** `{len(report['categories'])}/16`",
    ]
    if report.get("scan_path"):
        sample = ", ".join(f"`{x}`" for x in report["scanned_files_sample"][:8])
        lines.append(f"- **Repositório/Plano analisado:** `{report['scan_path']}` ({report['scanned_files_count']} arquivos lidos: {sample})")
    lines.extend([
        "- **Como usar:** incorpore as bibliotecas permissivas e as **Receitas de Micro-Componentes e Iconografia** abaixo na Seção 8 da `DESIGN-BIBLE.md`, no `shell.css` e nas Telas-Mãe.",
        "",
    ])

    bible_rows = []
    seen_bible_oss = set()

    for cat in report["categories"]:
        trigger = "Pilar Obrigatório Universal" if cat["always_include"] and not cat["matched_keywords"] else (
            f"Detectado no projeto por: `{', '.join(cat['matched_keywords'])}`" if cat["matched_keywords"] else "Categoria selecionada"
        )
        lines.extend([
            f"## {cat['name']} (`{cat['id']}`)",
            f"- **Gatilho:** {trigger}",
        ])

        if cat["adopt_oss"]:
            lines.append("- **Bibliotecas & Registries Open Source (`MIT / Apache-2.0 / ISC`):**")
            cat_added = 0
            for it in cat["adopt_oss"]:
                inst = f" · `{it['install']}`" if it.get("install") else ""
                lines.append(f"  - **{it['name']}** ({it['usage']} · {it['license']} · {it['url']}){inst}: {it['use_case']}")
                if it["id"] not in seen_bible_oss and cat_added < 2:
                    seen_bible_oss.add(it["id"])
                    bible_rows.append((cat["id"], it["name"], it["license"], it["usage"], it["use_case"]))
                    cat_added += 1

        if cat["studio_recipes"]:
            lines.append("- **Receitas Visuais & Micro-Componentes de Estúdio Obrigatórios:**")
            for rec in cat["studio_recipes"]:
                lines.append(f"  - **{rec['name']}** (`{rec['id']}`): {rec['anatomy']}")
                lines.append(f"    - *Anti-Slop:* {rec['anti_slop']}")

        ic = cat.get("icon_curation") or {}
        if ic.get("rule"):
            lines.append(f"- **Curadoria de Ícones da Categoria:** {ic['rule']}")
            if ic.get("avoid"):
                lines.append(f"  - *Proibido:* {ic['avoid']}")
        lines.append("")

    lines.extend([
        "## Tabela Pronta para a Seção 8 da `DESIGN-BIBLE.md`",
        "| Categoria Canônica | Fonte OSS | Licença | Uso | O que aproveitar no projeto |",
        "|---|---|---|---|---|",
    ])
    for cat_id, name, lic, usage, use_case in bible_rows[:24]:
        lines.append(f"| `{cat_id}` | **{name}** | {lic} | {usage} | {use_case} |")

    return "\n".join(lines)


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
        cat_tag = f" [`{item.get('taxonomy_category')}`]" if item.get("taxonomy_category") else ""
        lines.append(
            f"- **{item['name']}**{cat_tag} ({item['usage']} · {item['license']} · {item['url']}){install}: {item['use_case']}"
        )
        if item.get("a11y_notes"):
            lines.append(f"  - A11y: {item['a11y_notes']}")

    if local.get("recipes"):
        lines.extend(["", "## Receitas Visuais & Micro-Componentes de Estúdio Recomendados"])
        for rec in local["recipes"]:
            lines.append(f"- **{rec['name']}** (`{rec['category_id']}`): {rec['anatomy']}")
            lines.append(f"  - *Anti-Slop:* {rec['anti_slop']}")
            if rec.get("icon_rule"):
                lines.append(f"  - *Iconografia:* {rec['icon_rule']}")

    lines.extend(["", "## So referencia (guias oficiais, anatomia e galerias; nao copie codigo)"])
    if not local["reference"]:
        lines.append("- Nenhuma galeria local casou com esta busca.")
    for item in local["reference"]:
        lines.append(f"- **{item['name']}** ({item['kind']} · {item['url']}): {item['use_case']}")
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
    parser = argparse.ArgumentParser(description="Descobre componentes free/OSS e receitas visuais categorizadas para UI/UX.")
    parser.add_argument("--need", help="Interacao necessaria, ex.: 'tabela com edicao inline'")
    parser.add_argument("--scan", help="Caminho do repositorio, pasta ou arquivo de planejamento para mapeamento categorico automatico")
    parser.add_argument("--blueprint", default="", help="Texto descritivo do projeto/modulos para categorizacao automatica")
    parser.add_argument("--category", default="", help="Filtrar por uma das 16 categorias canonicas (veja --list-categories)")
    parser.add_argument("--list-categories", action="store_true", help="Lista as 16 categorias canonicas de UI/UX da skill")
    parser.add_argument("--stack", default="all", help="html, react, vue, svelte, solid, rn, flutter, ios, android, electron, tauri, all")
    parser.add_argument("--platform", default="all", choices=["all", "desktop", "mobile", "system", "ios", "android"])
    parser.add_argument("--mode", default="operate", choices=["operate", "read", "persuade", "all"])
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--online", action="store_true", help="Consulta GitHub e npm e filtra licenca permissiva")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = parser.parse_args()

    if args.list_categories:
        cats = load_recipes_taxonomy()
        if args.format == "json":
            print(json.dumps([{"id": c["id"], "name": c["name"], "always_include": c["always_include"]} for c in cats], ensure_ascii=False, indent=2))
        else:
            print("# 16 Categorias Canônicas de UI/UX — Design Aura v2.2.0\n")
            for c in cats:
                tag = " *(sempre ativa)*" if c.get("always_include") else ""
                print(f"- **`{c['id']}`** — {c['name']}{tag}")
        return

    if args.scan or args.blueprint or args.category:
        try:
            report = scan_project_categories(
                scan_path=args.scan,
                blueprint_text=args.blueprint,
                category_filter=args.category,
                stack=args.stack,
                platform=args.platform,
                mode=args.mode,
                top_per_cat=max(2, min(6, args.top)),
            )
        except Exception as exc:
            print(f"Erro ao escanear categorias do projeto: {exc}", file=sys.stderr)
            sys.exit(1)
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_scan_markdown(report))
        return

    if not args.need:
        parser.error("Informe --need '<interacao>' OU --scan '<caminho-do-projeto>' OU --category '<id>' OU --list-categories.")

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
