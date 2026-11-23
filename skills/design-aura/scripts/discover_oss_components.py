#!/usr/bin/env python3
"""Busca na base pre-categorizada de componentes da Design Aura.

A base (data/catalog/*.json) organiza cada peca por categoria, necessidade, stack,
plataforma, modo de superficie, estilo (forma, densidade, motion, como re-tematizar)
e situacao de licenca. Um projeto pode usar varias bibliotecas: a regra e uma peca
por necessidade, todas re-tematizadas pelos tokens do projeto.

Modos de uso:
1. Ler o projeto e mapear necessidades automaticamente:
   python3 discover_oss_components.py --scan <repo-ou-plano> --stack react --platform system --mode operate
2. Buscar uma necessidade pontual:
   python3 discover_oss_components.py --need "agenda de consultas por profissional" --stack html
3. Navegar a base:
   python3 discover_oss_components.py --list-categories
   python3 discover_oss_components.py --category charts --stack react
4. Ajustar o ranking a direcao escolhida:
   ... --shape soft --density compact --motion subtle   (ou --direction direcao.json)
5. Pesquisa ao vivo (GitHub/npm, so licenca permissiva): --online
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
CATALOG_DIR = DATA_DIR / "catalog"
PERMISSIVE = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "Unlicense", "CC0-1.0", "MPL-2.0"}
USABLE_STATUS = {"ok", "attribution", "platform", "free-license"}
REFERENCE_KINDS = {"gallery", "anatomy", "official", "study"}
PERSUADE_CATEGORIES = {"marketing", "effects"}
STACK_ALIASES = {
    "react": {"react", "all"},
    "next": {"react", "all"},
    "vue": {"vue", "all"},
    "nuxt": {"vue", "all"},
    "svelte": {"svelte", "all"},
    "solid": {"solid", "all"},
    "angular": {"angular", "all"},
    "rn": {"rn", "all"},
    "expo": {"rn", "all"},
    "flutter": {"flutter", "all"},
    "ios": {"ios", "all"},
    "swiftui": {"ios", "all"},
    "android": {"android", "all"},
    "compose": {"android", "all"},
    "electron": {"electron", "react", "html", "all"},
    "tauri": {"tauri", "react", "html", "all"},
    "html": {"html", "all"},
    "tailwind": {"html", "react", "all"},
    "all": {"all"},
}
STOPWORDS = {
    "de", "da", "do", "das", "dos", "a", "o", "e", "em", "para", "com", "um", "uma", "que", "no", "na",
    "os", "as", "por", "the", "of", "and", "for", "to", "with", "ou", "se", "ao", "sem",
}


# ---------------------------------------------------------------- carga

def load_taxonomy() -> dict:
    return json.loads((DATA_DIR / "taxonomy.json").read_text(encoding="utf-8"))


def need_index(taxonomy: dict | None = None) -> dict:
    taxonomy = taxonomy or load_taxonomy()
    idx = {}
    for cat in taxonomy["categories"]:
        for need in cat["needs"]:
            idx[need["id"]] = {**need, "category": cat["id"], "category_name": cat["name"]}
    return idx


def load_catalog() -> list[dict]:
    items = []
    for path in sorted(CATALOG_DIR.glob("*.json")):
        for raw in json.loads(path.read_text(encoding="utf-8")):
            items.append(normalize_item(raw, path.name))
    return items


def normalize_item(raw: dict, source: str) -> dict:
    status = raw.get("license_status") or ("ok" if raw.get("license") in PERMISSIVE else "verify")
    item = dict(raw)
    item.update({
        "stack": raw.get("stacks") or ["all"],
        "usage": {"copy": "registry", "dependency": "dependency", "platform": "platform", "reference": "reference", "tool": "tool"}.get(raw.get("use"), "dependency"),
        "license_ok": status in USABLE_STATUS,
        "use_case": raw.get("summary", ""),
        "a11y_notes": raw.get("a11y", ""),
        "catalog": source,
    })
    return item


# ---------------------------------------------------------------- filtros

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


def is_reference(item: dict) -> bool:
    return item["kind"] in REFERENCE_KINDS or (item.get("use") == "reference" and item["kind"] != "license-trap")


def can_adopt(item: dict, stack: str, platform: str, mode: str) -> bool:
    if item["kind"] == "license-trap" or is_reference(item):
        return False
    if item.get("use") == "tool" and item["kind"] not in {"font-source"}:
        return False
    if not item["license_ok"]:
        return False
    return match_platform(item.get("platforms", []), platform) and stack_ok(item, stack) and mode_ok(item, mode)


def needs_verification(item: dict, stack: str, platform: str, mode: str) -> bool:
    return (item.get("license_status") == "verify" and item["kind"] != "license-trap" and not is_reference(item)
            and match_platform(item.get("platforms", []), platform) and stack_ok(item, stack) and mode_ok(item, mode))


# ---------------------------------------------------------------- deteccao de necessidades

class TextIndex:
    def __init__(self, text: str):
        tokens = [t for t in normalize_text(text) if t not in STOPWORDS]
        self.counts = Counter(tokens)
        self.joined = " " + " ".join(normalize_text(text)) + " "
        self.size = len(tokens)

    def hits(self, keyword: str) -> int:
        exact = keyword.endswith("=")
        kw_tokens = normalize_text(keyword.rstrip("="))
        if not kw_tokens:
            return 0
        if len(kw_tokens) > 1:
            return self.joined.count(" " + " ".join(kw_tokens) + " ")
        tok = kw_tokens[0]
        if exact or len(tok) < 4:
            return self.counts.get(tok, 0)
        return sum(c for t, c in self.counts.items() if t.startswith(tok))


def detect_needs(text: str, min_score: int | None = None, taxonomy: dict | None = None) -> list[dict]:
    """Devolve as necessidades citadas no texto, da mais forte para a mais fraca."""
    index = TextIndex(text)
    if min_score is None:
        min_score = 1 if index.size < 4000 else 2
    found = []
    for need in need_index(taxonomy).values():
        score = 0
        matched = []
        for kw in need.get("keywords", []):
            n = index.hits(kw)
            if n:
                weight = 2 if " " in kw.strip("=") else 1
                score += min(n, 6) * weight
                matched.append(kw.rstrip("="))
        if score >= min_score:
            found.append({"id": need["id"], "name": need["name"], "category": need["category"],
                          "category_name": need["category_name"], "score": score, "matched": matched[:6]})
    found.sort(key=lambda n: -n["score"])
    return found


# ---------------------------------------------------------------- ranking

def load_direction(path: str | None, shape: str = "", density: str = "", motion: str = "", skin: str = "") -> dict:
    direction = {}
    if path:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        direction = data.get("style") or data
    for key, val in (("shape", shape), ("density", density), ("motion", motion), ("skin", skin)):
        if val:
            direction[key] = val
    return direction


def style_bonus(item: dict, direction: dict) -> float:
    if not direction:
        return -1.0 if item.get("flashy") else 0.0
    style = item.get("style") or {}
    bonus = 0.0
    want_motion = direction.get("motion")
    if want_motion and style.get("motion"):
        order = {"none": 0, "subtle": 1, "expressive": 2}
        gap = abs(order.get(style["motion"], 1) - order.get(want_motion, 1))
        bonus += 0.6 if gap == 0 else (-0.8 if gap == 2 else 0)
    want_skin = direction.get("skin")
    if want_skin and style.get("skin"):
        if style["skin"] == want_skin:
            bonus += 0.6
        elif style["skin"] in {"headless", "tokens"}:
            bonus += 0.3
    if item.get("flashy") and direction.get("motion") != "expressive":
        bonus -= 1.0
    if direction.get("density") == "compact" and item.get("id") in {"glide-data-grid", "ag-grid-community", "blueprint", "tanstack-table"}:
        bonus += 0.3
    return bonus


def item_text(item: dict) -> str:
    return " ".join([item["name"], item.get("summary", ""), " ".join(item.get("keywords") or []),
                     " ".join(item.get("needs") or []).replace("-", " "), " ".join(item.get("categories") or []).replace("-", " ")])


def rank(items: list[dict], query: str, need_ids: list[str], direction: dict, top: int,
         stack: str = "all", text_weight: float = 1.0) -> list[dict]:
    if not items:
        return []
    engine = BM25([normalize_text(item_text(it)) for it in items])
    q = [t for t in normalize_text(query) if t not in STOPWORDS and len(t) > 2] or normalize_text(query)
    scored = []
    for i, it in enumerate(items):
        text_score = engine.score(q, i) if q else 0.0
        need_score = 3.0 * len(set(need_ids) & set(it.get("needs") or []))
        if text_score <= 0 and need_score <= 0:
            continue
        score = text_weight * text_score + need_score + 0.9 * it.get("craft", 2) + style_bonus(it, direction)
        if stack != "all" and STACK_ALIASES.get(stack, {stack}) & ({s.lower() for s in it.get("stack", [])} - {"all"}):
            score += 0.8
        if it.get("license_status") == "attribution":
            score -= 0.2
        scored.append((score, it))
    scored.sort(key=lambda p: -p[0])
    return [it for _, it in scored[:top]]


def load_recipes() -> list[dict]:
    path = DATA_DIR / "recipes.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def recipes_for(need_ids: list[str], query: str = "", top: int = 3) -> list[dict]:
    recipes = load_recipes()
    hits = [r for r in recipes if set(r.get("needs", [])) & set(need_ids)]
    if query and len(hits) < top:
        engine = BM25([normalize_text(f"{r['name']} {r['problem']} {' '.join(o['name'] for o in r['options'])}") for r in recipes])
        q = [t for t in normalize_text(query) if t not in STOPWORDS and len(t) > 2]
        extra = sorted(((engine.score(q, i), r) for i, r in enumerate(recipes)), key=lambda p: -p[0])
        for score, r in extra:
            if score > 0 and r not in hits:
                hits.append(r)
    return hits[:top]


def search_local(need: str, stack: str, platform: str, mode: str, top: int, direction: dict | None = None) -> dict:
    items = load_catalog()
    direction = direction or {}
    need_ids = [n["id"] for n in detect_needs(need, min_score=1)]
    adopt = rank([it for it in items if can_adopt(it, stack, platform, mode)], need, need_ids, direction, top, stack)
    refs = rank([it for it in items if is_reference(it) and stack_ok(it, stack) and match_platform(it.get("platforms", []), platform)],
                need, need_ids, {}, 4)
    traps = rank([it for it in items if it["kind"] == "license-trap"], need, need_ids, {}, 3)
    verify = rank([it for it in items if needs_verification(it, stack, platform, mode)], need, need_ids, direction, 3, stack)
    return {"needs": need_ids, "adopt": adopt, "reference": refs, "traps": traps, "verify": verify,
            "recipes": recipes_for(need_ids, need, 3)}


# ---------------------------------------------------------------- leitura do projeto

IGNORE_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next", "__pycache__", "audit", "telas-anteriores", "coverage"}
SCAN_EXTS = {".md", ".txt", ".json", ".js", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".html"}


def collect_project_text(scan_path: Path, max_files: int = 45, max_bytes_per_file: int = 18000) -> tuple[str, list[str]]:
    if not scan_path.exists():
        raise FileNotFoundError(f"Caminho para --scan nao encontrado: {scan_path}")
    if scan_path.is_file():
        return scan_path.read_text(encoding="utf-8", errors="ignore")[:60000], [scan_path.name]
    priority, other = [], []
    for p in sorted(scan_path.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in SCAN_EXTS:
            continue
        if any(part in IGNORE_DIRS or part.startswith(".") for part in p.relative_to(scan_path).parts):
            continue
        if p.name in {"package-lock.json", "pnpm-lock.yaml", "yarn.lock"}:
            continue
        low = p.name.lower()
        bucket = priority if any(k in low for k in ("readme", "leiame", "concepcao", "plan", "prd", "spec", "escopo", "requisit", "rotas", "routes")) else other
        bucket.append(p)
    chunks, names = [], []
    for f in (priority + other)[:max_files]:
        try:
            chunks.append(f.read_text(encoding="utf-8", errors="ignore")[:max_bytes_per_file])
            names.append(str(f.relative_to(scan_path)))
        except OSError:
            continue
    return "\n".join(chunks), names


def scan_project_categories(scan_path: str | Path | None = None, blueprint_text: str = "", category_filter: str = "",
                            stack: str = "all", platform: str = "all", mode: str = "operate", top_per_cat: int = 3,
                            direction: dict | None = None, max_needs: int = 16) -> dict:
    taxonomy = load_taxonomy()
    catalog = load_catalog()
    direction = direction or {}
    files: list[str] = []
    text = blueprint_text or ""
    if scan_path:
        proj, files = collect_project_text(Path(scan_path))
        text = f"{text}\n{proj}".strip()

    needs = detect_needs(text, taxonomy=taxonomy) if text else []
    if category_filter:
        cat_needs = [n for n in need_index(taxonomy).values() if n["category"] == category_filter]
        known = {n["id"] for n in needs}
        needs = [n for n in needs if n["category"] == category_filter] + [
            {"id": n["id"], "name": n["name"], "category": n["category"], "category_name": n["category_name"], "score": 0, "matched": []}
            for n in cat_needs if n["id"] not in known]
    needs = needs[:max_needs]

    cats: dict[str, dict] = {}
    for need in needs:
        # Secoes de site e efeitos expressivos pertencem ao modo Persuade, mesmo num sistema Operate.
        need_mode = "persuade" if need["category"] in PERSUADE_CATEGORIES and mode in {"operate", "read"} else mode
        pool = [it for it in catalog if need["id"] in (it.get("needs") or []) and can_adopt(it, stack, platform, need_mode)]
        picks = rank(pool, need["name"], [need["id"]], direction, top_per_cat, stack, text_weight=0.3)
        need = {**need, "mode": need_mode}
        refs = [it for it in catalog if is_reference(it) and need["id"] in (it.get("needs") or [])][:2]
        entry = cats.setdefault(need["category"], {"id": need["category"], "name": need["category_name"], "needs": [],
                                                    "adopt_oss": [], "studio_recipes": [], "score": 0})
        entry["needs"].append({**need, "picks": picks, "references": refs})
        entry["score"] += need["score"]
        for it in picks:
            if it not in entry["adopt_oss"]:
                entry["adopt_oss"].append(it)
    for entry in cats.values():
        entry["studio_recipes"] = recipes_for([n["id"] for n in entry["needs"]], top=4)
    ordered = sorted(cats.values(), key=lambda c: -c["score"])
    return {
        "scan_path": str(scan_path) if scan_path else None,
        "scanned_files_count": len(files),
        "scanned_files_sample": files[:12],
        "filters": {"stack": stack, "platform": platform, "mode": mode, "category": category_filter or "auto", "direction": direction},
        "needs": [{k: v for k, v in n.items()} for n in needs],
        "categories": ordered,
    }


# ---------------------------------------------------------------- saida

def license_tag(it: dict) -> str:
    st = it.get("license_status")
    if st == "attribution":
        return f"{it['license']} · exige atribuição"
    if st == "free-license":
        return f"{it['license']} · gratuita, não é OSS"
    if st == "verify":
        return f"{it['license']} · conferir licença"
    return it.get("license", "")


def pick_line(it: dict) -> str:
    use = {"registry": "copiar", "dependency": "dependência", "platform": "plataforma", "tool": "ferramenta"}.get(it["usage"], it["usage"])
    stacks = ",".join(it.get("stack", []))
    inst = f" · `{it['install']}`" if it.get("install") else ""
    note = f" — {it['notes']}" if it.get("notes") else ""
    return f"**{it['name']}** ({use} · {license_tag(it)} · {stacks} · {it.get('url', '')}){inst}: {it.get('use_case', '')}{note}"


COHERENCE = [
    "Várias bibliotecas no mesmo projeto são normais; a regra é **uma peça por necessidade**.",
    "Re-tematize toda peça pelos tokens da Bíblia (cor, raio, tipo, sombra). Nenhuma traz a paleta da demo.",
    "Uma família de ícones e um sistema de motion por projeto, mesmo quando as peças vêm de bibliotecas diferentes.",
    "Antes de copiar ou instalar, confirme a licença na versão fixada e registre-a na Bíblia.",
]


def format_scan_markdown(report: dict) -> str:
    f = report["filters"]
    lines = [
        "# Design Aura — Necessidades do projeto e componentes candidatos",
        f"- Stack `{f['stack']}` · plataforma `{f['platform']}` · modo `{f['mode']}` · necessidades detectadas: {len(report['needs'])}",
    ]
    if report.get("scan_path"):
        lines.append(f"- Lido: `{report['scan_path']}` ({report['scanned_files_count']} arquivos)")
    if f.get("direction"):
        lines.append(f"- Ranking ajustado à direção: `{json.dumps(f['direction'], ensure_ascii=False)}`")
    lines.append("- Isto é uma lista de candidatos. A escolha final e o motivo vão para a Bíblia.")
    lines.append("")
    rows = []
    for cat in report["categories"]:
        lines.append(f"## {cat['name']} (`{cat['id']}`)")
        for need in cat["needs"]:
            why = f" — citado como: {', '.join(need['matched'])}" if need.get("matched") else ""
            if need.get("mode") and need["mode"] != f["mode"]:
                why += f" (avaliado no modo `{need['mode']}`)"
            lines.append(f"- **{need['name']}** (`{need['id']}`){why}")
            for i, it in enumerate(need["picks"]):
                lines.append(f"  {i + 1}. {pick_line(it)}")
                if i == 0:
                    rows.append((need["name"], it))
            if not need["picks"]:
                lines.append("  - Nenhuma peça para esta stack/plataforma/modo. Rode com `--online` ou amplie `--stack`.")
            for ref in need.get("references", []):
                lines.append(f"  - Referência para estudar: {ref['name']} ({ref.get('url', '')})")
        for rec in cat.get("studio_recipes", []):
            opts = " · ".join(o["name"] for o in rec["options"])
            lines.append(f"- Padrão `{rec['id']}` — {rec['problem']} Opções: {opts}.")
        lines.append("")
    lines.append("## Coerência")
    lines.extend(f"- {c}" for c in COHERENCE)
    lines.extend(["", "## Rascunho para a Bíblia (Parte B · Componentes)",
                  "| Necessidade | Peça | Uso | Licença | Versão fixada | Caminho | Adaptação aos tokens |",
                  "|---|---|---|---|---|---|---|"])
    for need_name, it in rows[:30]:
        lines.append(f"| {need_name} | {it['name']} | {it['usage']} | {license_tag(it)} | _a fixar_ | {it.get('install') or it.get('url', '')} | _descrever_ |")
    return "\n".join(lines)


def format_markdown(need: str, mode: str, stack: str, platform: str, local: dict, online: dict | None) -> str:
    lines = [f"# Componentes para: `{need}`",
             f"- Modo `{mode}` · stack `{stack}` · plataforma `{platform}` · necessidades: {', '.join(local['needs']) or 'busca livre'}", ""]
    lines.append("## Candidatos")
    lines.extend(f"{i + 1}. {pick_line(it)}" for i, it in enumerate(local["adopt"])) if local["adopt"] else lines.append("- Nenhum candidato local para estes filtros.")
    if local["verify"]:
        lines.append("\n## Promissores, licença a conferir")
        lines.extend(f"- {pick_line(it)}" for it in local["verify"])
    if local["recipes"]:
        lines.append("\n## Padrões visuais relacionados")
        for rec in local["recipes"]:
            lines.append(f"- **{rec['name']}** (`{rec['id']}`): {rec['problem']}")
            lines.extend(f"  - {o['name']} — {o['when']} Evitar: {o['avoid']}" for o in rec["options"])
    if local["reference"]:
        lines.append("\n## Referências (estudar, sem copiar código)")
        lines.extend(f"- {it['name']} ({it.get('url', '')}): {it.get('use_case', '')}" for it in local["reference"])
    if local["traps"]:
        lines.append("\n## Armadilhas de licença")
        lines.extend(f"- {it['name']} — {it['license']}. {it.get('notes', '')}" for it in local["traps"])
    if online:
        lines.append("\n## Ao vivo (GitHub / npm, licença permissiva)")
        for src in ("github", "npm"):
            for it in online.get(src, []):
                if "error" in it:
                    lines.append(f"- {src}: {it['error']}")
                else:
                    lines.append(f"- [{src}] **{it['name']}** ({it['license']}) {it.get('url', '')}: {it.get('use_case', '')}")
    lines.append("\n## Coerência")
    lines.extend(f"- {c}" for c in COHERENCE)
    return "\n".join(lines)


def format_category(cat_id: str, stack: str, platform: str, mode: str) -> str:
    idx = need_index()
    items = [it for it in load_catalog() if cat_id in (it.get("categories") or [])]
    lines = [f"# Categoria `{cat_id}`", ""]
    for need in [n for n in idx.values() if n["category"] == cat_id]:
        lines.append(f"## {need['name']} (`{need['id']}`)")
        pool = [it for it in items if need["id"] in it.get("needs", [])]
        for it in sorted(pool, key=lambda x: -x.get("craft", 2)):
            flag = "" if can_adopt(it, stack, platform, mode) else " _(fora dos filtros ou só referência)_"
            lines.append(f"- {pick_line(it)}{flag}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- online

def _get_json(url: str, timeout: float = 12) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "design-aura-catalog", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def search_github(need: str, stack: str) -> list[dict]:
    found, seen = [], set()
    base = f"{need} {stack if stack != 'all' else ''}".strip()
    for lic in ("mit", "apache-2.0", "bsd-3-clause", "isc"):
        q = urllib.parse.quote(f"{base} license:{lic}")
        try:
            payload = _get_json(f"https://api.github.com/search/repositories?q={q}&sort=stars&per_page=4")
        except Exception as exc:  # noqa: BLE001
            return [{"error": f"GitHub indisponivel: {exc}"}]
        for repo in payload.get("items") or []:
            spdx = ((repo.get("license") or {}).get("spdx_id") or "").strip()
            if spdx not in PERMISSIVE or repo["full_name"] in seen or repo.get("archived"):
                continue
            seen.add(repo["full_name"])
            found.append({"name": repo["full_name"], "license": spdx, "url": repo.get("html_url"), "stars": repo.get("stargazers_count"),
                          "pushed_at": repo.get("pushed_at"), "use_case": (repo.get("description") or "")[:220]})
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
    except Exception as exc:  # noqa: BLE001
        return [{"error": f"npm indisponivel: {exc}"}]
    found = []
    for row in payload.get("objects") or []:
        pkg = row.get("package") or {}
        name = pkg.get("name")
        if not name:
            continue
        try:
            meta = _get_json(f"https://registry.npmjs.org/{urllib.parse.quote(name)}")
        except Exception:  # noqa: BLE001
            continue
        latest = (meta.get("dist-tags") or {}).get("latest")
        lic = _npm_license((meta.get("versions") or {}).get(latest) or {}) or _npm_license(meta)
        if lic not in PERMISSIVE:
            continue
        found.append({"name": name, "license": lic, "url": (pkg.get("links") or {}).get("repository") or (pkg.get("links") or {}).get("npm"),
                      "use_case": (pkg.get("description") or "")[:220], "version": latest})
    return found[:5]


# ---------------------------------------------------------------- CLI

def main():
    parser = argparse.ArgumentParser(description="Busca componentes na base pre-categorizada da Design Aura.")
    parser.add_argument("--need", help="Interacao necessaria, ex.: 'tabela com edicao inline'")
    parser.add_argument("--scan", help="Repositorio, pasta ou arquivo de planejamento para detectar necessidades")
    parser.add_argument("--blueprint", default="", help="Texto descritivo do projeto")
    parser.add_argument("--category", default="", help="Uma categoria da taxonomia (veja --list-categories)")
    parser.add_argument("--list-categories", action="store_true")
    parser.add_argument("--stack", default="all", help="html, react, next, vue, nuxt, svelte, solid, angular, rn, expo, flutter, ios, android, electron, tauri, all")
    parser.add_argument("--platform", default="all", choices=["all", "desktop", "mobile", "system", "ios", "android"])
    parser.add_argument("--mode", default="operate", choices=["operate", "read", "persuade", "all"])
    parser.add_argument("--top", type=int, default=3, help="Candidatos por necessidade")
    parser.add_argument("--direction", help="JSON da direcao escolhida (campo style: shape, density, motion, skin)")
    parser.add_argument("--shape", default="", choices=["", "sharp", "soft", "round"])
    parser.add_argument("--density", default="", choices=["", "compact", "regular", "airy"])
    parser.add_argument("--motion", default="", choices=["", "none", "subtle", "expressive"])
    parser.add_argument("--skin", default="", choices=["", "headless", "tokens", "tailwind", "themeable"])
    parser.add_argument("--online", action="store_true", help="Consulta GitHub e npm (so licenca permissiva)")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = parser.parse_args()
    direction = load_direction(args.direction, args.shape, args.density, args.motion, args.skin)

    if args.list_categories:
        tax = load_taxonomy()
        catalog = load_catalog()
        for cat in tax["categories"]:
            count = sum(1 for it in catalog if cat["id"] in it.get("categories", []))
            print(f"- {cat['id']}: {cat['name']} ({count} entradas) — necessidades: {', '.join(n['id'] for n in cat['needs'])}")
        return

    if args.scan or args.blueprint or (args.category and not args.need):
        if args.category and not (args.scan or args.blueprint):
            print(format_category(args.category, args.stack, args.platform, args.mode))
            return
        report = scan_project_categories(args.scan, args.blueprint, args.category, args.stack, args.platform, args.mode,
                                         max(1, args.top), direction)
        print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else format_scan_markdown(report))
        return

    if not args.need:
        parser.error("use --need, --scan, --blueprint, --category ou --list-categories")
    local = search_local(args.need, args.stack, args.platform, args.mode, max(1, args.top) + 3, direction)
    online = {"github": search_github(args.need, args.stack), "npm": search_npm(args.need, args.stack)} if args.online else None
    if args.format == "json":
        print(json.dumps({"local": local, "online": online}, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(args.need, args.mode, args.stack, args.platform, local, online))


if __name__ == "__main__":
    main()
