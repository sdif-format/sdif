#!/usr/bin/env python3
"""Validate portable SDIF conformance fixtures.

The suite is intentionally SDIF-first so parser/tooling implementations can use
one manifest without a JSON adapter.

This checker uses the current Python parser as a reference implementation for
source/canonical/hash fixture consistency.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


# -----------------------------------------------------------------------------
# Repository paths
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Resolve conformance root (fallback to local if running in legacy/monolithic tree)
if (ROOT / "conformance").is_dir():
    CONF_ROOT = ROOT
else:
    CONF_ROOT = Path(os.environ.get("SDIF_SPEC_REPO") or ROOT.parent / "sdif-spec").expanduser().resolve()


# -----------------------------------------------------------------------------
# SDIF imports
# -----------------------------------------------------------------------------

from sdif import ParseError, PolicyError, canonicalize, parse_text, sdif_hash  # noqa: E402
from sdif.core.ast import Document, Table  # noqa: E402


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

MANIFEST = CONF_ROOT / "conformance" / "manifest.sdif"

CASE_COLUMNS = [
    "id",
    "profile",
    "source",
    "canonical",
    "tree",
    "sha256",
]

INVALID_CASE_COLUMNS = ["id", "source", "expected_code"]

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


# -----------------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------------

def main() -> int:
    errors: list[str] = []

    manifest_doc = _load_manifest(errors)
    if manifest_doc is None:
        return _fail(errors)

    _validate_manifest_header(manifest_doc, errors)

    cases = manifest_doc.tables.get("cases")
    if cases is None:
        errors.append("manifest must include cases table")
        return _fail(errors)

    _validate_cases_table_shape(cases, errors)

    seen_ids: set[str] = set()
    _process_valid_cases(cases, seen_ids, errors)

    invalid_cases = manifest_doc.tables.get("invalid_cases")
    if invalid_cases is not None:
        _validate_invalid_cases_table_shape(invalid_cases, errors)
        _process_invalid_cases(invalid_cases, seen_ids, errors)

    if errors:
        return _fail(errors)

    print("conformance fixtures OK")
    return 0


# -----------------------------------------------------------------------------
# Manifest validation
# -----------------------------------------------------------------------------

def _load_manifest(errors: list[str]) -> Document | None:
    try:
        return parse_text(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append("missing conformance/manifest.sdif")
    except Exception as exc:  # pragma: no cover - exercised by CLI failure path
        errors.append(f"invalid conformance manifest: {exc}")

    return None


def _validate_manifest_header(manifest_doc: Document, errors: list[str]) -> None:
    kind = manifest_doc.fields.get("kind")

    _expect(
        kind is not None and kind.value == "ConformanceManifest",
        errors,
        "manifest kind must be ConformanceManifest",
    )


def _validate_cases_table_shape(cases: Table, errors: list[str]) -> None:
    _expect(
        cases.columns == CASE_COLUMNS,
        errors,
        "cases table columns must be id,profile,source,canonical,tree,sha256",
    )

    _expect(
        bool(cases.rows),
        errors,
        "cases table must contain at least one case",
    )


def _validate_invalid_cases_table_shape(invalid_cases: Table, errors: list[str]) -> None:
    _expect(
        invalid_cases.columns == INVALID_CASE_COLUMNS,
        errors,
        "invalid_cases table columns must be id,source,expected_code",
    )


# -----------------------------------------------------------------------------
# Case processing
# -----------------------------------------------------------------------------

def _process_valid_cases(
    cases: Table,
    seen_ids: set[str],
    errors: list[str],
) -> None:
    for row in cases.rows:
        if len(row) != len(CASE_COLUMNS):
            errors.append(f"case row has wrong arity: {row!r}")
            continue

        case = dict(zip(CASE_COLUMNS, row, strict=True))
        case_id = case["id"]

        _expect(case_id not in seen_ids, errors, f"duplicate case id: {case_id}")
        seen_ids.add(case_id)

        _check_case(case, errors)


def _process_invalid_cases(
    invalid_cases: Table,
    seen_ids: set[str],
    errors: list[str],
) -> None:
    for row in invalid_cases.rows:
        if len(row) != len(INVALID_CASE_COLUMNS):
            errors.append(f"invalid_cases row has wrong arity: {row!r}")
            continue

        invalid_case = dict(zip(INVALID_CASE_COLUMNS, row, strict=True))
        case_id = invalid_case["id"]

        _expect(case_id not in seen_ids, errors, f"duplicate case id: {case_id}")
        seen_ids.add(case_id)

        _check_invalid_case(invalid_case, errors)


# -----------------------------------------------------------------------------
# Case validation
# -----------------------------------------------------------------------------

def _check_case(case: dict[str, str], errors: list[str]) -> None:
    case_id = case["id"]

    if not SHA256_RE.match(case["sha256"]):
        errors.append(f"{case_id}: sha256 must be 64 lowercase hex characters")

    source_path = _repo_path(case["source"], errors, case_id, "source")
    canonical_path = _repo_path(case["canonical"], errors, case_id, "canonical")
    tree_path = _repo_path(case["tree"], errors, case_id, "tree")

    if source_path is None or canonical_path is None or tree_path is None:
        return

    source = _read(source_path, errors)
    expected_canonical = _read(canonical_path, errors)
    _read(tree_path, errors)

    if source is None or expected_canonical is None:
        return

    actual_canonical = canonicalize(source)

    _expect(
        actual_canonical == expected_canonical,
        errors,
        f"{case_id}: canonical.sdif does not match Python reference canonicalization",
    )

    _expect(
        sdif_hash(source) == case["sha256"],
        errors,
        f"{case_id}: manifest sha256 does not match canonical bytes",
    )

    _expect(
        _tables_with_multiple_columns_use_htab(source),
        errors,
        f"{case_id}: table rows must use literal HTAB",
    )

    _expect(
        _tables_with_multiple_columns_use_htab(expected_canonical),
        errors,
        f"{case_id}: canonical table rows must use literal HTAB",
    )


def _check_invalid_case(invalid_case: dict[str, str], errors: list[str]) -> None:
    case_id = invalid_case["id"]
    expected_code = invalid_case["expected_code"]

    source_path = _repo_path(invalid_case["source"], errors, case_id, "source")
    if source_path is None:
        return

    source = _read(source_path, errors)
    if source is None:
        return

    try:
        parse_text(source)
        errors.append(f"{case_id}: expected {expected_code} but document parsed without error")
    except (ParseError, PolicyError) as exc:
        actual_code = getattr(exc, "code", None)
        _expect(
            actual_code == expected_code,
            errors,
            f"{case_id}: expected {expected_code} but got {actual_code}",
        )
    except Exception as exc:
        errors.append(f"{case_id}: unexpected exception type {type(exc).__name__}: {exc}")


# -----------------------------------------------------------------------------
# File helpers
# -----------------------------------------------------------------------------

def _repo_path(raw: str, errors: list[str], case_id: str, role: str) -> Path | None:
    root = CONF_ROOT.resolve()
    path = (CONF_ROOT / raw).resolve()

    try:
        path.relative_to(root)
    except ValueError:
        errors.append(f"{case_id}: {role} path must stay inside repository: {raw}")
        return None

    if not path.is_file():
        errors.append(f"{case_id}: missing {role} file: {raw}")
        return None

    return path


def _read(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing required file: {path.relative_to(CONF_ROOT)}")
        return None


# -----------------------------------------------------------------------------
# SDIF syntax helpers
# -----------------------------------------------------------------------------

def _tables_with_multiple_columns_use_htab(source: str) -> bool:
    active_columns = 0

    for line in source.splitlines():
        stripped = line.strip()

        if not stripped:
            active_columns = 0
            continue

        if _is_table_header(line, stripped):
            header = stripped[stripped.index("[") + 1 : stripped.index("]")]
            active_columns = _count_columns(header)
            continue

        if active_columns > 1 and line.startswith("  "):
            if "\t" not in line:
                return False
            continue

        if not line.startswith("  "):
            active_columns = 0

    return True


def _is_table_header(line: str, stripped: str) -> bool:
    return not line.startswith(" ") and "[" in line and stripped.endswith(":")


def _count_columns(header: str) -> int:
    return len([column for column in header.split(",") if column.strip()])


# -----------------------------------------------------------------------------
# Error handling
# -----------------------------------------------------------------------------

def _expect(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _fail(errors: list[str]) -> int:
    for error in errors:
        print(f"conformance fixture error: {error}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
