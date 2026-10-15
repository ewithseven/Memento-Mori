"""Launcher: python -I faz5/run7.py <command> ... (see faz5/faz7.py)."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
runpy.run_module("faz5.faz7", run_name="__main__")
