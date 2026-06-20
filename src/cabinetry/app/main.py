import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes import router

load_dotenv()

# When frozen by PyInstaller, __file__ is inside a temp dir; use _MEIPASS as base.
_FROZEN = getattr(sys, "frozen", False)
_BASE = Path(sys._MEIPASS) if _FROZEN else Path(__file__).parent  # type: ignore[attr-defined]

_STATIC = _BASE / "static"

# Output directory: env var → ~/.cabscript (frozen) → repo/data (dev)
if os.environ.get("CABSCRIPT_ROOT"):
    CABSCRIPT_ROOT = Path(os.environ["CABSCRIPT_ROOT"])
elif _FROZEN:
    CABSCRIPT_ROOT = Path.home() / ".cabscript"
else:
    CABSCRIPT_ROOT = Path(__file__).resolve().parents[3] / "data"
CABSCRIPT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Cabinetry Designer")
app.include_router(router)

app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")
_ASSETS = _STATIC / "assets"
if _ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=str(_ASSETS)), name="assets")


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(str(_STATIC / "favicon.ico"))


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(_STATIC / "index.html"))
