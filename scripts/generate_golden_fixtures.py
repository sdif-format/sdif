#!/usr/bin/env python3
"""Generate checked-in SDIF golden fixtures from canonical JSON examples.

Golden fixture directories treat ``equivalent.json`` as the semantic source.
This script derives ``source.sdif`` plus canonical/hash fixtures from that JSON
and removes unrelated derived formats so the fixture set stays unambiguous.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# -----------------------------------------------------------------------------
# Repository paths
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

EXAMPLES_DIR = ROOT / "examples"
GOLDEN_DIR = EXAMPLES_DIR / "golden"
DEFAULT_SCHEMA = EXAMPLES_DIR / "schema.sdif"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


# -----------------------------------------------------------------------------
# SDIF imports
# -----------------------------------------------------------------------------

from sdif import canonicalize, parse_text, sdif_hash  # noqa: E402
from sdif.json import json_data_to_sdif  # noqa: E402
from sdif.validation import Schema  # noqa: E402


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

EXPECTED_GOLDEN_FILES = {
    "equivalent.json",
    "source.sdif",
    "canonical.sdif",
    "canonical.sha256",
}


# -----------------------------------------------------------------------------
# Public entry points
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SDIF golden fixtures from examples/golden/*/equivalent.json.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate fixtures without writing files.",
    )

    args = parser.parse_args()

    if not GOLDEN_DIR.exists():
        print(f"Missing golden fixture directory: {GOLDEN_DIR.relative_to(ROOT)}")
        return 1

    return generate(check=args.check)


def generate(check: bool) -> int:
    if not check:
        _copy_top_level_json_examples()

    failures: list[str] = []

    for fixture_dir in _fixture_dirs():
        fixture = _build_expected_fixture(fixture_dir)
        stale_files = _stale_files(fixture_dir)

        if check:
            _check_fixture(fixture, stale_files, failures)
            continue

        _write_fixture(fixture, stale_files)
        print(f"OK: {fixture_dir.relative_to(GOLDEN_DIR)}")

    if failures:
        _print_failures(failures)
        return 1

    return 0


# -----------------------------------------------------------------------------
# Fixture model
# -----------------------------------------------------------------------------

class ExpectedFixture:
    def __init__(
        self,
        fixture_dir: Path,
        source: str,
        canonical: str,
        sha256: str,
    ) -> None:
        self.fixture_dir = fixture_dir
        self.source = source
        self.canonical = canonical
        self.sha256 = sha256

    @property
    def source_path(self) -> Path:
        return self.fixture_dir / "source.sdif"

    @property
    def canonical_path(self) -> Path:
        return self.fixture_dir / "canonical.sdif"

    @property
    def sha256_path(self) -> Path:
        return self.fixture_dir / "canonical.sha256"


# -----------------------------------------------------------------------------
# Fixture discovery and generation
# -----------------------------------------------------------------------------

def _fixture_dirs() -> list[Path]:
    return sorted(path.parent for path in GOLDEN_DIR.glob("*/equivalent.json"))


def _copy_top_level_json_examples() -> None:
    """Seed fixture directories from examples/*.json when those examples exist."""
    for json_path in sorted(EXAMPLES_DIR.glob("*.json")):
        fixture_dir = GOLDEN_DIR / json_path.stem
        fixture_dir.mkdir(parents=True, exist_ok=True)

        (fixture_dir / "equivalent.json").write_text(
            json_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )


def _build_expected_fixture(fixture_dir: Path) -> ExpectedFixture:
    source = _render_source_sdif(fixture_dir)
    schema = _schema_for_fixture(fixture_dir)

    canonical = canonicalize(source, schema=schema)
    sha256 = sdif_hash(source, schema=schema)

    return ExpectedFixture(
        fixture_dir=fixture_dir,
        source=source,
        canonical=canonical,
        sha256=sha256,
    )


def _render_source_sdif(fixture_dir: Path) -> str:
    equivalent_json = fixture_dir / "equivalent.json"
    data = json.loads(equivalent_json.read_text(encoding="utf-8"))

    return json_data_to_sdif(data, include_header=True)


def _schema_for_fixture(fixture_dir: Path) -> Schema | None:
    if fixture_dir.name != "plan":
        return None

    if not DEFAULT_SCHEMA.exists():
        return None

    schema_doc = parse_text(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    return Schema.from_document(schema_doc)


def _stale_files(fixture_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in fixture_dir.iterdir()
        if path.is_file() and path.name not in EXPECTED_GOLDEN_FILES
    )


# -----------------------------------------------------------------------------
# Check mode
# -----------------------------------------------------------------------------

def _check_fixture(
    fixture: ExpectedFixture,
    stale_files: list[Path],
    failures: list[str],
) -> None:
    _check_file(
        path=fixture.source_path,
        expected=fixture.source,
        failures=failures,
    )

    _check_file(
        path=fixture.canonical_path,
        expected=fixture.canonical,
        failures=failures,
    )

    _check_file(
        path=fixture.sha256_path,
        expected=f"{fixture.sha256}\n",
        failures=failures,
        strip_actual=True,
        strip_expected=True,
    )

    failures.extend(f"stale {path.relative_to(ROOT)}" for path in stale_files)


def _check_file(
    path: Path,
    expected: str,
    failures: list[str],
    *,
    strip_actual: bool = False,
    strip_expected: bool = False,
) -> None:
    if not path.exists():
        failures.append(f"missing {path.relative_to(ROOT)}")
        return

    actual = path.read_text(encoding="utf-8")

    if strip_actual:
        actual = actual.strip()

    if strip_expected:
        expected = expected.strip()

    if actual != expected:
        failures.append(f"outdated {path.relative_to(ROOT)}")


# -----------------------------------------------------------------------------
# Write mode
# -----------------------------------------------------------------------------

def _write_fixture(fixture: ExpectedFixture, stale_files: list[Path]) -> None:
    fixture.source_path.write_text(fixture.source, encoding="utf-8")
    fixture.canonical_path.write_text(fixture.canonical, encoding="utf-8")
    fixture.sha256_path.write_text(f"{fixture.sha256}\n", encoding="utf-8")

    for path in stale_files:
        path.unlink()


# -----------------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------------

def _print_failures(failures: list[str]) -> None:
    print("Golden fixtures are not up to date:", file=sys.stderr)

    for failure in failures:
        print(f"- {failure}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
