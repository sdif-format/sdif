"""Minimal SDIF schema validation."""

from .validator import (
    Diagnostic,
    RelationPolicy,
    Schema,
    SchemaError,
    TablePolicy,
    diagnostics_to_json,
    validate_document,
)

__all__ = [
    "Diagnostic",
    "RelationPolicy",
    "Schema",
    "SchemaError",
    "TablePolicy",
    "diagnostics_to_json",
    "validate_document",
]
