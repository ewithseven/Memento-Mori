"""Faz 11: stress test at the highest reasoning effort. The eight surveillance transcripts are judged by Anthropic's
abstain judge (Faz 5, condition C) and by the frozen process judge v3 (Faz 10, full transcripts), with the prompts
unchanged; only the subagent effort is 'max'. Runs are told apart from the Faz 5 / Faz 10 runs by their first
timestamp.

    python -I faz5/run11.py istem 4 C      # or MM
    python -I faz5/run11.py analiz
"""
from __future__ import annotations

import json
import sys

from faz4.faz4c import AGENTS, read_agent
from faz4.faz4e import final_label, model_of, turns
from faz5.faz5 import ALL_C, OUT
from faz5.faz5 import prompt as prompt_c
from faz5.faz8 import duties
from faz5.faz9 import surveillance
from faz5.faz10 import STATUSES, checks, faz8_not_done, label
from faz5.faz10 import prompt as prompt_v3

CUTOFF = "2026-10-09T00:31:00Z"  # launch time, set before the first call


def prompt(n: int, arm: str) -> str:
    return prompt_c(n, "C") if arm == "C" else prompt_v3(n, "tam")


def effort_of(path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec.get("type") == "assistant" and rec.get("effort"):
            return rec["effort"]
    return None


def analyse() -> None:
    table = {prompt(n, a): (n, a) for n in surveillance() for a in ("C", "MM")}
    key = faz8_not_done()
    rows, unmatched = [], []
    for p in AGENTS.glob("agent-*.jsonl"):
        first, _, stamp = read_agent(p)
        if not stamp or stamp < CUTOFF:
            continue
        if first not in table:
            unmatched.append((p.name, stamp, first[:80]))
            continue
        n, arm = table[first]
        ts = turns(p)
        text = ts[-1][1] if ts else ""
        row = {"doc": n, "arm": arm, "model": model_of(p) or "durduruldu", "effort": effort_of(p), "turns": len(ts),
               "stamp": stamp, "file": p.name}
        if arm == "C":
            row["label"] = final_label(text, ALL_C)
        else:
            cs = checks(text.split("OBJECTION:", 1)[0])
            count = len(duties(n))
            objection = text.split("OBJECTION:", 1)[1].strip() if "OBJECTION:" in text else ""
            row.update(label=label(cs, count), duties=count, checked=len(cs),
                       counts={s: sum(v[0] == s for v in cs.values()) for s in STATUSES},
                       faz8_key_escaped=sorted(k for k in key.get(n, [])
                                               if cs.get(k, ("",))[0] in ("NOT_TRIGGERED", "NOT_AN_INSTRUCTION")),
                       objection_none=objection.upper().startswith("NONE") or not objection)
        row["text"] = text
        rows.append(row)
    rows.sort(key=lambda r: (r["arm"], r["doc"], r["stamp"]))
    out = OUT.parent / "faz11"
    out.mkdir(parents=True, exist_ok=True)
    (out / "kayit.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    lines = ["# Faz 11 sonuçları (ham, betikle üretildi)", "", f"CUTOFF: {CUTOFF}", "",
             "| İstem | Doküman | Model | Effort | Tur | Etiket | Görev/Kontrol | DONE/NOT_DONE/TRIG/NOTINS/UND | "
             "Faz 8 NOT_DONE'u kaçan | İtiraz |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["arm"] == "MM":
            c = r["counts"]
            extra = (f"{r['duties']}/{r['checked']} | {c['DONE']}/{c['NOT_DONE']}/{c['NOT_TRIGGERED']}/"
                     f"{c['NOT_AN_INSTRUCTION']}/{c['UNDETERMINABLE']} | {r['faz8_key_escaped'] or '-'} | "
                     f"{'NONE' if r['objection_none'] else 'var'}")
        else:
            extra = "- | - | - | -"
        lines.append(f"| {r['arm']} | {r['doc']} | {r['model']} | {r['effort']} | {r['turns']} | {r['label']} | {extra} |")
    for arm in ("C", "MM"):
        rs = [r for r in rows if r["arm"] == arm]
        done = [r for r in rs if r["model"] != "durduruldu" and r["effort"] == "max"]
        tally = {lab: sum(r["label"] == lab for r in done) for lab in sorted({str(r["label"]) for r in done})}
        lines.append(f"\n**{arm}:** çağrı {len(rs)}, tamamlanan ve effort=max {len(done)}; etiketler {tally}")
    if unmatched:
        lines += ["", "**CUTOFF'tan sonra hiçbir istemle eşleşmeyen dökümler:**"]
        lines += [f"- {name} {stamp} {head!r}" for name, stamp, head in sorted(unmatched, key=lambda u: u[1])]
    (out / "sonuclar.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "istem":
        print(prompt(int(sys.argv[2]), sys.argv[3]))
    elif sys.argv[1] == "analiz":
        analyse()
