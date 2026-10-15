"""Faz 24 (exploratory, few records): the frozen v3 process judge (faz10.prompt 'tam', faz9.duties_of code list) on
test A AgentDojo runs: does v3 say COMPLIANT where the key says so ("not a stone")? Note: docs/NOT_FAZ24_V3.md.

    python -I faz5/run24.py hazirla | istem <name> | analiz
"""
from __future__ import annotations

import json
import sys

from faz5 import faz10, faz16, faz17, faz21
from faz5.faz5 import doc_path
from faz5.faz8 import duties_path
from faz5.faz9 import duties_of

RES = faz17.RES.parent / "faz24"
CUTOFF = "SET-BEFORE-FIRST-CALL"
# Rule fixed before any call: the first 4 utility=True and the first 2 utility=False runs of the sealed batch 1 order.
_b1 = faz17.chosen(1)
DOCS = [c["name"] for c in _b1 if c["utility"]][:4] + [c["name"] for c in _b1 if not c["utility"]][:2]
KEY = {c["name"]: ("COMPLIANT" if c["utility"] else "NON_COMPLIANT") for c in _b1}


def gorev(name: str):
    return faz16.path(name, "gorev24")


def prepare() -> None:
    for n in DOCS:
        ds = duties_of(faz16.path(n, "doc").read_text(encoding="utf-8"))
        gorev(n).write_text("\n".join(f"D{k}. (line {i}) {t}" for k, (i, t) in enumerate(ds, 1)) + "\n", encoding="utf-8")
        print(n, KEY[n], f"{len(ds)} görev")


def prompt(name: str) -> str:
    return (faz10.prompt(1, "tam").replace(doc_path(1), str(faz16.path(name, "doc")))
            .replace(str(duties_path(1)), str(gorev(name))))


def analyse() -> None:
    saved, faz21.CUTOFF = faz21.CUTOFF, CUTOFF
    try:
        calls = list(faz21._calls({prompt(n): n for n in DOCS}))
    finally:
        faz21.CUTOFF = saved
    old = {(r["name"], r["arm"]): r for r in map(json.loads, (faz17.RES / "kayit.jsonl").read_text(encoding="utf-8")
                                                .splitlines())}
    rows = {}
    for n, text, model, p, cut in calls:
        count = len(gorev(n).read_text(encoding="utf-8").strip().splitlines())
        cs = faz10.checks(text.split("OBJECTION:", 1)[0])
        rows[n] = "KESİNTİ" if cut else faz10.label(cs, count)
    out = ["# Faz 24 (v3, test A, keşif) sonuçları", "", f"CUTOFF: {CUTOFF}", "",
           "| Kayıt | Anahtar | v3 | MM ana (Faz 17) | S (Faz 17) |", "|---|---|---|---|---|"]
    for n in DOCS:
        out.append(f"| {n} | {KEY[n]} | {rows.get(n, 'yok')} | {old.get((n, 'MM'), {}).get('label')} | "
                   f"{old.get((n, 'S'), {}).get('label')} |")
    ok = sum(rows.get(n) == KEY[n] for n in DOCS)
    out.append(f"\n- v3 anahtarla uyuşan: {ok}/{len(DOCS)}")
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "sonuclar.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"hazirla": prepare, "analiz": analyse}.get(sys.argv[1], lambda: print(prompt(sys.argv[2])))()
