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

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"
GOLDEN_DIR = EXAMPLES_DIR / "golden"
DEFAULT_SCHEMA = EXAMPLES_DIR / "schema.sdif"
EXPECTED_GOLDEN_FILES = {"equivalent.json", "source.sdif", "canonical.sdif", "canonical.sha256"}

sys.path.insert(0, str(ROOT / "src"))

from sdif import canonicalize, parse_text, sdif_hash  # noqa: E402
from sdif.validation import Schema  # noqa: E402


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


def _render_fixture(fixture_dir: Path) -> str:
    from sdif.json import json_data_to_sdif

    data = json.loads((fixture_dir / "equivalent.json").read_text(encoding="utf-8"))
    return json_data_to_sdif(data, include_header=True)


def _schema_for_fixture(fixture_dir: Path) -> Schema | None:
    if fixture_dir.name != "plan" or not DEFAULT_SCHEMA.exists():
        return None
    return Schema.from_document(parse_text(DEFAULT_SCHEMA.read_text(encoding="utf-8")))


def _stale_files(fixture_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in fixture_dir.iterdir()
        if path.is_file() and path.name not in EXPECTED_GOLDEN_FILES
    )


def generate(check: bool) -> int:
    _copy_top_level_json_examples()
    failures: list[str] = []

    for fixture_dir in _fixture_dirs():
        expected_sdif = _render_fixture(fixture_dir)
        source_sdif = fixture_dir / "source.sdif"
        schema = _schema_for_fixture(fixture_dir)
        expected_canonical = canonicalize(expected_sdif, schema=schema)
        expected_hash = sdif_hash(expected_sdif, schema=schema)
        canonical_sdif = fixture_dir / "canonical.sdif"
        canonical_sha256 = fixture_dir / "canonical.sha256"
        stale_files = _stale_files(fixture_dir)

        if check:
            if not source_sdif.exists():
                failures.append(f"missing {source_sdif.relative_to(ROOT)}")
            elif source_sdif.read_text(encoding="utf-8") != expected_sdif:
                failures.append(f"outdated {source_sdif.relative_to(ROOT)}")
            if not canonical_sdif.exists():
                failures.append(f"missing {canonical_sdif.relative_to(ROOT)}")
            elif canonical_sdif.read_text(encoding="utf-8") != expected_canonical:
                failures.append(f"outdated {canonical_sdif.relative_to(ROOT)}")
            if not canonical_sha256.exists():
                failures.append(f"missing {canonical_sha256.relative_to(ROOT)}")
            elif canonical_sha256.read_text(encoding="utf-8").strip() != expected_hash:
                failures.append(f"outdated {canonical_sha256.relative_to(ROOT)}")
            failures.extend(f"stale {path.relative_to(ROOT)}" for path in stale_files)
            continue

        source_sdif.write_text(expected_sdif, encoding="utf-8")
        canonical_sdif.write_text(expected_canonical, encoding="utf-8")
        canonical_sha256.write_text(expected_hash + "\n", encoding="utf-8")
        for path in stale_files:
            path.unlink()
        print(f"OK: {fixture_dir.relative_to(GOLDEN_DIR)}")

    if failures:
        print("Golden fixtures are not up to date:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SDIF golden fixtures from examples/golden/*/equivalent.json."
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


if __name__ == "__main__":
    raise SystemExit(main())
