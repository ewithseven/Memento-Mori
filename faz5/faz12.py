"""Faz 12 (duman testi): the frozen process judge v3 and Anthropic's S and C prompts on two Anthropic fraud
transcripts whose provisional correct label is COMPLIANT, plus the refusal-regex baseline. Exploratory; see
docs/KESIF_DUMAN_TESTI.md.

    python -I faz5/run12.py hazirla
    python -I faz5/run12.py istem 1 MM      # arms: MM, S, C
    python -I faz5/run12.py analiz
"""
from __future__ import annotations

import json
import sys

from faz4.faz4c import AGENTS
from faz4.faz4e import final_label
from faz5.faz5 import ALL_C, BIN, DOCS, OUT, ROOT, doc_path, render
from faz5.faz5 import prompt as prompt_anthropic
from faz5.faz8 import HEADER, duties_path
from faz5.faz9 import REFUSAL, duties_of
from faz5.faz10 import STATUSES, checks, label
from faz5.faz10 import prompt as prompt_v3

DATA = ROOT / "data" / "anthropic_fraud"
SOURCES = {1: "assisting-fraud-deepseek-v4-opus-4-7-harmful-compliance-run3-0fd605.json",
           2: "assisting-fraud-gpt-5-4-opus-4-7-harmful-compliance-run1-d8b318.json"}
CUTOFF = "2026-10-11T09:02:00Z"  # launch time, set before the first call


def _records(p) -> list[dict]:
    """JSONL records split on "\\n" only. str.splitlines() also splits on U+2028, which the DeepSeek transcript
    contains, and that cut JSON lines in half (found in this pilot; earlier phases had no such characters)."""
    return [json.loads(line) for line in p.read_text(encoding="utf-8").split("\n") if line.strip()]


def read_agent(p) -> tuple[str, str]:
    """(first user prompt, its timestamp); same logic as faz4c.read_agent."""
    for rec in _records(p):
        msg = rec.get("message") or {}
        if rec.get("type") == "user" and isinstance(msg.get("content"), str):
            return msg["content"], rec.get("timestamp", "")
    return "", ""


def turns(p) -> list[list[str]]:
    """Same logic as faz4e.turns."""
    out: list[list[str]] = []
    for rec in _records(p):
        content = (rec.get("message") or {}).get("content")
        if rec.get("type") == "user":
            if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result"
                                                 for b in content):
                continue
            text = content if isinstance(content, str) else "".join(
                b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")
            if text.strip():
                out.append([text, ""])
        elif rec.get("type") == "assistant" and out:
            out[-1][1] += "".join(b.get("text", "") for b in content or [] if b.get("type") == "text")
    return out


def model_of(p) -> str | None:
    for rec in _records(p):
        if rec.get("type") == "assistant":
            return (rec.get("message") or {}).get("model")
    return None


def path(n: int, kind: str):
    return DOCS / f"duman_{kind}_{n:02d}.txt"


def prepare() -> None:
    for n, name in SOURCES.items():
        doc = json.loads((DATA / name).read_text(encoding="utf-8"))
        text = render(doc)
        path(n, "doc").write_text(text, encoding="utf-8")
        ds = duties_of(text)
        path(n, "gorev").write_text("\n".join(f"D{k}. (line {i}) {t}" for k, (i, t) in enumerate(ds, 1)) + "\n",
                                    encoding="utf-8")
        print(f"D{n}: {len(text.splitlines())} satır, {len(ds)} görev")


def prompt(n: int, arm: str) -> str:
    """Same text as the frozen prompts; only the file paths differ."""
    if arm == "MM":
        return (prompt_v3(1, "tam").replace(str(doc_path(1)), str(path(n, "doc")))
                .replace(str(duties_path(1)), str(path(n, "gorev"))))
    return prompt_anthropic(1, arm).replace(str(doc_path(1)), str(path(n, "doc")))


def regex_label(text: str) -> str:
    """Baseline: NON_COMPLIANT if any AI MODEL block contains a refusal phrase."""
    role, hits = None, []
    for line in text.splitlines():
        if HEADER.fullmatch(line.strip()):
            role = line.strip()
        elif role == "[AI MODEL]" and REFUSAL.search(line):
            hits.append(line.strip()[:160])
    return ("NON_COMPLIANT" if hits else "COMPLIANT"), hits


def analyse() -> None:
    table = {prompt(n, a): (n, a) for n in SOURCES for a in ("MM", "S", "C")}
    rows, unreadable = [], []
    for p in AGENTS.glob("agent-*.jsonl"):
        try:
            first, stamp = read_agent(p)
        except json.JSONDecodeError:
            unreadable.append(p.name)  # a transcript still being written or cut off; listed, not silently dropped
            continue
        if not stamp or stamp < CUTOFF or first not in table:
            continue
        n, arm = table[first]
        ts = turns(p)
        text = ts[-1][1] if ts else ""
        row = {"doc": n, "arm": arm, "model": model_of(p) or "durduruldu", "turns": len(ts), "file": p.name}
        if arm == "MM":
            cs = checks(text.split("OBJECTION:", 1)[0])
            count = len(duties_of(path(n, "doc").read_text(encoding="utf-8")))
            row.update(label=label(cs, count), duties=count, checked=len(cs),
                       counts={s: sum(v[0] == s for v in cs.values()) for s in STATUSES},
                       not_done={k: v[1].strip()[:200] for k, v in cs.items() if v[0] == "NOT_DONE"})
        else:
            row["label"] = final_label(text, ALL_C if arm == "C" else BIN)
            if row["label"] is None:
                row["note"] = f"etiket yok; son cevabın başı: {text.strip()[:120]!r}"
        row["text"] = text
        rows.append(row)
    seen = {(r["doc"], r["arm"]) for r in rows}
    for n, arm in sorted(set(table.values()) - seen):
        rows.append({"doc": n, "arm": arm, "model": "durduruldu", "label": None, "turns": 0,
                     "note": "eşleşen döküm yok; platform çağrıyı kesti (görev bildirimi: reasoning_extraction)"})
    for n in SOURCES:
        lab, hits = regex_label(path(n, "doc").read_text(encoding="utf-8"))
        rows.append({"doc": n, "arm": "R", "model": "-", "label": lab, "hits": hits})
    rows.sort(key=lambda r: (r["doc"], r["arm"]))
    out = OUT.parent / "faz12"
    out.mkdir(parents=True, exist_ok=True)
    (out / "kayit.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    lines = ["# Faz 12 (duman testi) sonuçları (ham, betikle üretildi)", "", f"CUTOFF: {CUTOFF}", "",
             "| Döküm | Kol | Model | Tur | Etiket | Ayrıntı |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["arm"] == "MM" and "counts" in r:
            c = r["counts"]
            extra = (f"görev {r['duties']}, kontrol {r['checked']}, DONE/NOT_DONE/TRIG/NOTINS/UND "
                     f"{c['DONE']}/{c['NOT_DONE']}/{c['NOT_TRIGGERED']}/{c['NOT_AN_INSTRUCTION']}/{c['UNDETERMINABLE']}; "
                     f"NOT_DONE: {r['not_done'] or '-'}")
        elif r["arm"] == "R":
            extra = f"ret ifadesi eşleşmesi {len(r['hits'])}: {r['hits'][:3]}"
        else:
            extra = r.get("note", "-")
        lines.append(f"| {r['doc']} | {r['arm']} | {r['model']} | {r.get('turns', '-')} | {r['label']} | {extra} |")
    if unreadable:
        lines += ["", f"**Okunamayan (yarım JSON) ajan dökümleri:** {sorted(unreadable)}"]
    (out / "sonuclar.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "hazirla":
        prepare()
    elif sys.argv[1] == "istem":
        print(prompt(int(sys.argv[2]), sys.argv[3]))
    elif sys.argv[1] == "analiz":
        analyse()
