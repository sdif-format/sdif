"""Canonical SDIF serializer for the MVP AST."""

from __future__ import annotations

from collections.abc import Sequence
import hashlib
from sdif.core.ast import Directive, Document, Field, Narrative, ObjectBlock, Relation, Rule, Table
from sdif.parser import parse_text, Policy
from sdif.validation import Schema

_DIRECTIVE_ORDER = {
    "sdif": 0,
    "sdif.ai": 0,
    "alias": 1,
    "profile": 2,
    "vocab": 3,
    "base": 4,
    "namespace": 5,
    "include": 6,
}


def canonicalize(
    source: str | Document, schema: Schema | None = None, *, policy: Policy | None = None
) -> str:
    doc = parse_text(source, policy=policy) if isinstance(source, str) else source
    lines: list[str] = []
    for directive in sorted(
        doc.directives, key=lambda d: (_DIRECTIVE_ORDER.get(d.name, 100), d.name, d.args)
    ):
        lines.append(_emit_directive(directive))
    for statement in _canonical_statement_order(doc.statements, schema):
        _emit_statement(statement, lines, indent=0, schema=schema)
    return "\n".join(lines).rstrip() + "\n"


def _emit_directive(directive: Directive) -> str:
    if directive.name == "alias":
        return f"alias[{','.join(directive.args)}]"
    args = " ".join(directive.args)
    return f"@{directive.name}" + (f" {args}" if args else "")


def sdif_hash(
    source: str | Document, schema: Schema | None = None, *, policy: Policy | None = None
) -> str:
    return hashlib.sha256(
        canonicalize(source, schema=schema, policy=policy).encode("utf-8")
    ).hexdigest()




def _canonical_statement_order(statements: Sequence[object], schema: Schema | None) -> list[object]:
    order = {"kind": 0, "id": 1, "schema": 2, "authority": 3, "lifecycle": 4}
    fields = [s for s in statements if isinstance(s, Field)]
    relations = sorted(
        [s for s in statements if isinstance(s, Relation)],
        key=lambda r: (r.subject, r.predicate, r.object),
    )
    rules = sorted([s for s in statements if isinstance(s, Rule)], key=lambda r: r.source)
    others = [s for s in statements if not isinstance(s, Field | Relation | Rule)]
    fields.sort(key=lambda f: (order.get(f.key, 100), f.key))
    return [*fields, *_canonical_others(others, schema), *relations, *rules]


def _canonical_others(statements: Sequence[object], schema: Schema | None) -> list[object]:
    result: list[object] = []
    for statement in statements:
        if isinstance(statement, Table) and schema is not None:
            policy = schema.table_policies.get(statement.name)
            if policy is not None and not policy.ordered:
                if policy.primary_key is None:
                    raise ValueError(
                        f"unordered table `{statement.name}` requires primary_key "
                        "for strict canonicalization"
                    )
                if policy.primary_key not in statement.columns:
                    raise ValueError(
                        f"unordered table `{statement.name}` primary_key "
                        f"`{policy.primary_key}` is not present in table columns"
                    )
                idx = statement.columns.index(policy.primary_key)  # type: ignore[arg-type]
                result.append(
                    Table(
                        statement.name,
                        statement.columns,
                        sorted(statement.rows, key=lambda row: row[idx]),
                        statement.quoted_columns,
                    )
                )
                continue
        result.append(statement)
    return result


def _emit_statement(
    statement: object, lines: list[str], indent: int, schema: Schema | None
) -> None:
    prefix = " " * indent
    if isinstance(statement, Field):
        lines.append(
            f"{prefix}{statement.key} {_quote_if_needed(statement.value, force=getattr(statement, 'quoted', False))}"
        )
    elif isinstance(statement, ObjectBlock):
        lines.append(f"{prefix}{statement.key}:")
        for child in _canonical_statement_order(statement.statements, schema):
            _emit_statement(child, lines, indent + 2, schema)
    elif isinstance(statement, Table):
        lines.append(f"{prefix}{statement.name}[{','.join(statement.columns)}]:")
        for row in statement.rows:
            cells = [
                _quote_if_needed(cell, force=True) if index in statement.quoted_columns else cell
                for index, cell in enumerate(row)
            ]
            lines.append(f"{' ' * (indent + 2)}" + "\t".join(cells))
    elif isinstance(statement, Relation):
        if not _inside_current_block(lines, f"{prefix}rel:"):
            lines.append(f"{prefix}rel:")
        relation_object = _quote_if_needed(
            statement.object, force=getattr(statement, "object_quoted", False)
        )
        lines.append(
            f"{' ' * (indent + 2)}{statement.subject} {statement.predicate} {relation_object}"
        )
    elif isinstance(statement, Rule):
        if not _inside_current_block(lines, f"{prefix}rules:"):
            lines.append(f"{prefix}rules:")
        lines.append(f"{' ' * (indent + 2)}{statement.source}")
    elif isinstance(statement, Narrative):
        lines.append(f'{prefix}{statement.key} """')
        lines.extend(statement.text.split("\n"))
        lines.append('"""')
    else:  # pragma: no cover - defensive for future AST nodes
        raise TypeError(f"unsupported statement: {statement!r}")


def _quote_if_needed(value: str, *, force: bool = False) -> str:
    if force:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if value in {"null", "true", "false"}:
        return value
    safe = all(ch.isalnum() or ch in "_-./:[] ," for ch in value)
    if safe and value and " " not in value and "," not in value:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def _inside_current_block(lines: list[str], header: str) -> bool:
    for line in reversed(lines):
        if line == header:
            return True
        if not line.startswith("  "):
            return False
    return False
