"""Resolve bundled UI assets in dev and PyInstaller builds."""

from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def asset_path(*parts: str) -> Path:
    relative = Path("assets").joinpath(*parts)
    if getattr(sys, "frozen", False):
        frozen_path = Path(sys._MEIPASS) / relative
        if frozen_path.exists():
            return frozen_path
    return project_root() / relative


def font_paths() -> list[Path]:
    names = (
        "Rubik-Regular.ttf",
        "Rubik-Medium.ttf",
        "Rubik-SemiBold.ttf",
        "Rubik-Bold.ttf",
        "Rubik-Italic.ttf",
    )
    return [asset_path("fonts", name) for name in names]


def font_path() -> Path:
    return asset_path("fonts", "Rubik-Regular.ttf")


def icon_png_path() -> Path:
    return asset_path("icon", "icon-artwork.png")


def icon_ico_path() -> Path:
    return asset_path("icon", "icon-artwork.ico")


def license_path() -> Path:
    if getattr(sys, "frozen", False):
        frozen_path = Path(sys._MEIPASS) / "LICENSE"
        if frozen_path.is_file():
            return frozen_path
        dist_path = Path(sys.executable).resolve().parent / "LICENSE"
        if dist_path.is_file():
            return dist_path
    return project_root() / "LICENSE"


def stylesheet_path() -> Path:
    candidates = (
        Path(__file__).resolve().parent.parent / "ui" / "styles" / "ams2.qss",
        project_root() / "ams2_ai" / "ui" / "styles" / "ams2.qss",
    )
    if getattr(sys, "frozen", False):
        candidates = (
            Path(sys._MEIPASS) / "ams2_shared" / "ui" / "styles" / "ams2.qss",
            Path(sys._MEIPASS) / "ams2_ai" / "ui" / "styles" / "ams2.qss",
        ) + candidates
    for path in candidates:
        if path.is_file():
            return path
    return candidates[0]
