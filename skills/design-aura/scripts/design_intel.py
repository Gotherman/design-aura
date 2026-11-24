#!/usr/bin/env python3
"""Motor offline BM25 de inteligencia de design da skill Design Aura.

Consulta os catalogos locais (domains.json, typography.json, patterns.json e a base
pre-categorizada data/catalog/) sem dependencias externas ou acesso a rede. Tudo o que
sai daqui e hipotese: a marca, o fluxo real e a direcao escolhida prevalecem.
"""
import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def normalize_text(text: str) -> list[str]:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1 = k1
        self.b = b
        self.n = len(docs)
        self.avgdl = sum(len(d) for d in docs) / max(1, self.n)
        self.df = Counter()
        self.tf = []
        for doc in docs:
            counts = Counter(doc)
            self.tf.append(counts)
            for term in counts:
                self.df[term] += 1

    def score(self, query_tokens: list[str], idx: int) -> float:
        doc = self.docs[idx]
        if not doc or not query_tokens:
            return 0.0
        dl = len(doc)
        tf_doc = self.tf[idx]
        total = 0.0
        for q in query_tokens:
            if q not in tf_doc:
                continue
            df_q = self.df[q]
            idf = math.log(1.0 + (self.n - df_q + 0.5) / (df_q + 0.5))
            freq = tf_doc[q]
            denom = freq + self.k1 * (1.0 - self.b + self.b * (dl / self.avgdl))
            total += idf * ((freq * (self.k1 + 1.0)) / max(1e-9, denom))
        return total


def load_json(name: str) -> list[dict]:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Catalogo ausente: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def match_platform(item_platforms: list[str], platform: str) -> bool:
    if platform == "all":
        return True
    if not item_platforms:
        return True
    if platform in item_platforms:
        return True
    if platform == "mobile" and any(p in item_platforms for p in ("ios", "android", "mobile")):
        return True
    return False


def rank_items(
    items: list[dict],
    query: str,
    text_fn,
    platform: str = "all",
    extra_filter=None,
    top: int = 3,
) -> list[dict]:
    filtered = [
        item for item in items
        if match_platform(item.get("platforms", []), platform)
        and (extra_filter(item) if extra_filter else True)
    ]
    if not filtered:
        filtered = list(items)
    docs = [normalize_text(text_fn(item)) for item in filtered]
    bm25 = BM25(docs)
    q_tokens = normalize_text(query)
    scored = []
    for i, item in enumerate(filtered):
        s = bm25.score(q_tokens, i)
        scored.append((s, i, item))
    scored.sort(key=lambda x: (x[0], -x[1]), reverse=True)
    return [x[2] for x in scored[:top]]


def build_report(query: str, platform: str, stack: str, top: int) -> dict:
    domains = load_json("domains.json")
    typography = load_json("typography.json")
    from discover_oss_components import load_catalog, stack_ok  # import tardio evita ciclo

    components = [c for c in load_catalog() if c["kind"] not in {"gallery", "anatomy", "official", "study", "license-trap"} and c["license_ok"]]
    patterns = load_json("patterns.json")

    typo_map = {t["id"]: t for t in typography}

    top_domains = rank_items(
        domains,
        query,
        lambda d: " ".join([
            d["name"],
            " ".join(d.get("keywords", [])),
            d.get("layout_archetype", ""),
            " ".join(d.get("signature_moves", [])),
        ]),
        platform=platform,
        top=top,
    )

    preferred_typo_ids = []
    for d in top_domains:
        for tid in d.get("typography_ids", []):
            if tid in typo_map and tid not in preferred_typo_ids:
                preferred_typo_ids.append(tid)

    # Uma familia por personalidade: a direcao compara opcoes de fato diferentes.
    top_typography, seen_pers = [], set()
    for tid in preferred_typo_ids:
        t = typo_map[tid]
        if t.get("personality") in seen_pers:
            continue
        seen_pers.add(t.get("personality"))
        top_typography.append(t)
        if len(top_typography) >= top:
            break
    if len(top_typography) < top:
        more_typo = rank_items(
            typography,
            query,
            lambda t: f"{t['name']} {t.get('mood', '')} {' '.join(t.get('platforms', []))}",
            platform=platform,
            top=top + 2,
        )
        seen = {t["id"] for t in top_typography}
        for t in more_typo:
            if t["id"] not in seen and len(top_typography) < top:
                top_typography.append(t)
                seen.add(t["id"])

    top_patterns = rank_items(
        patterns,
        query,
        lambda p: f"{p['name']} {p['when_to_use']} {' '.join(p.get('anatomy', []))}",
        platform=platform,
        top=max(3, top),
    )

    def stack_filter(c: dict) -> bool:
        return stack_ok(c, stack)

    top_components = rank_items(
        components,
        query,
        lambda c: f"{c['name']} {' '.join(c.get('needs', []))} {' '.join(c.get('categories', []))} {c['use_case']}",
        platform=platform,
        extra_filter=stack_filter,
        top=max(5, top + 2),
    )

    return {
        "query": query,
        "filters": {"platform": platform, "stack": stack},
        "domains": top_domains,
        "typography": top_typography,
        "patterns": top_patterns,
        "components_oss": top_components,
    }


def format_markdown(report: dict) -> str:
    lines = [
        f"# Design Aura Intel — Consulta: `{report['query']}`",
        f"- **Filtros:** plataforma=`{report['filters']['platform']}` · stack=`{report['filters']['stack']}`",
        "- **Isto é hipótese de catálogo, não a pele do projeto.** Paleta, arquétipo e assinatura só entram na Bíblia se combinam com o planejamento, o repositório e o fluxo de trabalho já lidos. Se não combinam, recuse e escreva a recusa no contrato.",
        "",
        "## 1. Domínios & Direções (hipótese, a confirmar)",
    ]
    for i, d in enumerate(report["domains"], 1):
        ideas = " · ".join(f"`{c['seed']}` + `{c['accent']}` ({c['harmony']}: {c['why']})" for c in d.get("color_ideas", []))
        lines.extend([
            f"### {i}. {d['name']} (`{d['id']}`)",
            f"- **Modo:** `{d['surface_mode']}` · **Densidade:** `{d['density']}` · **Plataformas:** `{', '.join(d['platforms'])}` · **Profundidade sugerida:** {d.get('depth_hint', '')}",
            f"- **Arquétipo provável:** {d['layout_archetype']}",
            f"- **Sementes de cor (gere a paleta com `generate_tokens.py --seed`):** {ideas}",
            f"- **Assinaturas possíveis:** {'; '.join(d.get('signature_moves', []))}",
            f"- **Erros comuns do setor:** {'; '.join(d.get('anti_patterns', []))}",
            "",
        ])

    lines.append("## 2. Tipografia: uma opção por personalidade")
    for t in report["typography"]:
        lines.append(
            f"- **{t['name']}** (`{t['id']}` · {t.get('personality', '')} · {t.get('license', '')}): {t['mood']} · tracking de display `{t['tracking_display']}` · medida `{t['body_measure']}`"
        )
    lines.append("- Teste cada opção com conteúdo real do projeto: números, nomes longos e acentos (ç, ã, õ).")
    lines.append("")

    lines.append("## 3. Padrões de Arquitetura & Interação")
    for p in report["patterns"]:
        lines.append(f"- **{p['name']}** ({', '.join(p['platforms'])}): {p['when_to_use']}")
        lines.append(f"  - Anatomia: {' → '.join(p['anatomy'])}")
        lines.append(f"  - Evitar: {'; '.join(p['avoid'])}")
    lines.append("")

    lines.append("## 4. Componentes relacionados (amostra da base)")
    for c in report["components_oss"]:
        lines.append(f"- **{c['name']}** (`{','.join(c.get('stack', []))}` · {c['license']} · {c['url']}): {c['use_case']}")
    lines.append("")
    lines.append("Para mapear as necessidades do projeto inteiro na base pre-categorizada, rode `discover_oss_components.py --scan <caminho-do-projeto> --stack <stack> --platform <platform> --mode <modo>`.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pesquisa offline BM25 de inteligencia de design Design Aura.")
    parser.add_argument("query", help="Descricao do produto, dominio ou interface")
    parser.add_argument(
        "--platform",
        default="all",
        choices=["all", "desktop", "mobile", "system", "ios", "android"],
        help="Filtrar por plataforma alvo",
    )
    parser.add_argument(
        "--stack",
        default="all",
        choices=["all", "html", "react", "next", "vue", "nuxt", "svelte", "solid", "angular", "electron", "tauri", "rn", "expo", "flutter", "ios", "android"],
        help="Filtrar bibliotecas OSS por stack",
    )
    parser.add_argument("--top", type=int, default=3, help="Quantidade maxima de dominios/tipografias")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"], help="Formato de saida")
    args = parser.parse_args()

    try:
        report = build_report(args.query, args.platform, args.stack, max(1, args.top))
    except Exception as exc:
        print(f"Erro ao consultar catalogo Design Aura: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(report))


if __name__ == "__main__":
    main()
