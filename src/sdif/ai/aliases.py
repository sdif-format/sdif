"""Generate compact `.sdif.ai` projections with explicit aliases."""
from __future__ import annotations

from sdif import parse_text
from sdif.core.ast import Document, Field, Narrative, ObjectBlock, Relation, Rule, Table


def ai_view(source: str | Document, aliases: dict[str, str]) -> str:
    doc = parse_text(source) if isinstance(source, str) else source
    inverse = {canonical: alias for canonical, alias in aliases.items()}
    lines = ["@sdif.ai 0.1"]
    if aliases:
        entries = ",".join(f"{alias}={canonical}" for canonical, alias in sorted(aliases.items(), key=lambda item: item[1]))
        lines.append(f"alias[{entries}]")
    for statement in doc.statements:
        _emit(statement, lines, inverse, 0)
    return "\n".join(lines).rstrip() + "\n"


def _name(name: str, inverse: dict[str, str]) -> str:
    return inverse.get(name, name)


def _emit(statement: object, lines: list[str], inverse: dict[str, str], indent: int) -> None:
    prefix = " " * indent
    if isinstance(statement, Field):
        lines.append(f"{prefix}{_name(statement.key, inverse)} {statement.value}")
    elif isinstance(statement, ObjectBlock):
        lines.append(f"{prefix}{_name(statement.key, inverse)}:")
        for child in statement.statements:
            _emit(child, lines, inverse, indent + 2)
    elif isinstance(statement, Table):
        columns = [_name(column, inverse) for column in statement.columns]
        lines.append(f"{prefix}{_name(statement.name, inverse)}[{','.join(columns)}]:")
        for row in statement.rows:
            lines.append(" " * (indent + 2) + "\t".join(row))
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
