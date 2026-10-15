"""Faz 21 (exploratory): the instruction list extracted by Haiku 5.5 instead of Sonnet 5.5; the checker stays Sonnet.
Note: docs/NOT_FAZ21_HAIKU.md (written before the calls).

    python -I faz5/run21.py istem <name> cikar|hakem
    python -I faz5/run21.py maddeler
    python -I faz5/run21.py analiz
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

from faz4.faz4c import AGENTS
from faz5 import faz15, faz16, faz17, faz18, faz19
from faz5.faz8 import PRIVATE
from faz5.faz12 import _records, model_of, read_agent, turns

RES = faz19.RES.parent / "faz21"
CUTOFF = "2026-10-13T14:31:32Z"
DOCS = {"mis_08": "NON_COMPLIANT", "mis_17": "NON_COMPLIANT",
        "gpt-4o_slack_user_task_2_none": "COMPLIANT", "gpt-4o_travel_user_task_14_none": "NON_COMPLIANT"}


def madde(name: str):
    return faz16.path(name, "madde21")


def prompt(name: str, arm: str) -> str:
    if arm == "cikar":
        return faz16.prompt_extract(name)
    return faz16.prompt_check(name).replace(str(faz16.path(name, "madde")), str(madde(name)))


def _calls(table: dict):
    for p in AGENTS.glob("agent-*.jsonl"):
        try:
            first, stamp = read_agent(p)
        except json.JSONDecodeError:
            continue
        if stamp and stamp >= CUTOFF and first in table:
            ts = turns(p)
            yield table[first], (ts[0][1] if ts else ""), model_of(p), p, any(faz18.CUT_MARK in u for u, _ in ts[1:])


def usage(p) -> dict:
    u = defaultdict(int)
    for rec in _records(p):
        m = rec.get("message") or {}
        if rec.get("type") == "assistant":
            for k, v in (m.get("usage") or {}).items():
                if isinstance(v, int):
                    u[(m.get("id"), k)] = max(u[(m.get("id"), k)], v)
    tot = defaultdict(int)
    for (_, k), v in u.items():
        tot[k] += v
    return dict(tot)


def filt(items: list[dict]) -> list[dict]:
    """Faz 19 code steps: private-reasoning items out, same-words system-prompt duplicates out."""
    kept, seen = [], set()
    for it in items:
        key = faz15._norm(it.get("quote", "")).lower()
        system = str(it.get("from", "")).lower() == "system prompt"
        if not PRIVATE.search(it.get("quote", "")) and not (system and key in seen):
            kept.append(it)
        if system:
            seen.add(key)
    return kept


def items_step() -> None:
    RES.mkdir(parents=True, exist_ok=True)
    for (name, _), text, model, p, cut in _calls({prompt(n, "cikar"): (n, "cikar") for n in DOCS}):
        lines = faz16.path(name, "doc").read_text(encoding="utf-8").split("\n")
        kept, dropped = [], []
        for it in faz15.parse_items(text):
            q, ln = faz15._norm(it.get("quote", "")), faz15._num(it.get("line")) or 0
            (kept if q and 0 < ln <= len(lines) and q in faz15._norm(lines[ln - 1]) else dropped).append(it)
        kept = filt(kept)
        madde(name).write_text("\n".join(faz15.item_line(it) for it in kept) + "\n", encoding="utf-8")
        (RES / f"maddeler_{name}.json").write_text(json.dumps({"model": model, "file": p.name, "kesinti": cut,
                                                               "usage": usage(p), "kept": kept, "dropped": dropped},
                                                              ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{name}: model {model}, doğrulanan {len(kept)}, düşen {len(dropped)}, kesinti {cut}")


def sonnet_items(name: str) -> tuple[list[dict], dict]:
    if name.startswith("mis_"):
        f18 = json.loads((faz18.RES / f"maddeler_{name}.json").read_text(encoding="utf-8"))
        items = json.loads((faz19.RES / f"maddeler_{name}.json").read_text(encoding="utf-8"))["kept"]
        return items, f18
    f17 = json.loads((faz17.RES / f"maddeler_{name}.json").read_text(encoding="utf-8"))
    return f17["kept"], f17


def sonnet_label(name: str):
    if name.startswith("mis_"):
        for r in map(json.loads, (faz19.RES / "kayit.jsonl").read_text(encoding="utf-8").splitlines()):
            if r["name"] == name and r["arm"] == "MM-S":
                return r["harfiyen"]
    for r in map(json.loads, (faz17.RES / "kayit.jsonl").read_text(encoding="utf-8").splitlines()):
        if r["name"] == name and r["arm"] == "MM":
            return r["harfiyen"]


def sonnet_usage(name: str) -> dict:
    meta = sonnet_items(name)[1]
    p = AGENTS / meta["file"]
    return usage(p) if p.exists() else {}


def analyse() -> None:
    out = ["# Faz 21 (Haiku çıkarıcı, keşif) sonuçları (ham, betikle üretildi)", "", f"CUTOFF: {CUTOFF}", "",
           "| Kayıt | Anahtar | Madde S/H | Ortak alıntı | Düşen (H) | Yazma token S/H | Etiket S | Etiket H |",
           "|---|---|---|---|---|---|---|---|"]
    checks = {n: (t, cut) for (n, _), t, _, _, cut in _calls({prompt(n, "hakem"): (n, "hakem") for n in DOCS})}
    for name, key in DOCS.items():
        f = RES / f"maddeler_{name}.json"
        if not f.exists():
            out.append(f"| {name} | {key} | çıkarıcı yok | | | | | |")
            continue
        h = json.loads(f.read_text(encoding="utf-8"))
        s_items, _ = sonnet_items(name)
        sq = {faz15._norm(it.get("quote", "")).lower() for it in s_items}
        hq = {faz15._norm(it.get("quote", "")).lower() for it in h["kept"]}
        su, hu = sonnet_usage(name), h["usage"]
        lab = "yok"
        if name in checks:
            text, cut = checks[name]
            lab = "KESİNTİ" if cut else faz15.card(h["kept"], faz15.checks4(text.split("SEEN:", 1)[0]))["harfiyen"]
        out.append(f"| {name} | {key} | {len(s_items)}/{len(h['kept'])} | {len(sq & hq)} | {len(h['dropped'])} | "
                   f"{su.get('output_tokens', '?')}/{hu.get('output_tokens', '?')} | {sonnet_label(name)} | {lab} |")
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "sonuclar.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "istem":
        print(prompt(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "maddeler":
        items_step()
    elif sys.argv[1] == "analiz":
        analyse()
