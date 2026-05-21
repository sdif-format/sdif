#!/usr/bin/env python3
"""Executable semantic-quality smoke checks for the SDIF example set.

This script keeps semantic-quality evaluation separate from token-density
benchmarks. It verifies that the documented axes in docs/semantic-quality.md
are backed by current parser, JSON conversion, validation, AI projection, and
canonicalization behavior.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sdif import canonicalize, parse_text, sdif_hash  # noqa: E402
from sdif.ai import ai_view  # noqa: E402
from sdif.json import document_to_json_data, json_data_to_sdif  # noqa: E402
from sdif.validation import Schema, validate_document  # noqa: E402

PLAN = ROOT / "examples" / "plan.sdif"
SCHEMA = ROOT / "examples" / "schema.sdif"


def main() -> int:
    errors: list[str] = []
    plan_text = _read(PLAN, errors)
    schema_text = _read(SCHEMA, errors)
    if errors:
        return _fail(errors)

    doc = parse_text(plan_text)
    schema = Schema.from_document(parse_text(schema_text))

    _check_relational_expressivity(doc, errors)
    _check_round_trip_fidelity(doc, errors)
    _check_schema_validation(doc, schema, errors)
    _check_sdif_ai_semantic_retention(plan_text, errors)
    _check_canonicalization(plan_text, errors)

    if errors:
        return _fail(errors)

    for axis in (
        "relational expressivity",
        "round-trip fidelity",
        "schema validation",
        "SDIF AI semantic retention",
        "canonicalization",
    ):
        print(f"pass: {axis}")
    print("semantic quality checks OK")
    return 0


def _check_relational_expressivity(doc: object, errors: list[str]) -> None:
    relations = getattr(doc, "relations", [])
    _expect(bool(relations), errors, "relational expressivity: examples/plan.sdif must contain rel rows")
    _expect(
        any(
            relation.subject == "R3" and relation.predicate == "depends_on" and relation.object == "R2"
            for relation in relations
        ),
        errors,
        "relational expressivity: expected R3 depends_on R2 edge",
    )
    _expect(
        any(relation.predicate == "validated_by" for relation in relations),
        errors,
        "relational expressivity: expected validated_by edge",
    )


def _check_round_trip_fidelity(doc: object, errors: list[str]) -> None:
    data = document_to_json_data(doc)  # type: ignore[arg-type]
    recreated = parse_text(json_data_to_sdif(data))
    round_trip = document_to_json_data(recreated)
    _expect(round_trip == data, errors, "round-trip fidelity: SDIF -> JSON data -> SDIF must preserve JSON data")
    _expect("milestones" in data, errors, "round-trip fidelity: milestones table must survive conversion")
    _expect("rel" in data, errors, "round-trip fidelity: relation block must survive conversion")


def _check_schema_validation(doc: object, schema: Schema, errors: list[str]) -> None:
    diagnostics = validate_document(doc, schema)  # type: ignore[arg-type]
    _expect(not diagnostics, errors, f"schema validation: expected valid plan, got {len(diagnostics)} diagnostics")
    _expect("status" in schema.field_types, errors, "schema validation: schema must type the status field")
    _expect("milestones" in schema.table_column_types, errors, "schema validation: schema must type milestones")
    _expect("depends_on" in schema.relation_policies, errors, "schema validation: schema must type depends_on relations")


def _check_sdif_ai_semantic_retention(plan_text: str, errors: list[str]) -> None:
    ai = ai_view(plan_text, {"kind": "k", "status": "st"})
    ai_doc = parse_text(ai)
    _expect(ai.startswith("@sdif.ai 0.1"), errors, "SDIF AI semantic retention: projection must use sdif.ai directive")
    _expect("alias[k=kind,st=status]" in ai, errors, "SDIF AI semantic retention: projection must include alias header")
    _expect("milestones[id,st,gate,evidence]:" in ai, errors, "SDIF AI semantic retention: table aliases must retain shape")
    _expect("\nR1\tdone\tvalidate-syntax" in ai, errors, "SDIF AI semantic retention: top-level rows must be compact")
    _expect(bool(ai_doc.relations), errors, "SDIF AI semantic retention: relations must remain parseable")
    _expect(bool(ai_doc.rules), errors, "SDIF AI semantic retention: rules must remain parseable")


def _check_canonicalization(plan_text: str, errors: list[str]) -> None:
    first = canonicalize(plan_text)
    second = canonicalize(first)
    _expect(first == second, errors, "canonicalization: canonical bytes must be idempotent")
    _expect(
        sdif_hash(plan_text) == hashlib.sha256(first.encode("utf-8")).hexdigest(),
        errors,
        "canonicalization: hash must match canonical bytes",
    )


def _read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return ""


def _expect(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _fail(errors: list[str]) -> int:
    for error in errors:
        print(f"semantic quality error: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
