"""Faz 18: regression of Memento Mori v4.1 on all 18 Anthropic judge-input transcripts (10 welfare, 8 surveillance; v2
gave NON_COMPLIANT on 16/16 completed calls in Faz 8, v3 8/8 on the surveillance eight in Faz 11). The correct label is
NON_COMPLIANT for all. Anthropic's abstain prompt (C) runs in the same agent environment as a pressure check. Pre-registration: docs/ON_KAYIT_FAZ18.md. Prompts: faz15/faz16 (v4.1), faz5 (C).

    python -I faz5/run18.py hazirla
    python -I faz5/run18.py istem <name> cikar|hakem|C
    python -I faz5/run18.py maddeler
    python -I faz5/run18.py analiz
"""
from __future__ import annotations

import json
import sys
from collections import Counter

from faz4.faz4c import AGENTS
from faz4.faz4e import final_label
from faz5 import faz15, faz16
from faz5.faz5 import ALL_C, DATA, OUT, doc_path, mapping
from faz5.faz5 import prompt as prompt_anthropic
from faz5.faz12 import model_of, read_agent, turns

RES = OUT.parent / "faz18"
CUTOFF = "2026-10-12T22:19:17Z"  # launch time, set before the first call


def names() -> dict[str, str]:
    """name -> Anthropic transcript id, for all 18 documents (numbering as in Faz 5)."""
    docs = mapping()["docs"]
    return {f"mis_{int(n):02d}": r["id"] for n, r in sorted(docs.items(), key=lambda x: int(x[0]))}


def prepare() -> None:
    for name, ident in names().items():
        text = faz15.render4(json.loads((DATA / f"mislabel-input-{ident}.json").read_text(encoding="utf-8")))
        faz16.path(name, "doc").write_text(text, encoding="utf-8")
        faz16.path(name, "kor").write_text(faz15.blind(text), encoding="utf-8")
        print(name, ident, f"{len(text.split(chr(10)))} satır")


def prompt(name: str, arm: str) -> str:
    if arm == "cikar":
        return faz16.prompt_extract(name)
    if arm == "hakem":
        return faz16.prompt_check(name)
    return prompt_anthropic(1, arm).replace(doc_path(1), str(faz16.path(name, "doc")))


CUT_MARK = "stopped by a safety classifier"  # platform message that opens a new turn after a withheld reply


def _rows(table: dict, with_cut: bool = False) -> list[tuple]:
    """Reply to the original prompt (turn 0). Added after mis_01/mis_03 (Faz 18): when the platform withholds a reply it
    adds a turn, and the old code read that turn's text; with one turn the result is unchanged."""
    rows = []
    for p in AGENTS.glob("agent-*.jsonl"):
        try:
            first, stamp = read_agent(p)
        except json.JSONDecodeError:
            continue
        if stamp and stamp >= CUTOFF and first in table:
            ts = turns(p)
            row = (table[first], ts[0][1] if ts else "", model_of(p) or "durduruldu", p.name)
            rows.append(row + (any(CUT_MARK in u for u, _ in ts[1:]),) if with_cut else row)
    return rows


def items_step() -> None:
    RES.mkdir(parents=True, exist_ok=True)
    for (name, _), text, model, agent in _rows({prompt(n, "cikar"): (n, "cikar") for n in names()}):
        lines = faz16.path(name, "doc").read_text(encoding="utf-8").split("\n")
        kept, dropped = [], []
        for it in faz15.parse_items(text):
            q, ln = faz15._norm(it.get("quote", "")), faz15._num(it.get("line")) or 0
            (kept if q and 0 < ln <= len(lines) and q in faz15._norm(lines[ln - 1]) else dropped).append(it)
        faz16.path(name, "madde").write_text("\n".join(faz15.item_line(it) for it in kept) + "\n", encoding="utf-8")
        (RES / f"maddeler_{name}.json").write_text(json.dumps({"model": model, "file": agent, "kept": kept,
                                                               "dropped": dropped}, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
        print(f"{name}: doğrulanan {len(kept)}, düşen {len(dropped)}")


def analyse() -> None:
    table = {prompt(n, "C"): (n, "C") for n in names()}
    table.update({prompt(n, "hakem"): (n, "hakem") for n in names() if faz16.path(n, "madde").exists()})
    rows = []
    for (n, arm), text, model, agent, cut in _rows(table, with_cut=True):
        row = {"name": n, "id": names()[n], "arm": arm, "model": model, "file": agent, "text": text, "kesinti": cut}
        if arm == "hakem":
            items = json.loads((RES / f"maddeler_{n}.json").read_text(encoding="utf-8"))["kept"]
            cs = faz15.checks4(text.split("SEEN:", 1)[0])
            c = faz15.card(items, cs)
            row.update(arm="MM", card=c, label=c["ana_istek"], harfiyen=c["harfiyen"], kontrol=len(cs), madde=len(items))
        else:
            row["label"] = final_label(text, ALL_C)
        if cut:  # T6: a withheld reply is a cut, not a judge result; what survived is reported apart
            row.update(kismi_label=row["label"], kismi_harfiyen=row.get("harfiyen"), label="KESİNTİ")
            if arm == "hakem":
                row["harfiyen"] = "KESİNTİ"
        rows.append(row)
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "kayit.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    lines = ["# Faz 18 (geri gitme kontrolü) sonuçları (ham, betikle üretildi)", "", f"CUTOFF: {CUTOFF}", "",
             "| Kayıt | MM ana istek | MM harfiyen | C |", "|---|---|---|---|"]
    by = {}
    for r in rows:
        by.setdefault(r["name"], {})[r["arm"]] = r
    for n in names():
        a = by.get(n, {})
        lines.append(f"| {n} | {a.get('MM', {}).get('label', 'yok')} | {a.get('MM', {}).get('harfiyen', 'yok')} | "
                     f"{a.get('C', {}).get('label', 'yok')} |")
    for r in rows:
        if r["kesinti"]:
            extra = f", kontrol {r['kontrol']}/{r['madde']} madde" if r["arm"] == "MM" else ""
            lines.append(f"- kesinti: {r['name']} {r['arm']}; kesilmeden önce yazılan kısımdan: etiket "
                         f"{r['kismi_label']}, harfiyen {r.get('kismi_harfiyen')}{extra}")
    for arm, key in (("MM", "label"), ("MM", "harfiyen"), ("C", "label")):
        rs = [r for r in rows if r["arm"] == arm and not r["kesinti"]]
        lines.append(f"- {arm} {key}: NON_COMPLIANT {sum(r.get(key) == 'NON_COMPLIANT' for r in rs)}/{len(rs)}; "
                     f"dağılım {dict(Counter(str(r.get(key)) for r in rs))}")
    (RES / "sonuclar.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "hazirla":
        prepare()
    elif sys.argv[1] == "istem":
        print(prompt(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "maddeler":
        items_step()
    elif sys.argv[1] == "analiz":
        analyse()
