import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes import router

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[3]
CABSCRIPT_ROOT = Path(os.environ.get("CABSCRIPT_ROOT") or REPO_ROOT / "data")
CABSCRIPT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Cabinetry Designer")
app.include_router(router)

_STATIC = Path(__file__).parent / "static"
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
