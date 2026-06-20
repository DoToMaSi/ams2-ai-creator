"""Structured metadata stored in the XML header comment."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HeaderMeta:
    name: str = ""
    vehicle_class: str = ""
    custom_class_name: str = ""
    body: str = ""


def parse_header_comment(comment: str) -> HeaderMeta:
    """Parse structured or legacy header comments."""
    stripped = comment.strip()
    if not stripped:
        return HeaderMeta()

    lines = stripped.splitlines()
    if lines[0].startswith("Name:"):
        meta = HeaderMeta()
        body_start = len(lines)
        for index, line in enumerate(lines):
            if line.startswith("Name:"):
                meta.name = line[5:].strip()
            elif line.startswith("Class:"):
                meta.vehicle_class = line[6:].strip()
            elif line.startswith("Custom Name:"):
                meta.custom_class_name = line[12:].strip()
            elif not line.strip() and index < 4:
                continue
            else:
                body_start = index
                break
        meta.body = "\n".join(lines[body_start:]).strip()
        return meta

    return HeaderMeta(name=lines[0].strip(), body="\n".join(lines[1:]).strip())


def build_header_comment(meta: HeaderMeta) -> str:
    """Serialize document metadata into a header comment body."""
    lines = [
        f"Name: {meta.name.strip()}",
        f"Class: {meta.vehicle_class.strip()}",
        f"Custom Name: {meta.custom_class_name.strip()}",
    ]
    if meta.body.strip():
        lines.extend(["", meta.body.strip()])
    return "\n".join(lines)
