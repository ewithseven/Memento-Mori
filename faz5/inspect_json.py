"""Print the shape of one downloaded transcript JSON (keys, roles, short previews). Data only, nothing is executed.

    python -I faz5/inspect_json.py data/anthropic_mislabel/<file>.json
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
doc = json.load(open(sys.argv[1], encoding="utf-8"))


def shape(x, depth=0):
    pad = "  " * depth
    if isinstance(x, dict):
        for k, v in list(x.items())[:25]:
            kind = type(v).__name__
            extra = f" len={len(v)}" if isinstance(v, (list, str, dict)) else f" = {v!r}"[:80]
            print(f"{pad}{k}: {kind}{extra}")
            if isinstance(v, dict) and depth < 2:
                shape(v, depth + 1)
            elif isinstance(v, list) and v and depth < 2:
                print(f"{pad}  [0]:")
                shape(v[0], depth + 2)
    elif isinstance(x, str):
        print(f"{pad}{x[:120]!r}")


shape(doc)
print("notice:", doc.get("notice"))
msgs = doc.get("target_messages") or []
roles, keys, kinds = {}, set(), set()
for m in msgs:
    roles[m.get("role")] = roles.get(m.get("role"), 0) + 1
    keys |= set(m)
    kinds.add(type(m.get("content")).__name__)
print("roles:", roles, "keys:", sorted(keys), "content types:", kinds)
for m in msgs[:4]:
    c = m.get("content")
    print("---", m.get("role"), repr(c if isinstance(c, str) else json.dumps(c))[:400])
print("--- last", msgs[-1].get("role"), repr(msgs[-1].get("content"))[:400])
