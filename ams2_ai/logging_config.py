"""Centralized logging configuration."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_log_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    log_dir = base / "ams2-ai-creator" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_log_file_path() -> Path:
    return get_log_dir() / "ams2-ai-creator.log"


def setup_logging() -> logging.Logger:
    """Configure root logger with rotating file and optional console output."""
    logger = logging.getLogger("ams2_ai")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        get_log_file_path(),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_level = logging.DEBUG if os.environ.get("AMS2_AI_DEBUG") else logging.WARNING
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger
