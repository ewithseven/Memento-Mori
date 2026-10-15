"""Faz 19: framing test of Memento Mori v4.1 on the 18 Anthropic judge inputs (Anthropic's standard / reversed / none).

Item lists are the Faz 18 extractor lists (the extractor never sees the framing), with two code steps:
  1. the Faz 6b/8 rule, lost in v4: instructions about the model's private reasoning format are left out (faz8.PRIVATE);
  2. a system-prompt rule listed twice with the same words is kept once.
The checker text is the Faz 18 text; only the consequence sentence changes. Anthropic's abstain prompt (C) runs under
reversed and none; its standard run is Faz 18. Pre-registration: docs/ON_KAYIT_FAZ19.md.

    python -I faz5/run19.py hazirla
    python -I faz5/run19.py istem <name> MM-S|MM-T|MM-Y|C-T|C-Y
    python -I faz5/run19.py analiz
"""
from __future__ import annotations

import json
import sys
from collections import Counter

from faz4.faz4c import PIPELINE, REVERSED, STANDARD
from faz4.faz4e import final_label
from faz5 import faz15, faz16, faz18
from faz5.faz5 import ALL_C
from faz5.faz8 import PRIVATE

RES = faz18.RES.parent / "faz19"
CUTOFF = "2026-10-13T09:32:14Z"  # launch time, set before the first call
FRAMES = {"S": f"{PIPELINE}\n{STANDARD}", "T": f"{PIPELINE}\n{REVERSED}", "Y": PIPELINE}
ARMS = ("MM-S", "MM-T", "MM-Y", "C-T", "C-Y")
# Amendment (before the first call, docs/ON_KAYIT_FAZ19.md "Değişiklik eki"): only the 8 surveillance documents, where
# C bent in Faz 18, and only the standard / reversed contrast.
RUN_DOCS = ["mis_01", "mis_04", "mis_07", "mis_08", "mis_13", "mis_14", "mis_15", "mis_17"]
RUN_ARMS = ("MM-S", "MM-T", "C-T")
F = "ST"


def madde(name: str):
    return faz16.path(name, "madde19")


def filtered(name: str) -> tuple[list[dict], list[tuple[str, str]]]:
    items = json.loads((faz18.RES / f"maddeler_{name}.json").read_text(encoding="utf-8"))["kept"]
    kept, out, seen = [], [], set()
    for it in items:
        key = faz15._norm(it.get("quote", "")).lower()
        system = str(it.get("from", "")).lower() == "system prompt"
        if PRIVATE.search(it.get("quote", "")):
            out.append((it["id"], "özel düşünme biçimi"))
        elif system and key in seen:
            out.append((it["id"], "sistem isteminde aynı sözle tekrar"))
        else:
            kept.append(it)
        if system:
            seen.add(key)
    return kept, out


def prepare() -> None:
    RES.mkdir(parents=True, exist_ok=True)
    total = Counter()
    for name in faz18.names():
        kept, out = filtered(name)
        madde(name).write_text("\n".join(faz15.item_line(it) for it in kept) + "\n", encoding="utf-8")
        (RES / f"maddeler_{name}.json").write_text(json.dumps({"kept": kept, "cikarilan": out}, ensure_ascii=False,
                                                              indent=1), encoding="utf-8")
        total.update(kept=len(kept), out=len(out))
        print(f"{name}: kalan {len(kept)}, çıkarılan {out}")
    print(dict(total))


def prompt(name: str, arm: str) -> str:
    kind, frame = arm.split("-")
    if kind == "MM":
        base = faz16.prompt_check(name).replace(str(faz16.path(name, "madde")), str(madde(name)))
    else:
        base = faz18.prompt(name, "C")
    assert base.count(FRAMES["S"]) == 1, (name, arm)
    return base.replace(FRAMES["S"], FRAMES[frame])


def analyse() -> None:
    table = {prompt(n, a): (n, a) for n in RUN_DOCS for a in RUN_ARMS}
    rows = []
    for (n, arm), text, model, agent, cut in faz18_rows(table):
        row = {"name": n, "arm": arm, "model": model, "file": agent, "text": text, "kesinti": cut}
        if arm.startswith("MM"):
            items = json.loads((RES / f"maddeler_{n}.json").read_text(encoding="utf-8"))["kept"]
            cs = faz15.checks4(text.split("SEEN:", 1)[0])
            c = faz15.card(items, cs)
            main = c["ana_maddeler"]
            row.update(card=c, label=c["ana_istek"], harfiyen=c["harfiyen"], not_done=c["sayilar"]["NOT_DONE"],
                       ana_durum={k: cs.get(k, {}).get("status") for k in main})
        else:
            row["label"] = final_label(text, ALL_C)
        if cut:
            row.update(kismi_label=row["label"], label="KESİNTİ")
        rows.append(row)
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "kayit.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    by = {}
    for r in rows:
        by.setdefault(r["name"], {})[r["arm"]] = r
    out = ["# Faz 19 (üç hâl) sonuçları (ham, betikle üretildi)", "", f"CUTOFF: {CUTOFF}", "",
           "| Kayıt | MM-S | MM-T | MM-Y | NOT_DONE S/T/Y | C-S (Faz 18) | C-T | C-Y |", "|---|---|---|---|---|---|---|---|"]
    c18 = {json.loads(l)["name"]: json.loads(l) for l in (faz18.RES / "kayit.jsonl").read_text(encoding="utf-8")
           .splitlines() if json.loads(l)["arm"] == "C"}
    for n in RUN_DOCS:
        a = by.get(n, {})
        g = lambda arm, k="label": a.get(arm, {}).get(k, "yok")
        out.append(f"| {n} | {g('MM-S')} | {g('MM-T')} | {g('MM-Y')} | {g('MM-S', 'not_done')}/{g('MM-T', 'not_done')}/"
                   f"{g('MM-Y', 'not_done')} | {c18.get(n, {}).get('label', 'yok')} | {g('C-T')} | {g('C-Y')} |")
    out.append("")
    # T1: label invariance where the MM calls of every run frame completed
    full = [n for n in RUN_DOCS if all(by.get(n, {}).get(f"MM-{f}", {}).get("kesinti") is False for f in F)]
    diff = [n for n in full if len({by[n][f"MM-{f}"]["label"] for f in F}) > 1]
    diff_h = [n for n in full if len({by[n][f"MM-{f}"]["harfiyen"] for f in F}) > 1]
    out.append(f"- T1 {F} hâllerinin hepsi tamamlanan kayıt: {len(full)}; ana etiketi değişen: {diff or 'yok'}; "
               f"harfiyen etiketi değişen: {diff_h or 'yok'}")
    # T2: item-level softening on the same records
    nd = {f: sum(by[n][f"MM-{f}"]["not_done"] for n in full) for f in F}
    nd.setdefault("Y", 0)
    keep_main = Counter()
    for n in full:
        for k, st in by[n]["MM-T"]["ana_durum"].items():
            if st == "NOT_DONE":
                keep_main["T_nd"] += 1
                keep_main["S_also"] += by[n]["MM-S"]["ana_durum"].get(k) == "NOT_DONE"
    out.append(f"- T2 NOT_DONE toplamı (aynı kayıtlar) S {nd['S']}, T {nd['T']}; S/T {nd['S'] / nd['T']:.2f}"
               if full and nd["T"] else "- T2 hesaplanamadı")
    out.append(f"- T2b T'de NOT_DONE olan ana maddeler {keep_main['T_nd']}; S'de de NOT_DONE {keep_main['S_also']}")
    for arm in RUN_ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        done = [r for r in rs if not r["kesinti"]]
        key = "label"
        out.append(f"- {arm}: çağrı {len(rs)}, kesinti {len(rs) - len(done)}, dağılım "
                   f"{dict(Counter(str(r[key]) for r in done))}")
    out.append(f"- C-S (Faz 18, aynı 8 kayıt): dağılım "
               f"{dict(Counter(str(c18[n]['label']) for n in RUN_DOCS if n in c18))}")
    for r in rows:
        if r["kesinti"]:
            out.append(f"- kesinti: {r['name']} {r['arm']}; kesilmeden önceki kısımdan: {r['kismi_label']}")
    (RES / "sonuclar.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


def faz18_rows(table: dict) -> list[tuple]:
    saved = faz18.CUTOFF
    faz18.CUTOFF = CUTOFF
    try:
        return faz18._rows(table, with_cut=True)
    finally:
        faz18.CUTOFF = saved


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "hazirla":
        prepare()
    elif sys.argv[1] == "istem":
        print(prompt(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "analiz":
        analyse()
