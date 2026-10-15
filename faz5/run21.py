"""Launcher: python -I faz5/run21.py <command> ... (see faz5/faz21.py)."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
runpy.run_module("faz5.faz21", run_name="__main__")
