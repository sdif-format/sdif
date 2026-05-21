#!/usr/bin/env python3
"""Validate portable SDIF conformance fixtures.

The suite is intentionally SDIF-first so parser/tooling implementations can use
one manifest without a JSON adapter. This checker uses the current Python parser
as a reference implementation and also checks that expected Tree-sitter node
names stay aligned with the local grammar scaffold.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sdif import canonicalize, parse_text, sdif_hash  # noqa: E402

MANIFEST = ROOT / "conformance" / "manifest.sdif"
GRAMMAR = ROOT / "tree-sitter-sdif" / "grammar.js"
CASE_COLUMNS = ["id", "profile", "source", "canonical", "tree", "sha256"]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def main() -> int:
    errors: list[str] = []

    try:
        manifest_doc = parse_text(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _fail(["missing conformance/manifest.sdif"])
    except Exception as exc:  # pragma: no cover - exercised by CLI failure path
        return _fail([f"invalid conformance manifest: {exc}"])

    _expect(
        manifest_doc.fields.get("kind") is not None
        and manifest_doc.fields["kind"].value == "ConformanceManifest",
        errors,
        "manifest kind must be ConformanceManifest",
    )
    cases = manifest_doc.tables.get("cases")
    if cases is None:
        errors.append("manifest must include cases table")
        return _fail(errors)
    _expect(cases.columns == CASE_COLUMNS, errors, "cases table columns must be id,profile,source,canonical,tree,sha256")
    _expect(bool(cases.rows), errors, "cases table must contain at least one case")

    grammar_nodes = _grammar_rule_names(_read(GRAMMAR, errors))
    seen_ids: set[str] = set()
    for row in cases.rows:
        if len(row) != len(CASE_COLUMNS):
            errors.append(f"case row has wrong arity: {row!r}")
            continue
        case = dict(zip(CASE_COLUMNS, row, strict=True))
        case_id = case["id"]
        _expect(case_id not in seen_ids, errors, f"duplicate case id: {case_id}")
        seen_ids.add(case_id)
        _check_case(case, grammar_nodes, errors)

    if errors:
        return _fail(errors)

    print("conformance fixtures OK")
    return 0


def _check_case(case: dict[str, str], grammar_nodes: set[str], errors: list[str]) -> None:
    case_id = case["id"]
    source_path = _repo_path(case["source"], errors, case_id, "source")
    canonical_path = _repo_path(case["canonical"], errors, case_id, "canonical")
    tree_path = _repo_path(case["tree"], errors, case_id, "tree")

    if not SHA256_RE.match(case["sha256"]):
        errors.append(f"{case_id}: sha256 must be 64 lowercase hex characters")

    if source_path is None or canonical_path is None or tree_path is None:
        return

    source = _read(source_path, errors)
    expected_canonical = _read(canonical_path, errors)
    expected_tree = _read(tree_path, errors)
    if errors:
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
    _expect(_tables_with_multiple_columns_use_htab(source), errors, f"{case_id}: table rows must use literal HTAB")
    _expect(
        _tables_with_multiple_columns_use_htab(expected_canonical),
        errors,
        f"{case_id}: canonical table rows must use literal HTAB",
    )

    expected_nodes = _tree_node_names(expected_tree)
    missing_nodes = sorted(expected_nodes - grammar_nodes)
    _expect(
        not missing_nodes,
        errors,
        f"{case_id}: expected.tree references undeclared grammar nodes: {', '.join(missing_nodes)}",
    )


def _repo_path(raw: str, errors: list[str], case_id: str, role: str) -> Path | None:
    path = ROOT / raw
    try:
        path.relative_to(ROOT)
    except ValueError:
        errors.append(f"{case_id}: {role} path must stay inside repository: {raw}")
        return None
    if not path.is_file():
        errors.append(f"{case_id}: missing {role} file: {raw}")
        return None
    return path


def _read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
    return ""


def _grammar_rule_names(grammar: str) -> set[str]:
    return set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[$_]\s*=>", grammar, re.MULTILINE))


def _tree_node_names(tree: str) -> set[str]:
    return set(re.findall(r"\(([A-Za-z_][A-Za-z0-9_]*)", tree))


def _tables_with_multiple_columns_use_htab(source: str) -> bool:
    active_columns = 0
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped:
            active_columns = 0
            continue
        if not line.startswith(" ") and "[" in line and stripped.endswith(":"):
            header = stripped[stripped.index("[") + 1 : stripped.index("]")]
            active_columns = len([column for column in header.split(",") if column.strip()])
            continue
        if active_columns > 1 and line.startswith("  "):
            if "\t" not in line:
                return False
            continue
        if not line.startswith("  "):
            active_columns = 0
    return True


def _expect(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _fail(errors: list[str]) -> int:
    for error in errors:
        print(f"conformance fixture error: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
