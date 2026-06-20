# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

SRC = Path("src/cabinetry")

a = Analysis(
    [str(SRC / "__main__.py")],
    pathex=["src"],
    binaries=[],
    datas=[
        # Frontend build output → extracted to sys._MEIPASS/static/
        (str(SRC / "app" / "static"), "static"),
        # Stdlib YAML files → extracted alongside the cabinetry package
        (str(SRC / "stdlib" / "*.yaml"), "cabinetry/stdlib"),
    ],
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.lifespan.on",
        "anyio._backends._asyncio",
        "cabinetry.app.main",
        "cabinetry.app.routes",
        "cabinetry.dsl",
        "cabinetry.compiler",
        "cabinetry.geometry",
        "cabinetry.outputs",
        "cabinetry.stdlib",
        "trimesh",
        "scipy",
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="cabscript",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
