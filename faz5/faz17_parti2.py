"""Guard for test A batch 2 (audit round 2, T2-13). faz17.py is sealed and unchanged; this only narrows which agent
transcripts its steps read: Sonnet 5.5 calls only, and per (document, arm) the earliest one. Faz 21 sent Haiku calls
with the same extractor prompts, so without this the batch 1 list of gpt-4o_slack_user_task_2_none would be
overwritten.

    python -I faz5/run17p2.py liste 2 | istem <name> cikar|hakem|S|C | maddeler | analiz
"""
from __future__ import annotations

import json

from faz5 import faz17
from faz5.faz12 import model_of, read_agent, turns

MODEL = "claude-sonnet-5-5"


def _rows(table: dict) -> list[tuple]:
    best = {}
    for p in faz17.AGENTS.glob("agent-*.jsonl"):
        try:
            first, stamp = read_agent(p)
        except json.JSONDecodeError:
            continue
        if stamp and stamp >= faz17.CUTOFF and first in table and model_of(p) == MODEL:
            key = table[first]
            if key not in best or stamp < best[key][0]:
                ts = turns(p)
                best[key] = (stamp, (key, ts[-1][1] if ts else "", MODEL, p.name))
    return [row for _, row in best.values()]


faz17._rows = _rows
