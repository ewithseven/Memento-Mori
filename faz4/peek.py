"""Faz 4a: why do judges call refusals COMPLIANT, and do they cite the training consequence?"""
import json
import re

from .judge_check import OUT

rows = [json.loads(l) for l in (OUT / "kayit.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
motive = re.compile(r"training|negative example|discourage|future model|checkpoint", re.I)
for m in ("qwen2.5:7b", "ministral-3:8b"):
    wrong = [r for r in rows if r["model"] == m and r["truth"] == "NON_COMPLIANT" and r["label"] == "COMPLIANT"]
    std = [r for r in wrong if r["condition"] == "standart"]
    cites = [r for r in std if motive.search(r["text"])]
    print(f"== {m}: yanlış COMPLIANT {len(wrong)}; standart koşulda {len(std)}, bunların {len(cites)}'i eğitim sonucunu anıyor")
    for r in (cites[:1] or std[:1]) + [r for r in wrong if r["condition"] == "yok"][:1]:
        print(f"-- vaka {r['case']} / {r['condition']}:", " ".join(r["text"].split())[:420])
