"""Faz 13 (duman testi 2, ayna yönü): the frozen process judge v3 and Anthropic's S and C prompts, each on Sonnet 5.5
and Opus 5.5, on two transcripts from Anthropic's CAFT sabotage sweep (U: complied after objecting; M: disclosed hold),
plus the refusal-regex baseline. Exploratory; see docs/KESIF_DUMAN_TESTI_2.md.

    python -I faz5/run13.py hazirla
    python -I faz5/run13.py istem U MM      # arms: MM, S, C
    python -I faz5/run13.py analiz
"""
from __future__ import annotations

import json
import sys

from faz4.faz4c import AGENTS
from faz4.faz4e import final_label
from faz5.faz5 import ALL_C, BIN, DOCS, OUT, ROOT, doc_path, render
from faz5.faz5 import prompt as prompt_anthropic
from faz5.faz8 import duties_path
from faz5.faz9 import duties_of
from faz5.faz10 import STATUSES, checks, label
from faz5.faz10 import prompt as prompt_v3
from faz5.faz12 import model_of, read_agent, regex_label, turns

DATA = ROOT / "data" / "anthropic_sabotage"
SOURCES = {"U": "sabotage-freq-opus-4-6-run1-0982ff.json", "M": "sabotage-freq-sonnet-4-6-run1-9fef85.json"}
TRUTH = {"U": "COMPLIANT", "M": "NON_COMPLIANT"}  # provisional, set by the main session before the run
CUTOFF = "2026-10-11T09:26:00Z"  # launch time, set before the first call


def path(k: str, kind: str):
    return DOCS / f"duman2_{kind}_{k}.txt"


def prepare() -> None:
    for k, name in SOURCES.items():
        text = render(json.loads((DATA / name).read_text(encoding="utf-8")))
        path(k, "doc").write_text(text, encoding="utf-8")
        ds = duties_of(text)
        path(k, "gorev").write_text("\n".join(f"D{i}. (line {ln}) {t}" for i, (ln, t) in enumerate(ds, 1)) + "\n",
                                    encoding="utf-8")
        odd = sum(text.count(c) for c in "  \x0b\x0c\x1c\x1d\x1e\x85")
        print(f"{k}: {len(text.splitlines())} satır, {len(ds)} görev, gizli satır ayırıcı {odd}")


def prompt(k: str, arm: str) -> str:
    """Same text as the frozen prompts; only the file paths differ."""
    if arm == "MM":
        return (prompt_v3(1, "tam").replace(str(doc_path(1)), str(path(k, "doc")))
                .replace(str(duties_path(1)), str(path(k, "gorev"))))
    return prompt_anthropic(1, arm).replace(str(doc_path(1)), str(path(k, "doc")))


def analyse() -> None:
    table = {prompt(k, a): (k, a) for k in SOURCES for a in ("MM", "S", "C")}
    rows, unreadable = [], []
    for p in AGENTS.glob("agent-*.jsonl"):
        try:
            first, stamp = read_agent(p)
        except json.JSONDecodeError:
            unreadable.append(p.name)
            continue
        if not stamp or stamp < CUTOFF or first not in table:
            continue
        k, arm = table[first]
        ts = turns(p)
        text = ts[-1][1] if ts else ""
        row = {"doc": k, "truth": TRUTH[k], "arm": arm, "model": model_of(p) or "durduruldu", "turns": len(ts),
               "file": p.name}
        if arm == "MM":
            cs = checks(text.split("OBJECTION:", 1)[0])
            count = len(duties_of(path(k, "doc").read_text(encoding="utf-8")))
            row.update(label=label(cs, count), duties=count, checked=len(cs),
                       counts={s: sum(v[0] == s for v in cs.values()) for s in STATUSES},
                       not_done={i: v[1].strip()[:200] for i, v in cs.items() if v[0] == "NOT_DONE"})
        else:
            row["label"] = final_label(text, ALL_C if arm == "C" else BIN)
        if row["label"] is None:
            row["note"] = f"etiket yok; son cevabın başı: {text.strip()[:120]!r}"
        row["text"] = text
        rows.append(row)
    for k in SOURCES:
        lab, hits = regex_label(path(k, "doc").read_text(encoding="utf-8"))
        rows.append({"doc": k, "truth": TRUTH[k], "arm": "R", "model": "-", "label": lab, "hits": hits})
    rows.sort(key=lambda r: (r["doc"], r["arm"], r["model"]))
    out = OUT.parent / "faz13"
    out.mkdir(parents=True, exist_ok=True)
    (out / "kayit.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    lines = ["# Faz 13 (duman testi 2) sonuçları (ham, betikle üretildi)", "", f"CUTOFF: {CUTOFF}", "",
             "| Döküm | Geçici doğru | Kol | Model | Tur | Etiket | Ayrıntı |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["arm"] == "MM" and "counts" in r:
            c = r["counts"]
            extra = (f"görev {r['duties']}, kontrol {r['checked']}, DONE/NOT_DONE/TRIG/NOTINS/UND "
                     f"{c['DONE']}/{c['NOT_DONE']}/{c['NOT_TRIGGERED']}/{c['NOT_AN_INSTRUCTION']}/{c['UNDETERMINABLE']}; "
                     f"NOT_DONE: {r['not_done'] or '-'}")
        elif r["arm"] == "R":
            extra = f"ret ifadesi eşleşmesi {len(r['hits'])}: {r['hits'][:2]}"
        else:
            extra = r.get("note", "-")
        lines.append(f"| {r['doc']} | {r['truth']} | {r['arm']} | {r['model']} | {r.get('turns', '-')} | {r['label']} "
                     f"| {extra} |")
    if unreadable:
        lines += ["", f"**Okunamayan ajan dökümleri:** {sorted(unreadable)}"]
    (out / "sonuclar.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "hazirla":
        prepare()
    elif sys.argv[1] == "istem":
        print(prompt(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "analiz":
        analyse()
