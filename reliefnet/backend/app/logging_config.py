# reliefnet/backend/app/logging_config.py
"""Logging configuration helper.
Initialises a root logger with console and optional file handler.
Uses the log level from Settings (e.g., INFO, DEBUG).
"""

import logging
import sys
import io
from pathlib import Path

def configure_logging(level: str = "INFO") -> None:
    logger = logging.getLogger()
    logger.setLevel(level.upper())
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler - use UTF-8 to avoid Windows cp1252 encoding errors
    if sys.platform == "win32":
        stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    else:
        stream = sys.stdout
    ch = logging.StreamHandler(stream)
    ch.setLevel(level.upper())
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional file handler - writes to project root logs directory
    log_dir = Path(__file__).resolve().parents[3] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / "reliefnet.log", encoding="utf-8")
    fh.setLevel(level.upper())
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.info("Logging configured - level %s", level.upper())
