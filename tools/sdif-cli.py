#!/usr/bin/env python3
"""Development wrapper for `python -m sdif.cli` without requiring installation."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sdif.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
