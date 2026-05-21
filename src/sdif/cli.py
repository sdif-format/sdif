"""Command-line interface for the SDIF MVP tools."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sdif import canonicalize, parse_text, sdif_hash
from sdif.ai import ai_view
from sdif.json import document_to_json_data, json_data_to_sdif
from sdif.parser import ParseError
from sdif.validation import Diagnostic, Schema, SchemaError, diagnostics_to_json, validate_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdif", description="SDIF parser and canonicalization tools")
    sub = parser.add_subparsers(dest="command", required=True)

    parse = sub.add_parser("parse")
    parse.add_argument("path", type=Path)

    canon = sub.add_parser("canon")
    canon.add_argument("path", type=Path)
    canon.add_argument("--schema", type=Path, help="optional schema for schema-aware canonical policies")

    hash_cmd = sub.add_parser("hash")
    hash_cmd.add_argument("path", type=Path)
    hash_cmd.add_argument("--schema", type=Path, help="optional schema for schema-aware canonical policies")

    for name in ("tokens", "to-json", "from-json"):
        cmd = sub.add_parser(name)
        cmd.add_argument("path", type=Path)

    ai = sub.add_parser("ai")
    ai.add_argument("path", type=Path)
    ai.add_argument("--alias", action="append", default=[], metavar="FIELD=ALIAS")
    validate = sub.add_parser("validate")
    validate.add_argument("path", type=Path)
    validate.add_argument("--schema", type=Path, required=True)
    validate.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)
    text = args.path.read_text(encoding="utf-8")

    if args.command == "parse":
        doc = parse_text(text)
        print(f"directives={len(doc.directives)} statements={len(doc.statements)}")
        return 0
    if args.command == "canon":
        sys.stdout.write(canonicalize(text, schema=_load_schema(args.schema)))
        return 0
    if args.command == "hash":
        print(sdif_hash(text, schema=_load_schema(args.schema)))
        return 0
    if args.command == "tokens":
        byte_count = len(text.encode("utf-8"))
        # Lightweight dependency-free estimate for the base CLI; benchmark script can use tiktoken.
        estimate = max(1, (byte_count + 3) // 4)
        print(f"bytes={byte_count} tokens_estimate={estimate}")
        return 0
    if args.command == "to-json":
        json.dump(document_to_json_data(parse_text(text)), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if args.command == "from-json":
        sys.stdout.write(json_data_to_sdif(json.loads(text)))
        return 0
    if args.command == "ai":
        aliases = _parse_aliases(args.alias)
        sys.stdout.write(ai_view(text, aliases))
        return 0
    if args.command == "validate":
        schema = _load_schema(args.schema)
        if schema is None:  # pragma: no cover - argparse requires --schema for validate
            raise SystemExit("missing required --schema")
        try:
            doc = parse_text(text)
        except ParseError as exc:
            diagnostics = [_diagnostic_from_parse_error(exc)]
        else:
            diagnostics = validate_document(doc, schema)
        if args.json_output:
            json.dump({"valid": not diagnostics, "diagnostics": diagnostics_to_json(diagnostics)}, sys.stdout, indent=2)
            sys.stdout.write("\n")
        elif diagnostics:
            for diagnostic in diagnostics:
                print(f"{diagnostic.severity}: {diagnostic.code} {diagnostic.path}: {diagnostic.message}")
        else:
            print("valid")
        return 0 if not diagnostics else 1
    return 2


def _diagnostic_from_parse_error(exc: ParseError) -> Diagnostic:
    return Diagnostic(
        code=exc.code,
        severity="error",
        message=exc.message,
        path="$parse",
        line=exc.line,
        column=exc.column,
    )


def _load_schema(path: Path | None) -> Schema | None:
    if path is None:
        return None
    try:
        return Schema.from_document(parse_text(path.read_text(encoding="utf-8")))
    except SchemaError as exc:
        raise SystemExit(f"invalid --schema `{path}`: {exc}") from exc


def _parse_aliases(raw_aliases: list[str]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for raw in raw_aliases:
        if "=" not in raw:
            raise SystemExit(f"invalid alias `{raw}`; expected FIELD=ALIAS")
        field, alias = raw.split("=", 1)
        aliases[field] = alias
    return aliases


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
