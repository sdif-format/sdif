"""Command-line interface for the SDIF v1 tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sdif import Policy, PolicyError, canonicalize, parse_file, sdif_hash
from sdif.ai import ai_view, sdif_from_ai
from sdif.json import document_to_json_data, json_data_to_sdif
from sdif.parser import ParseError
from sdif.core.ast import Directive, Document, Field, Narrative, ObjectBlock, Relation, Rule, Table
from sdif.validation import Diagnostic, Schema, SchemaError, diagnostics_to_json, validate_document

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENCODING = "utf-8"
DIRECTIVE_AI = "sdif.ai"
REMOTE_SCHEMES = ("http://", "https://", "ftp://")
PARSE_LOCATION = "$parse"


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sdif",
        description="SDIF (Semantic Data Interchange Format) tools for parsing, formatting, canonicalizing, validating, and projecting structured documents.",
    )
    sub = parser.add_subparsers(
        dest="command", required=True, title="subcommands", description="valid subcommands"
    )

    policy_parser = argparse.ArgumentParser(add_help=False)
    policy_parser.add_argument(
        "--allow-include",
        action="store_true",
        dest="allow_includes",
        help="Allow parsing local includes (@include directive)",
    )
    policy_parser.add_argument(
        "--allow-include-path",
        type=Path,
        action="append",
        dest="allow_include_paths",
        default=[],
        help="Add a path directory/file to the allowlist for includes (can be specified multiple times)",
    )
    policy_parser.add_argument(
        "--allow-remote-include",
        action="store_true",
        dest="allow_remote_includes",
        help="Allow parsing remote/URL includes",
    )
    policy_parser.add_argument(
        "--allow-remote-schema",
        action="store_true",
        dest="allow_remote_schemas",
        help="Allow loading remote/URL schemas",
    )

    parse = sub.add_parser(
        "parse",
        parents=[policy_parser],
        help="Parse an SDIF document and display counts of directives and statements",
        description="Parse an SDIF document and display counts of directives and statements.",
    )
    parse.add_argument("path", type=Path, help="Path to the SDIF file to parse")

    canon = sub.add_parser(
        "canon",
        parents=[policy_parser],
        help="Format an SDIF document to its canonical form and write to stdout",
        description="Format an SDIF document to its canonical form and write to stdout.",
    )
    canon.add_argument("path", type=Path, help="Path to the SDIF file to canonicalize")
    canon.add_argument(
        "--schema", type=Path, help="Optional schema file to apply schema-aware canonical policies"
    )

    hash_cmd = sub.add_parser(
        "hash",
        parents=[policy_parser],
        help="Generate a stable SHA-256 hash of the canonicalized SDIF document",
        description="Generate a stable SHA-256 hash of the canonicalized SDIF document.",
    )
    hash_cmd.add_argument("path", type=Path, help="Path to the SDIF file")
    hash_cmd.add_argument(
        "--schema", type=Path, help="Optional schema file to apply schema-aware canonical policies"
    )

    tokens = sub.add_parser(
        "tokens",
        parents=[policy_parser],
        help="Analyze and count tokens and bytes in an SDIF document",
        description="Analyze and count tokens and bytes in an SDIF document.",
    )
    tokens.add_argument("path", type=Path, help="Path to the SDIF file")

    to_json = sub.add_parser(
        "to-json",
        parents=[policy_parser],
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
        parents=[policy_parser],
        help="Project an SDIF document into the token-dense .sdif.ai AI-friendly format",
        description="Project an SDIF document into the token-dense .sdif.ai AI-friendly format.",
    )
    ai.add_argument("path", type=Path, help="Path to the SDIF file")
    ai.add_argument(
        "--alias",
        action="append",
        default=[],
        metavar="FIELD=ALIAS",
        help="Optional alias to map a field/column name for the AI view (can be specified multiple times)",
    )

    from_ai = sub.add_parser(
        "from-ai",
        parents=[policy_parser],
        help="Convert a .sdif.ai projection back into canonical source SDIF",
        description="Convert a .sdif.ai projection back into canonical source SDIF.",
    )
    from_ai.add_argument("path", type=Path, help="Path to the SDIF AI file")

    validate = sub.add_parser(
        "validate",
        parents=[policy_parser],
        help="Validate an SDIF document against a given schema",
        description="Validate an SDIF document against a given schema.",
    )
    validate.add_argument("path", type=Path, help="Path to the SDIF file to validate")
    validate.add_argument(
        "--schema", type=Path, required=True, help="Required schema file to validate against"
    )
    validate.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output validation results as structured JSON instead of plain text",
    )

    inspect_cmd = sub.add_parser(
        "inspect",
        parents=[policy_parser],
        help="Inspect the internal AST of an SDIF document",
        description="Inspect the internal AST of an SDIF document.",
    )
    inspect_cmd.add_argument("path", type=Path, help="Path to the SDIF file")
    inspect_cmd.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output the parsed AST structure as JSON",
    )
    inspect_cmd.add_argument(
        "--schema",
        type=Path,
        help="Optional schema file to include validation diagnostics in the JSON output",
    )

    fmt = sub.add_parser(
        "fmt",
        parents=[policy_parser],
        help="Format an SDIF document in-place or check formatting compliance",
        description="Format an SDIF document in-place or check formatting compliance.",
    )
    fmt.add_argument("path", type=Path, help="Path to the SDIF file")
    fmt.add_argument(
        "--check",
        action="store_true",
        help="Check formatting compliance and exit with non-zero code on discrepancies instead of writing in-place",
    )
    fmt.add_argument(
        "--schema", type=Path, help="Optional schema file to apply schema-aware canonical policies"
    )

    return parser


# ---------------------------------------------------------------------------
# Per-subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_parse(args: argparse.Namespace, policy: Policy) -> int:
    doc = parse_file(args.path, policy=policy)
    print(f"directives={len(doc.directives)} statements={len(doc.statements)}")
    return 0


def _cmd_canon(args: argparse.Namespace, policy: Policy) -> int:
    doc = parse_file(args.path, policy=policy)
    sys.stdout.write(canonicalize(doc, schema=_load_schema(args.schema, policy=policy)))
    return 0


def _cmd_hash(args: argparse.Namespace, policy: Policy) -> int:
    doc = parse_file(args.path, policy=policy)
    print(sdif_hash(doc, schema=_load_schema(args.schema, policy=policy)))
    return 0


def _cmd_tokens(args: argparse.Namespace, policy: Policy) -> int:
    parse_file(args.path, policy=policy)
    text = args.path.read_text(encoding=ENCODING)
    byte_count = len(text.encode(ENCODING))
    tokenizer, token_count = _count_tokens(text, byte_count)
    print(f"bytes={byte_count} tokenizer={tokenizer} tokens={token_count}")
    return 0


def _cmd_to_json(args: argparse.Namespace, policy: Policy) -> int:
    doc = parse_file(args.path, policy=policy)
    json.dump(document_to_json_data(doc), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def _cmd_from_json(args: argparse.Namespace, policy: Policy) -> int:  # noqa: ARG001
    text = args.path.read_text(encoding=ENCODING)
    sys.stdout.write(json_data_to_sdif(json.loads(text)))
    return 0


def _cmd_ai(args: argparse.Namespace, policy: Policy) -> int:
    aliases = _parse_aliases(args.alias)
    doc = parse_file(args.path, policy=policy)
    sys.stdout.write(ai_view(doc, aliases))
    return 0


def _cmd_from_ai(args: argparse.Namespace, policy: Policy) -> int:
    doc = parse_file(args.path, policy=policy)
    sys.stdout.write(sdif_from_ai(doc, policy=policy))
    return 0


def _cmd_validate(args: argparse.Namespace, policy: Policy) -> int:
    schema = _load_schema(args.schema, policy=policy)
    if schema is None:  # pragma: no cover - argparse requires --schema for validate
        raise SystemExit("missing required --schema")
    try:
        doc = parse_file(args.path, policy=policy)
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
            print(_format_diagnostic(diagnostic))
    else:
        print("valid")
    return 0 if not diagnostics else 1


def _cmd_inspect(args: argparse.Namespace, policy: Policy) -> int:
    try:
        doc = parse_file(args.path, policy=policy)
        diagnostics: list[Diagnostic] = []
        if args.schema:
            schema = _load_schema(args.schema, policy=policy)
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
        ast_result: dict[str, object] = {"ast": _ast_to_json(doc)}
        if args.schema:
            ast_result["diagnostics"] = diagnostics_to_json(diagnostics)
        json.dump(ast_result, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if not diagnostics else 1
    else:
        print(f"directives={len(doc.directives)} statements={len(doc.statements)}")
        if diagnostics:
            for diagnostic in diagnostics:
                print(_format_diagnostic(diagnostic))
            return 1
        return 0


def _cmd_fmt(args: argparse.Namespace, policy: Policy) -> int:
    schema = _load_schema(args.schema, policy=policy)
    try:
        doc = parse_file(args.path, policy=policy)
        is_ai_projection = any(directive.name == DIRECTIVE_AI for directive in doc.directives)
        canonical_text = (
            sdif_from_ai(doc, policy=policy)
            if is_ai_projection
            else canonicalize(doc, schema=schema)
        )
    except ParseError as exc:
        sys.stderr.write(f"Format error: parse failed: {exc}\n")
        return 1

    if args.check:
        text = args.path.read_text(encoding=ENCODING)
        if text != canonical_text:
            sys.stderr.write(f"Format check failed: {args.path} is not canonicalized\n")
            return 1
        return 0
    else:
        text = args.path.read_text(encoding=ENCODING)
        if text != canonical_text:
            args.path.write_text(canonical_text, encoding=ENCODING)
            print(f"Reformatted {args.path}")
        return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    policy = Policy(
        allow_includes=getattr(args, "allow_includes", False),
        allowed_include_paths=frozenset(getattr(args, "allow_include_paths", [])),
        allow_remote_includes=getattr(args, "allow_remote_includes", False),
        allow_remote_schemas=getattr(args, "allow_remote_schemas", False),
    )

    _handlers = {
        "parse": _cmd_parse,
        "canon": _cmd_canon,
        "hash": _cmd_hash,
        "tokens": _cmd_tokens,
        "to-json": _cmd_to_json,
        "from-json": _cmd_from_json,
        "ai": _cmd_ai,
        "from-ai": _cmd_from_ai,
        "validate": _cmd_validate,
        "inspect": _cmd_inspect,
        "fmt": _cmd_fmt,
    }

    try:
        handler = _handlers.get(args.command)
        if handler is None:  # pragma: no cover
            return 0
        return handler(args, policy)

    except PolicyError as exc:
        if getattr(args, "json_output", False):
            json.dump(
                {
                    "policy_denial": {
                        "code": exc.code,
                        "message": exc.message,
                    }
                },
                sys.stdout,
                indent=2,
            )
            sys.stdout.write("\n")
        else:
            sys.stderr.write(f"Policy denial: {exc.code}: {exc.message}\n")
        return 2
    except ParseError as exc:
        if getattr(args, "json_output", False):
            json.dump(
                {
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                        "line": exc.line,
                        "column": exc.column,
                    }
                },
                sys.stdout,
                indent=2,
            )
            sys.stdout.write("\n")
        else:
            sys.stderr.write(f"Parse error: {exc}\n")
        return 1
    except ValueError as exc:
        if getattr(args, "json_output", False):
            json.dump(
                {
                    "error": {
                        "code": "SDIF_CANONICALIZATION_ERROR",
                        "message": str(exc),
                    }
                },
                sys.stdout,
                indent=2,
            )
            sys.stdout.write("\n")
        else:
            sys.stderr.write(f"Canonicalization error: {exc}\n")
        return 1


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _format_diagnostic(diagnostic: Diagnostic) -> str:
    return f"{diagnostic.severity}: {diagnostic.code} {diagnostic.path}: {diagnostic.message}"


def _diagnostic_from_parse_error(exc: ParseError) -> Diagnostic:
    return Diagnostic(
        code=exc.code,
        severity="error",
        message=exc.message,
        path=PARSE_LOCATION,
        line=exc.line,
        column=exc.column,
        hint=exc.hint,
    )


def _count_tokens(text: str, byte_count: int) -> tuple[str, int]:
    try:
        import tiktoken  # type: ignore[import-not-found]  # optional dependency; lazy import avoids hard requirement
    except ImportError:
        return "estimate/4bytes", max(1, (byte_count + 3) // 4)

    encoding_name = "cl100k_base"
    encoder = tiktoken.get_encoding(encoding_name)
    return f"tiktoken/{encoding_name}", len(encoder.encode(text))


def _load_schema(path: Path | None, policy: Policy | None = None) -> Schema | None:
    if path is None:
        return None
    policy = policy or Policy()
    path_str = str(path)
    is_remote = path_str.startswith(REMOTE_SCHEMES)
    if is_remote:
        if not policy.allow_remote_schemas:
            raise PolicyError(
                "SDIF_POLICY_REMOTE_SCHEMA",
                f"Remote schema loading of {path_str} is disabled by policy",
            )
        raise PolicyError(
            "SDIF_POLICY_REMOTE_SCHEMA",
            f"Remote schemas not supported: {path_str}",
        )
    try:
        return Schema.from_document(parse_file(path, policy=policy))
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
