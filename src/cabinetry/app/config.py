import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_FROZEN = getattr(sys, "frozen", False)

if os.environ.get("CABSCRIPT_ROOT"):
    CABSCRIPT_ROOT = Path(os.environ["CABSCRIPT_ROOT"])
elif _FROZEN:
    CABSCRIPT_ROOT = Path.home() / ".cabscript"
else:
    CABSCRIPT_ROOT = Path(__file__).resolve().parents[3] / "data"
CABSCRIPT_ROOT.mkdir(parents=True, exist_ok=True)
