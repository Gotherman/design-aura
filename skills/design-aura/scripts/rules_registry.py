#!/usr/bin/env python3
"""Registro unico de regras da Design Aura (data/rules.json).

Cada regra pertence a uma camada que limita a severidade que ela pode emitir:
- invariant: oficio objetivo (pode bloquear);
- tell: sinal forte de interface generica (ate HIGH);
- craft: acabamento (ate MEDIUM);
- heuristic: sinal de gosto ou composicao medido por aproximacao (sai como REVIEW).
Os scripts produzem achados com a severidade que acharem certa; `apply_caps` impoe o teto
da camada, para que nenhuma heuristica trave a entrega.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ORDER = {"BLOCK": 0, "HIGH": 1, "REVIEW": 2, "MEDIUM": 3, "LOW": 4, "PASS": 9}
RULE_ID = re.compile(r"DA-[A-Z0-9]+(?:-[A-Z0-9]+)*")


@lru_cache(maxsize=1)
def load_rules() -> dict:
    data = json.loads((DATA / "rules.json").read_text(encoding="utf-8"))
    data["by_id"] = {r["id"]: r for r in data["rules"]}
    return data


def budgets_for(mode: str = "operate") -> dict:
    return dict(load_rules()["budgets"].get(mode, load_rules()["budgets"]["operate"]))


def cap(rule_id: str | None, severity: str) -> tuple[str, str | None]:
    """Devolve (severidade com teto da camada, camada)."""
    if not rule_id or severity in {"PASS", None}:
        return severity, None
    reg = load_rules()
    rule = reg["by_id"].get(rule_id)
    if not rule:
        return severity, None
    layer = rule["layer"]
    limit = reg["caps"].get(layer)
    if limit == "REVIEW":
        return "REVIEW", layer
    if limit and ORDER.get(severity, 9) < ORDER[limit]:
        return limit, layer
    return severity, layer


def apply_caps(findings: list[dict], rule_key: str = "rule", text_keys: tuple[str, ...] = ("label",)) -> list[dict]:
    for f in findings:
        rid = f.get(rule_key)
        if not rid:
            for key in text_keys:
                m = RULE_ID.search(str(f.get(key, "")))
                if m:
                    rid = m.group(0)
                    break
        new_sev, layer = cap(rid, f.get("severity"))
        if layer:
            f["severity"] = new_sev
            f["layer"] = layer
    return findings


def summary_counts(findings: list[dict]) -> dict:
    counts = {k: 0 for k in ("BLOCK", "HIGH", "REVIEW", "MEDIUM", "LOW")}
    for f in findings:
        if f.get("severity") in counts:
            counts[f["severity"]] += 1
    return counts
