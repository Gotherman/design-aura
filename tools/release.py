#!/usr/bin/env python3
"""Release da Design Aura: paridade de versao, instalacoes locais e pacotes.

    python3 tools/release.py --check          # selos de versao iguais e instalacoes identicas ao repositorio
    python3 tools/release.py --sync           # copia as skills para as instalacoes, remove arquivos velhos e __pycache__, gera dist/
    python3 tools/release.py --sync --dest ~/outra/pasta/skills

Instalacoes padrao (so as que existem): ~/.claude/skills, ~/.agents/skills, ~/.codex/skills, ~/.gemini/config/skills.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAMES = ("design-aura", "designaura")
DEFAULT_DESTS = [Path.home() / p for p in (".claude/skills", ".agents/skills", ".codex/skills", ".gemini/config/skills")]


def skill_files(root: Path) -> dict:
    return {p.relative_to(root): p for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc" and p.name != ".DS_Store"}


def digest(root: Path) -> str:
    h = hashlib.sha256()
    for rel, p in sorted(skill_files(root).items()):
        h.update(str(rel).encode()); h.update(p.read_bytes())
    return h.hexdigest()[:16]


def version() -> str:
    m = re.search(r'version:\s*"([^"]+)"', (SKILLS / "design-aura" / "SKILL.md").read_text(encoding="utf-8"))
    return m.group(1)


def stamp_problems(v: str) -> list[str]:
    checks = {
        "skills/designaura/SKILL.md": [rf'version:\s*"{re.escape(v)}"', rf"`v{re.escape(v)}`"],
        "skills/design-aura/assets/design-bible-template.md": [rf"`v{re.escape(v)}`"],
        "skills/design-aura/data/rules.json": [rf'"version":\s*"{re.escape(v)}"'],
        "skills/design-aura/data/taxonomy.json": [rf'"version":\s*"{re.escape(v)}"'],
        ".claude-plugin/plugin.json": [rf'"version":\s*"{re.escape(v)}"'],
        ".claude-plugin/marketplace.json": [rf'"version":\s*"{re.escape(v)}"'],
        "README.md": [rf"`v{re.escape(v)}`"],
        "skills/design-aura/CHANGELOG.md": [rf"^## {re.escape(v)}\b"],
    }
    out = []
    for rel, pats in checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for pat in pats:
            if not re.search(pat, text, re.M):
                out.append(f"{rel}: selo {v} ausente ({pat})")
    stray = re.findall(r'"version":\s*"(\d+\.\d+\.\d+)"', (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    out += [f".claude-plugin/marketplace.json: versao divergente {s}" for s in stray if s != v]
    return out


def dests(extra: list[str]) -> list[Path]:
    found = [d for d in DEFAULT_DESTS if d.exists()]
    return found + [Path(e).expanduser() for e in extra]


def sync(targets: list[Path]) -> None:
    for name in NAMES:
        src = skill_files(SKILLS / name)
        for t in targets:
            root = t / name
            root.mkdir(parents=True, exist_ok=True)
            for p in sorted(root.rglob("*"), key=lambda x: -len(x.parts)):
                rel = p.relative_to(root)
                if p.is_file() and rel not in src:
                    p.unlink()
                elif p.is_dir() and (p.name == "__pycache__" or not any(p.iterdir())):
                    shutil.rmtree(p, ignore_errors=True)
            for rel, sp in src.items():
                dp = root / rel
                dp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sp, dp)


def build_dist(v: str) -> list[Path]:
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    files = sorted(skill_files(SKILLS / "design-aura").items())
    out = []
    for ext in ("zip", "skill"):
        path = dist / f"design-aura-v{v}.{ext}"
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for rel, p in files:
                z.write(p, Path("design-aura") / rel)
        out.append(path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sync", action="store_true")
    ap.add_argument("--dest", action="append", default=[])
    args = ap.parse_args()
    v = version()
    problems = stamp_problems(v)
    targets = dests(args.dest)
    if args.sync:
        if problems:
            print("Selos de versao divergentes; corrija antes de sincronizar:", *problems, sep="\n- ")
            return 1
        sync(targets)
        for p in build_dist(v):
            print(f"Pacote: {p}")
    ref = {name: digest(SKILLS / name) for name in NAMES}
    for t in targets:
        for name in NAMES:
            root = t / name
            if not root.exists():
                problems.append(f"{root}: instalacao ausente")
                continue
            if digest(root) != ref[name]:
                problems.append(f"{root}: difere do repositorio")
            junk = [p for p in root.rglob("*") if p.suffix == ".pyc" or p.name == "__pycache__"]
            if junk:
                problems.append(f"{root}: {len(junk)} arquivo(s) de cache")
    print(f"Design Aura v{v} · {len(targets)} instalacao(oes)")
    for p in problems:
        print(f"- {p}")
    if not problems:
        print("Paridade conferida: selos de versao iguais e instalacoes identicas ao repositorio.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
