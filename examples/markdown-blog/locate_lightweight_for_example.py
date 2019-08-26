import os
import sys
from pathlib import Path

_fp = Path(os.path.realpath(__file__))
os.chdir(_fp.parent)
sys.path.append(str(_fp.parent.parent.parent))
