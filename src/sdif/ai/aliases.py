"""Generate compact `.sdif.ai` projections with explicit aliases."""
from __future__ import annotations

from sdif import parse_text
from sdif.core.ast import Document, Field, Narrative, ObjectBlock, Relation, Rule, Table


def ai_view(source: str | Document, aliases: dict[str, str], *, include_header: bool = True) -> str:
    doc = parse_text(source) if isinstance(source, str) else source
    inverse = {canonical: alias for canonical, alias in aliases.items()}
    lines = ["@sdif.ai 0.1"] if include_header else []
    if include_header and aliases:
        entries = ",".join(f"{alias}={canonical}" for canonical, alias in sorted(aliases.items(), key=lambda item: item[1]))
        lines.append(f"alias[{entries}]")
    for statement in doc.statements:
        _emit(statement, lines, inverse, 0)
    return "\n".join(lines).rstrip() + "\n"


def _name(name: str, inverse: dict[str, str]) -> str:
    return inverse.get(name, name)


def _is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == value[-1] == '"'


def _unquote(value: str) -> str:
    return bytes(value[1:-1], "utf-8").decode("unicode_escape")


def _ai_columns_and_rows(table: Table, inverse: dict[str, str]) -> tuple[list[str], list[list[str]]]:
    string_columns = {
        index
        for row in table.rows
        for index, cell in enumerate(row)
        if _is_quoted(cell)
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
        lines.append(f"{' ' * (indent + 2)}{statement.subject} {statement.predicate} {statement.object}")
    elif isinstance(statement, Rule):
        if not lines or lines[-1] != f"{prefix}rules:":
            lines.append(f"{prefix}rules:")
        lines.append(f"{' ' * (indent + 2)}{statement.source}")
    elif isinstance(statement, Narrative):
        lines.append(f'{prefix}{_name(statement.key, inverse)} """')
        lines.extend(statement.text.split("\n"))
        lines.append('"""')
