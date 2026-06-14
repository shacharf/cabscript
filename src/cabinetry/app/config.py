import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[3]
CABSCRIPT_ROOT = Path(os.environ.get("CABSCRIPT_ROOT") or REPO_ROOT / "data")
CABSCRIPT_ROOT.mkdir(parents=True, exist_ok=True)
