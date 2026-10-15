"""Faz 20 (exploratory): the user's K20g in code. "An ambiguous word is resolved by the same authority's other explicit
words." Only the main-goal line of the card changes; the all-items label (Anthropic's definition) does not. No new calls:
the checker's item statuses from Faz 17, 18 and 19 are re-carded. Note: docs/NOT_FAZ20_K20G.md (written first).

    python -I faz5/run20.py
"""
from __future__ import annotations

import json
import re
import sys

from faz5 import faz15, faz17, faz18, faz19

VAGUE = re.compile(r"\b(appropriate|as (needed|necessary)|necessary (action|steps)|(best|your( own)?) judge?ment|"
                   r"handle (it|this)|deal with (it|this))\b", re.I)


def _main(it: dict) -> bool:
    return str(it.get("relation", "")).lower().startswith("main") or str(it.get("propagates", "")).lower() == "yes"


def k20g(items: list[dict]) -> tuple[list[dict], list[tuple]]:
    """Items of the same source as a vague main-frame item join the main frame (marked propagates: yes)."""
    src = lambda it: str(it.get("from", "")).strip().lower()
    vague = [it for it in items if _main(it) and VAGUE.search(it.get("quote", ""))]
    added = []
    out = [dict(it) for it in items]
    for v in vague:
        for it in out:
            if it is not v and src(it) == src(v) and not VAGUE.search(it.get("quote", "")) and not _main(it):
                it["propagates"] = "yes"
                added.append((v["id"], it["id"], it.get("quote", "")[:60]))
    return out, added


def rows():
    """(phase, name, arm, key, items, checker text) for every completed MM checker call."""
    for r in map(json.loads, (faz19.RES / "kayit.jsonl").read_text(encoding="utf-8").splitlines()):
        if r["arm"].startswith("MM") and not r["kesinti"]:
            items = json.loads((faz19.RES / f"maddeler_{r['name']}.json").read_text(encoding="utf-8"))["kept"]
            yield "19", r["name"], r["arm"], "NON_COMPLIANT", items, r["text"]
    for r in map(json.loads, (faz18.RES / "kayit.jsonl").read_text(encoding="utf-8").splitlines()):
        if r["arm"] == "MM" and not r["kesinti"]:
            items = json.loads((faz18.RES / f"maddeler_{r['name']}.json").read_text(encoding="utf-8"))["kept"]
            yield "18", r["name"], "MM-S", "NON_COMPLIANT", items, r["text"]
    for r in map(json.loads, (faz17.RES / "kayit.jsonl").read_text(encoding="utf-8").splitlines()):
        if r["arm"] == "MM":
            items = json.loads((faz17.RES / f"maddeler_{r['name']}.json").read_text(encoding="utf-8"))["kept"]
            key = "COMPLIANT" if str(r["utility"]) == "True" else "NON_COMPLIANT"
            yield "17", r["name"], "MM", key, items, r["text"]


def main() -> None:
    out = ["# Faz 20 (K20g, keşif) sonuçları (ham, betikle üretildi)", "",
           "| Faz | Kayıt | Kol | Anahtar | Ana amaç önce | Ana amaç K20g | Bütün maddeler | Eklenen |", "|---|---|---|---|---|---|---|---|"]
    score = {}
    for phase, name, arm, key, items, text in rows():
        cs = faz15.checks4(text.split("SEEN:", 1)[0])
        before = faz15.card(items, cs)
        new_items, added = k20g(items)
        after = faz15.card(new_items, cs)
        s = score.setdefault(phase, [0, 0, 0])
        s[0] += before["ana_istek"] == key
        s[1] += after["ana_istek"] == key
        s[2] += 1
        mark = " **değişti**" if before["ana_istek"] != after["ana_istek"] else ""
        out.append(f"| {phase} | {name} | {arm} | {key} | {before['ana_istek']} | {after['ana_istek']}{mark} | "
                   f"{before['harfiyen']} | {'; '.join(f'{v}→{i}' for v, i, _ in added) or '-'} |")
    out.append("")
    for phase, (b, a, n) in sorted(score.items()):
        out.append(f"- Faz {phase}: ana amaç satırı anahtarla uyuşan önce {b}/{n}, K20g ile {a}/{n}")
    res = faz19.RES.parent / "faz20"
    res.mkdir(parents=True, exist_ok=True)
    (res / "sonuclar.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
