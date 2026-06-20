"""Generate a Windows-compatible .ico from PNG artwork.

Pillow writes PNG-compressed ICO entries, which PyInstaller embeds correctly but
Windows Explorer often fails to display on executables. This script writes
classic 32-bit BMP/DIB icon images instead.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG_PATH = ROOT / "assets" / "icon" / "icon-artwork.png"
ICO_PATH = ROOT / "assets" / "icon" / "icon-artwork.ico"
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def _dib_from_rgba(width: int, height: int, rgba_bytes: bytes) -> bytes:
    """Build a 32-bit DIB payload (XOR bitmap + AND mask) for ICO/RT_ICON."""
    header = struct.pack(
        "<IIIHHIIIIII",
        40,
        width,
        height * 2,
        1,
        32,
        0,
        len(rgba_bytes) + (((width + 31) // 32) * 4 * height),
        0,
        0,
        0,
        0,
    )
    mask_row_bytes = ((width + 31) // 32) * 4
    and_mask = b"\x00" * (mask_row_bytes * height)
    return header + rgba_bytes + and_mask


def _image_payload(image) -> bytes:
    width, height = image.size
    rgba = image.convert("RGBA")
    row_bytes = width * 4
    rows = []
    for y in range(height - 1, -1, -1):
        row = bytearray()
        for x in range(width):
            r, g, b, a = rgba.getpixel((x, y))
            row.extend((b, g, r, a))
        rows.append(bytes(row))
    return _dib_from_rgba(width, height, b"".join(rows))


def build_icon() -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow is required: pip install pillow") from exc

    if not PNG_PATH.is_file():
        raise SystemExit(f"PNG artwork not found: {PNG_PATH}")

    source = Image.open(PNG_PATH).convert("RGBA")
    payloads: list[bytes] = []
    entries: list[tuple[int, int, bytes]] = []

    for size in ICO_SIZES:
        if source.size != size:
            image = source.resize(size, Image.Resampling.LANCZOS)
        else:
            image = source
        payload = _image_payload(image)
        payloads.append(payload)
        width, height = size
        entries.append((width, height, payload))

    offset = 6 + len(entries) * 16
    parts = [struct.pack("<HHH", 0, 1, len(entries))]

    for width, height, payload in entries:
        parts.append(
            struct.pack(
                "<BBBBHHII",
                0 if width == 256 else width,
                0 if height == 256 else height,
                0,
                0,
                1,
                32,
                len(payload),
                offset,
            )
        )
        offset += len(payload)

    for payload in payloads:
        parts.append(payload)

    ICO_PATH.write_bytes(b"".join(parts))
    print(f"Wrote {ICO_PATH} ({len(entries)} BMP sizes)")


def apply_exe_icon(exe_path: Path | None = None) -> None:
    """Apply the generated ICO to a built executable (post-PyInstaller step)."""
    exe = exe_path or (ROOT / "dist" / "AMS2-AI-Creator" / "AMS2-AI-Creator.exe")
    if not exe.is_file():
        raise SystemExit(f"Executable not found: {exe}")
    if not ICO_PATH.is_file():
        build_icon()

    from PyInstaller.utils.win32.icon import CopyIcons_FromIco

    CopyIcons_FromIco(str(exe), [str(ICO_PATH)])
    print(f"Applied icon to {exe}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--apply-exe":
        target = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        apply_exe_icon(target)
    else:
        build_icon()
