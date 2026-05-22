"""Shared benchmark infrastructure: paths, env loading, directory management."""

from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

BENCHMARK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BENCHMARK_DIR.parent

# Make the SDIF library importable for all benchmark scripts that import this module.
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

CORPUS_DIR_NAME = "corpus"
DASHBOARD_FILE_NAME = "dashboard.html"


class Tee:
    def __init__(self, *streams: TextIO) -> None:
        self.streams = streams

    def write(self, data: str) -> int:
        for stream in self.streams:
            stream.write(data)
        return len(data)

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def replace_directory(source: Path, destination: Path) -> None:
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    elif destination.is_dir():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def benchmark_output_dir() -> Path:
    configured = os.environ.get("SDIF_BENCHMARK_OUTPUT_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return REPO_ROOT / "benchmarks"


def benchmark_golden_dir() -> Path:
    configured = os.environ.get("SDIF_BENCHMARK_GOLDEN_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return REPO_ROOT / "examples" / "golden"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path.absolute())


def benchmark_result_dir(track_name: str, base_dir: Path | None = None) -> Path:
    target_dir = base_dir or benchmark_output_dir()
    return target_dir / "results" / track_name


def create_benchmark_run_dir(track_name: str, base_dir: Path | None = None) -> Path:
    target_dir = base_dir or benchmark_output_dir()
    run_dir = target_dir / "tmp" / track_name
    if run_dir.is_symlink() or run_dir.is_file():
        run_dir.unlink()
    elif run_dir.is_dir():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    return run_dir


def publish_benchmark_result(
    run_dir: Path, track_name: str, base_dir: Path | None = None
) -> Path:
    final_dir = benchmark_result_dir(track_name, base_dir)
    replace_directory(run_dir, final_dir)
    return final_dir


def discover_documents(golden_dir: Path) -> list[str]:
    return [path.parent.name for path in sorted(golden_dir.glob("*/equivalent.json"))]


def verbose_warning(message: str) -> None:
    if os.environ.get("SDIF_BENCHMARK_VERBOSE") == "1":
        print(f"⚠️  {message}")


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def env_value(name: str, *, secret: bool = False) -> str:
    value = os.environ.get(name)
    if not value:
        return "_unset_"
    if secret:
        return "_set_"
    return f"`{markdown_escape(value)}`"


def parse_env_value(raw_value: str) -> str:
    value = raw_value.strip()
    if not value:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    if "#" in value:
        value = value.split("#", 1)[0].rstrip()
    return value


def load_env_file(path: Path) -> bool:
    if not path.exists():
        return False
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            verbose_warning(f"Ignoring invalid .env line {line_number}: missing '='")
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            verbose_warning(f"Ignoring invalid .env line {line_number}: empty key")
            continue
        override_env = os.environ.get("SDIF_ENV_OVERRIDE", "1") != "0"
        if key in os.environ and not override_env:
            continue
        os.environ[key] = parse_env_value(raw_value)
    return True
