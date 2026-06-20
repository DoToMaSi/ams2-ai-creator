# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

ROOT = Path(SPECPATH)
DATA_DIR = ROOT / "ams2_ai" / "data"
FLAGS_DIR = DATA_DIR / "flags"
ASSETS_DIR = ROOT / "assets"
STYLES_DIR = ROOT / "ams2_ai" / "ui" / "styles"
ICON_ICO = ASSETS_DIR / "icon" / "icon-artwork.ico"
if not ICON_ICO.is_file():
    raise SystemExit(
        f"Missing {ICON_ICO}. Run: python scripts/build_icon.py"
    )

datas = [
    (str(DATA_DIR / "countries.json"), "ams2_ai/data"),
    (str(DATA_DIR / "country_meta.json"), "ams2_ai/data"),
    (str(DATA_DIR / "tracks.json"), "ams2_ai/data"),
    (str(DATA_DIR / "track_meta.json"), "ams2_ai/data"),
    (str(DATA_DIR / "vehicle_classes.json"), "ams2_ai/data"),
    (str(FLAGS_DIR), "ams2_ai/data/flags"),
    (str(ASSETS_DIR / "fonts"), "assets/fonts"),
    (str(ASSETS_DIR / "icon"), "assets/icon"),
    (str(STYLES_DIR), "ams2_ai/ui/styles"),
    (str(ROOT / "LICENSE"), "."),
]

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=["faker", "faker.providers", "unidecode"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AMS2-AI-Creator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_ICO),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AMS2-AI-Creator",
)
