"""Command-line interface for the SDIF MVP tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sdif import canonicalize, parse_text, sdif_hash
from sdif.ai import ai_view, sdif_from_ai
from sdif.json import document_to_json_data, json_data_to_sdif
from sdif.parser import ParseError
from sdif.core.ast import Directive, Document, Field, Narrative, ObjectBlock, Relation, Rule, Table
from sdif.validation import Diagnostic, Schema, SchemaError, diagnostics_to_json, validate_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sdif",
        description="SDIF (Semantic Data Interchange Format) tools for parsing, formatting, canonicalizing, validating, and projecting structured documents.",
    )
    sub = parser.add_subparsers(dest="command", required=True, title="subcommands", description="valid subcommands")

    parse = sub.add_parser(
        "parse",
        help="Parse an SDIF document and display counts of directives and statements",
        description="Parse an SDIF document and display counts of directives and statements.",
    )
    parse.add_argument("path", type=Path, help="Path to the SDIF file to parse")

    canon = sub.add_parser(
        "canon",
        help="Format an SDIF document to its canonical form and write to stdout",
        description="Format an SDIF document to its canonical form and write to stdout.",
    )
    canon.add_argument("path", type=Path, help="Path to the SDIF file to canonicalize")
    canon.add_argument(
        "--schema", type=Path, help="Optional schema file to apply schema-aware canonical policies"
    )

    hash_cmd = sub.add_parser(
        "hash",
        help="Generate a stable SHA-256 hash of the canonicalized SDIF document",
        description="Generate a stable SHA-256 hash of the canonicalized SDIF document.",
    )
    hash_cmd.add_argument("path", type=Path, help="Path to the SDIF file")
    hash_cmd.add_argument(
        "--schema", type=Path, help="Optional schema file to apply schema-aware canonical policies"
    )

    tokens = sub.add_parser(
        "tokens",
        help="Analyze and count tokens and bytes in an SDIF document",
        description="Analyze and count tokens and bytes in an SDIF document.",
    )
    tokens.add_argument("path", type=Path, help="Path to the SDIF file")

    to_json = sub.add_parser(
        "to-json",
        help="Convert an SDIF document into its corresponding JSON data representation",
        description="Convert an SDIF document into its corresponding JSON data representation.",
    )
    to_json.add_argument("path", type=Path, help="Path to the SDIF file")

    from_json = sub.add_parser(
        "from-json",
        help="Convert a JSON data representation back into an SDIF document",
        description="Convert a JSON data representation back into an SDIF document.",
    )
    from_json.add_argument("path", type=Path, help="Path to the JSON file")

    ai = sub.add_parser(
        "ai",
        help="Project an SDIF document into the token-dense .sdif.ai AI-friendly format",
        description="Project an SDIF document into the token-dense .sdif.ai AI-friendly format.",
    )
    ai.add_argument("path", type=Path, help="Path to the SDIF file")
    ai.add_argument(
        "--alias",
        action="append",
        default=[],
        metavar="FIELD=ALIAS",
        help="Optional alias to map a field/column name for the AI view (can be specified multiple times)"
    )

    from_ai = sub.add_parser(
        "from-ai",
        help="Convert a .sdif.ai projection back into canonical source SDIF",
        description="Convert a .sdif.ai projection back into canonical source SDIF.",
    )
    from_ai.add_argument("path", type=Path, help="Path to the SDIF AI file")

    validate = sub.add_parser(
        "validate",
        help="Validate an SDIF document against a given schema",
        description="Validate an SDIF document against a given schema.",
    )
    validate.add_argument("path", type=Path, help="Path to the SDIF file to validate")
    validate.add_argument("--schema", type=Path, required=True, help="Required schema file to validate against")
    validate.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output validation results as structured JSON instead of plain text"
    )

    inspect_cmd = sub.add_parser(
        "inspect",
        help="Inspect the internal AST of an SDIF document",
        description="Inspect the internal AST of an SDIF document.",
    )
    inspect_cmd.add_argument("path", type=Path, help="Path to the SDIF file")
    inspect_cmd.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output the parsed AST structure as JSON"
    )
    inspect_cmd.add_argument(
        "--schema",
        type=Path,
        help="Optional schema file to include validation diagnostics in the JSON output"
    )

    fmt = sub.add_parser(
        "fmt",
        help="Format an SDIF document in-place or check formatting compliance",
        description="Format an SDIF document in-place or check formatting compliance.",
    )
    fmt.add_argument("path", type=Path, help="Path to the SDIF file")
    fmt.add_argument(
        "--check",
        action="store_true",
        help="Check formatting compliance and exit with non-zero code on discrepancies instead of writing in-place"
    )
    fmt.add_argument(
        "--schema",
        type=Path,
        help="Optional schema file to apply schema-aware canonical policies"
    )

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
        tokenizer, token_count = _count_tokens(text, byte_count)
        print(f"bytes={byte_count} tokenizer={tokenizer} tokens={token_count}")
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
    if args.command == "from-ai":
        sys.stdout.write(sdif_from_ai(text))
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
            json.dump(
                {"valid": not diagnostics, "diagnostics": diagnostics_to_json(diagnostics)},
                sys.stdout,
                indent=2,
            )
            sys.stdout.write("\n")
        elif diagnostics:
            for diagnostic in diagnostics:
                print(
                    f"{diagnostic.severity}: {diagnostic.code} {diagnostic.path}: {diagnostic.message}"
                )
        else:
            print("valid")
        return 0 if not diagnostics else 1

    if args.command == "inspect":
        try:
            doc = parse_text(text)
            diagnostics = []
            if args.schema:
                schema = _load_schema(args.schema)
                if schema:
                    diagnostics = validate_document(doc, schema)
        except ParseError as exc:
            if args.json_output:
                err_result = {
                    "ast": None,
                    "diagnostics": diagnostics_to_json([_diagnostic_from_parse_error(exc)]),
                }
                json.dump(err_result, sys.stdout, indent=2)
                sys.stdout.write("\n")
                return 1
            else:
                sys.stderr.write(f"Parse error: {exc}\n")
                return 1

        if args.json_output:
            ast_result = {"ast": _ast_to_json(doc)}
            if args.schema:
                ast_result["diagnostics"] = diagnostics_to_json(diagnostics)
            json.dump(ast_result, sys.stdout, indent=2)
            sys.stdout.write("\n")
            return 0 if not diagnostics else 1
        else:
            print(f"directives={len(doc.directives)} statements={len(doc.statements)}")
            if diagnostics:
                for diagnostic in diagnostics:
                    print(
                        f"{diagnostic.severity}: {diagnostic.code} {diagnostic.path}: {diagnostic.message}"
                    )
                return 1
            return 0

    if args.command == "fmt":
        schema = _load_schema(args.schema)
        try:
            doc = parse_text(text)
            is_ai_projection = any(directive.name == "sdif.ai" for directive in doc.directives)
            canonical_text = sdif_from_ai(doc) if is_ai_projection else canonicalize(doc, schema=schema)
        except ParseError as exc:
            sys.stderr.write(f"Format error: parse failed: {exc}\n")
            return 1

        if args.check:
            if text != canonical_text:
                sys.stderr.write(f"Format check failed: {args.path} is not canonicalized\n")
                return 1
            return 0
        else:
            if text != canonical_text:
                args.path.write_text(canonical_text, encoding="utf-8")
                print(f"Reformatted {args.path}")
            return 0
    return 2


def _diagnostic_from_parse_error(exc: ParseError) -> Diagnostic:
    return Diagnostic(
        code=exc.code,
        severity="error",
        message=exc.message,
        path="$parse",
        line=exc.line,
        column=exc.column,
        hint=exc.hint,
    )


def _count_tokens(text: str, byte_count: int) -> tuple[str, int]:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return "estimate/4bytes", max(1, (byte_count + 3) // 4)

    encoding_name = "cl100k_base"
    encoder = tiktoken.get_encoding(encoding_name)
    return f"tiktoken/{encoding_name}", len(encoder.encode(text))


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


def _ast_to_json(node: object) -> object:
    if isinstance(node, list):
        return [_ast_to_json(item) for item in node]
    elif isinstance(node, dict):
        return {k: _ast_to_json(v) for k, v in node.items()}
    elif isinstance(node, Directive):
        return {
            "type": "directive",
            "name": node.name,
            "args": node.args,
        }
    elif isinstance(node, Field):
        return {
            "type": "field",
            "key": node.key,
            "value": node.value,
            "quoted": node.quoted,
        }
    elif isinstance(node, ObjectBlock):
        return {
            "type": "object",
            "key": node.key,
            "statements": [_ast_to_json(s) for s in node.statements],
        }
    elif isinstance(node, Table):
        return {
            "type": "table",
            "name": node.name,
            "columns": node.columns,
            "rows": node.rows,
        }
    elif isinstance(node, Relation):
        return {
            "type": "relation",
            "subject": node.subject,
            "predicate": node.predicate,
            "object": node.object,
            "object_quoted": node.object_quoted,
        }
    elif isinstance(node, Rule):
        return {
            "type": "rule",
            "source": node.source,
        }
    elif isinstance(node, Narrative):
        return {
            "type": "narrative",
            "key": node.key,
            "text": node.text,
        }
    elif isinstance(node, Document):
        return {
            "directives": [_ast_to_json(d) for d in node.directives],
            "statements": [_ast_to_json(s) for s in node.statements],
        }
    return node


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
