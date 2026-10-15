"""Launcher: python -I faz5/run.py <command> ...

Isolated mode keeps the downloaded data folder and the working directory out of the import path; the project root is
added explicitly.
"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
runpy.run_module("faz5.faz5", run_name="__main__")
