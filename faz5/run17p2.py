"""Launcher for test A batch 2 with the T2-13 guard: python -I faz5/run17p2.py liste 2 | istem <name> <arm> |
maddeler | analiz. Same commands as faz17's own __main__ (sec is left out: the selection is sealed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from faz5 import faz17  # noqa: E402
import faz5.faz17_parti2  # noqa: E402,F401  (patches faz17._rows)

sys.stdout.reconfigure(encoding="utf-8")
cmd = sys.argv[1]
if cmd == "istem":
    print(faz17.prompt(sys.argv[2], sys.argv[3]))
elif cmd == "liste":
    print("\n".join(c["name"] for c in faz17.chosen(int(sys.argv[2]))))
elif cmd == "maddeler":
    faz17.items_step()
elif cmd == "analiz":
    faz17.analyse()
