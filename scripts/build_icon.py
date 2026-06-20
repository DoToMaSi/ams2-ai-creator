"""Generate a multi-resolution Windows .ico from the PNG artwork."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG_PATH = ROOT / "assets" / "icon" / "icon-artwork.png"
ICO_PATH = ROOT / "assets" / "icon" / "icon-artwork.ico"
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def build_icon() -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow is required: pip install pillow") from exc

    if not PNG_PATH.is_file():
        raise SystemExit(f"PNG artwork not found: {PNG_PATH}")

    source = Image.open(PNG_PATH).convert("RGBA")
    source.save(ICO_PATH, format="ICO", sizes=ICO_SIZES)
    print(f"Wrote {ICO_PATH} ({len(ICO_SIZES)} sizes)")


if __name__ == "__main__":
    build_icon()
    sys.exit(0)
