"""Generate compact `.sdif.ai` projections with explicit reversible aliases."""

from __future__ import annotations

from sdif import parse_text
from sdif.canonical import canonicalize
from typing import Sequence

from sdif.core.ast import (
    Directive,
    Document,
    Field,
    Narrative,
    ObjectBlock,
    Relation,
    Rule,
    Statement,
    Table,
)


def ai_view(source: str | Document, aliases: dict[str, str], *, include_header: bool = True) -> str:
    doc = parse_text(source) if isinstance(source, str) else source
    inverse = {canonical: alias for canonical, alias in aliases.items()}
    lines = ["@sdif.ai 0.1"] if include_header else []
    if include_header and aliases:
        entries = ",".join(
            f"{alias}={canonical}"
            for canonical, alias in sorted(aliases.items(), key=lambda item: item[1])
        )
        lines.append(f"alias[{entries}]")
    _emit_statements(doc.statements, lines, inverse, 0)
    return "\n".join(lines).rstrip() + "\n"


def sdif_from_ai(source: str | Document) -> str:
    """Convert a `.sdif.ai` projection back to canonical source SDIF.

    The reverse contract is canonical/semantic, not byte-for-byte source
    recovery. This function does not preserve source trivia, comments, original
    ordering, or byte-for-byte source formatting. Perfect canonical isomorphism
    must be proven by comparing canonical hashes of the original source and
    this restored source.
    """

    doc = parse_text(source) if isinstance(source, str) else source
    aliases = _alias_to_canonical(doc)
    directives = _source_directives(doc)
    statements: list[Statement] = [
        _expand_statement(statement, aliases) for statement in doc.statements
    ]
    return canonicalize(Document(directives=directives, statements=statements))


def _name(name: str, inverse: dict[str, str]) -> str:
    return inverse.get(name, name)


def _expanded_name(name: str, aliases: dict[str, str]) -> str:
    return aliases.get(name, name)


def _alias_to_canonical(doc: Document) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for directive in doc.directives:
        if directive.name != "alias":
            continue
        for entry in directive.args:
            alias, canonical = entry.split("=", 1)
            aliases[alias] = canonical
    return aliases


def _source_directives(doc: Document) -> list[Directive]:
    directives: list[Directive] = []
    saw_version = False
    for directive in doc.directives:
        if directive.name == "alias":
            continue
        if directive.name == "sdif.ai":
            directives.append(Directive("sdif", directive.args))
            saw_version = True
            continue
        directives.append(directive)
        if directive.name == "sdif":
            saw_version = True
    if not saw_version:
        directives.insert(0, Directive("sdif", ["0.1"]))
    return directives


def _expand_statement(statement: object, aliases: dict[str, str]) -> Statement:
    if isinstance(statement, Field):
        return Field(_expanded_name(statement.key, aliases), statement.value, statement.quoted)
    if isinstance(statement, ObjectBlock):
        return ObjectBlock(
            _expanded_name(statement.key, aliases),
            [_expand_statement(child, aliases) for child in statement.statements],
        )
    if isinstance(statement, Table):
        columns: list[str] = []
        quoted_columns: set[int] = set(statement.quoted_columns)
        for index, column in enumerate(statement.columns):
            if column.endswith("$"):
                quoted_columns.add(index)
                column = column[:-1]
            columns.append(_expanded_name(column, aliases))
        return Table(
            _expanded_name(statement.name, aliases),
            columns,
            statement.rows,
            frozenset(quoted_columns),
        )
    if isinstance(statement, Relation):
        return Relation(
            statement.subject,
            _expanded_name(statement.predicate, aliases),
            statement.object,
            statement.object_quoted,
        )
    if isinstance(statement, Rule):
        return statement
    if isinstance(statement, Narrative):
        return Narrative(_expanded_name(statement.key, aliases), statement.text)
    raise TypeError(f"unsupported statement: {statement!r}")


def _is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == value[-1] == '"'


def _unquote(value: str) -> str:
    return bytes(value[1:-1], "utf-8").decode("unicode_escape")


def _ai_columns_and_rows(
    table: Table, inverse: dict[str, str]
) -> tuple[list[str], list[list[str]]]:
    string_columns = {
        index for row in table.rows for index, cell in enumerate(row) if _is_quoted(cell)
    }
    columns = [
        f"{_name(column, inverse)}$" if index in string_columns else _name(column, inverse)
        for index, column in enumerate(table.columns)
    ]
    rows = [
        [
            _unquote(cell) if index in string_columns and _is_quoted(cell) else cell
            for index, cell in enumerate(row)
        ]
        for row in table.rows
    ]
    return columns, rows


def _emit(statement: object, lines: list[str], inverse: dict[str, str], indent: int) -> None:
    prefix = " " * indent
    if isinstance(statement, Field):
        lines.append(f"{prefix}{_name(statement.key, inverse)} {statement.value}")
    elif isinstance(statement, ObjectBlock):
        lines.append(f"{prefix}{_name(statement.key, inverse)}:")
        for child in statement.statements:
            _emit(child, lines, inverse, indent + 2)
    elif isinstance(statement, Table):
        columns, rows = _ai_columns_and_rows(statement, inverse)
        lines.append(f"{prefix}{_name(statement.name, inverse)}[{','.join(columns)}]:")
        row_prefix = "" if indent == 0 else " " * indent
        for row in rows:
            lines.append(row_prefix + "\t".join(row))
    elif isinstance(statement, Relation):
        if not lines or lines[-1] != f"{prefix}rel:":
            lines.append(f"{prefix}rel:")
        lines.append(
            f"{' ' * (indent + 2)}{statement.subject} {statement.predicate} {statement.object}"
        )
    elif isinstance(statement, Rule):
        if not lines or lines[-1] != f"{prefix}rules:":
            lines.append(f"{prefix}rules:")
        lines.append(f"{' ' * (indent + 2)}{statement.source}")
    elif isinstance(statement, Narrative):
        lines.append(f'{prefix}{_name(statement.key, inverse)} """')
        lines.extend(statement.text.split("\n"))
        lines.append('"""')


def _emit_statements(
    statements: Sequence[object], lines: list[str], inverse: dict[str, str], indent: int
) -> None:
    relation_groups: dict[str, list[Relation]] = {}
    relation_subjects: list[str] = []
    for statement in statements:
        if isinstance(statement, Relation):
            if statement.subject not in relation_groups:
                relation_subjects.append(statement.subject)
                relation_groups[statement.subject] = []
            relation_groups[statement.subject].append(statement)
            continue
        _emit(statement, lines, inverse, indent)
    for subject in relation_subjects:
        _emit_relation_group(subject, relation_groups[subject], lines, inverse, indent)


def _emit_relation_group(
    subject: str,
    relations: list[Relation],
    lines: list[str],
    inverse: dict[str, str],
    indent: int,
) -> None:
    prefix = " " * indent
    relation_name = _name("rel", inverse)
    lines.append(f"{prefix}{relation_name}[{subject}]:")
    row_prefix = " " * (indent + 2)
    for relation in relations:
        predicate = _name(relation.predicate, inverse)
        lines.append(f"{row_prefix}{predicate} {relation.object}")
