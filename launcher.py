"""Launch the game with its bundled resources available from any directory."""

import os
from pathlib import Path
import runpy
import sys


resource_directory = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
os.chdir(resource_directory)
runpy.run_module("jeopardyGame", run_name="__main__")
