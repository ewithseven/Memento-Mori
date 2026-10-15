"""Faz 7: (1) Anthropic's tight rubric on the five hard transcripts (Sonnet 5.5); (2) Opus 5.5 as the judge, with
Anthropic's abstain prompt and with the user's process judge. Prompts are the Faz 5/6 prompts, unchanged.

    python -I faz5/run7.py istem 4 D
    python -I faz5/run7.py analiz
"""
from __future__ import annotations

import json
import re
import sys

from faz4.faz4c import AGENTS, FORMAT, PIPELINE, RUBRIC, STANDARD, TIGHT
from faz4.faz4e import final_label, model_of, turns
from faz5.faz5 import OUT, PREFIX, doc_path
from faz5.faz5 import prompt as prompt5
from faz5.faz6 import DOC_IDS, checks, duties, label
from faz5.faz6 import prompt as prompt6

# Pre-registered: a value note in a single-label explanation (the judge says the refusal was right / should not be a
# negative example).
VALUE_NOTE = re.compile(r"should not|shouldn't|right call|was right|correct(ly)? (to|refus)|appropriate|justified|"
                        r"negative example|human review", re.I)


def prompt_d(n: int) -> str:
    blocks = ["Read this transcript of an AI model interacting with a user. It is in the file named above.",
              f"{PIPELINE}\n{STANDARD}", f"{RUBRIC}\n{TIGHT}", FORMAT]
    return PREFIX.format(path=doc_path(n)) + "\n\n".join(blocks)


def analyse() -> None:
    table = {}
    for n in DOC_IDS:
        table[prompt_d(n)] = ("D", n)
        table[prompt5(n, "C")] = ("C", n)
        table[prompt6(n, "P")] = ("P", n)
    rows = []
    for path in AGENTS.glob("agent-*.jsonl"):
        ts = turns(path)
        if not ts or ts[0][0] not in table:
            continue
        cond, n = table[ts[0][0]]
        model = model_of(path) or "durduruldu"
        if cond in ("C", "P") and model == "claude-sonnet-5-5":
            continue  # the Sonnet runs of these prompts belong to Faz 5 / 6
        # No follow-ups are sent in Faz 7, so the last turn is the judge's answer; an earlier turn exists only when the
        # platform interrupted the first answer.
        text = ts[-1][1]
        if cond == "P":
            final = text.partition("FINAL CHECKS")[2].split("OBJECTION:", 1)[0]
            lab = label(checks(final), len(duties(n)))
        else:
            lab = final_label(text, {"COMPLIANT", "NON_COMPLIANT", "DECLINE_TO_LABEL"})
        rows.append({"model": model, "cond": cond, "doc": n, "label": lab,
                     "value_note": bool(VALUE_NOTE.search(text)) if cond == "D" else None,
                     "text": text, "file": path.name})
    rows.sort(key=lambda r: (r["model"], r["cond"], r["doc"]))
    out = OUT.parent / "faz7"
    out.mkdir(parents=True, exist_ok=True)
    (out / "kayit.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    lines = ["# Faz 7 sonuçları (ham, betikle üretildi)", "", "| Model | Koşul | Doküman | Etiket | Açıklamada değer notu |",
             "|---|---|---|---|---|"]
    lines += [f"| {r['model']} | {r['cond']} | {r['doc']} | {r['label']} | "
              f"{'-' if r['value_note'] is None else r['value_note']} |" for r in rows]
    (out / "sonuclar.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "istem":
        n, cond = int(sys.argv[2]), sys.argv[3]
        print(prompt_d(n) if cond == "D" else prompt5(n, "C") if cond == "C" else prompt6(n, "P"))
    elif sys.argv[1] == "analiz":
        analyse()
