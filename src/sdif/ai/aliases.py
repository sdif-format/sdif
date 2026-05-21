"""Generate compact `.sdif.ai` projections with explicit reversible aliases."""

from __future__ import annotations

from sdif import parse_text
from sdif.canonical import canonicalize
from typing import Sequence
from sdif.core.policy import Policy
from sdif.core.policy import PolicyError

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


def ai_view(
    source: str | Document,
    aliases: dict[str, str],
    *,
    include_header: bool = True,
    policy: Policy | None = None,
) -> str:
    doc = parse_text(source, policy=policy) if isinstance(source, str) else source
    _ensure_safe_projection(doc.statements)
    inverse = {canonical: alias for canonical, alias in aliases.items()}
    lines = ["@sdif.ai 1.0"] if include_header else []
    if include_header and aliases:
        entries = ",".join(
            f"{alias}={canonical}"
            for canonical, alias in sorted(aliases.items(), key=lambda item: item[1])
        )
        lines.append(f"alias[{entries}]")
    _emit_statements(doc.statements, lines, inverse, 0)
    return "\n".join(lines).rstrip() + "\n"


def sdif_from_ai(source: str | Document, *, policy: Policy | None = None) -> str:
    """Convert a `.sdif.ai` projection back to canonical source SDIF.

    The reverse contract is canonical/semantic, not byte-for-byte source
    recovery. This function does not preserve source trivia, comments, original
    ordering, or byte-for-byte source formatting. Perfect canonical isomorphism
    must be proven by comparing canonical hashes of the original source and
    this restored source.
    """
    from sdif.core.policy import Policy

    pol = policy or Policy()

    doc = parse_text(source, policy=pol) if isinstance(source, str) else source
    aliases = _alias_to_canonical(doc)
    directives = _source_directives(doc)

    expansion_count = [0]
    limit = pol.max_alias_expansion

    statements: list[Statement] = [
        _expand_statement(statement, aliases, expansion_count, limit)
        for statement in doc.statements
    ]
    return canonicalize(Document(directives=directives, statements=statements))


def _name(name: str, inverse: dict[str, str]) -> str:
    return inverse.get(name, name)


def _expanded_name(
    name: str,
    aliases: dict[str, str],
    expansion_count: list[int] | None = None,
    limit: int = 0,
) -> str:
    if name in aliases:
        if expansion_count is not None:
            expansion_count[0] += 1
            if expansion_count[0] > limit:
                from sdif.core.policy import PolicyError

                raise PolicyError(
                    "SDIF_POLICY_ALIAS_EXPANSION",
                    f"Alias expansion limit of {limit} exceeded",
                )
        return aliases[name]
    return name


def _alias_to_canonical(doc: Document) -> dict[str, str]:
    from sdif.core.policy import RESERVED_TERMS, PolicyError

    aliases: dict[str, str] = {}
    for directive in doc.directives:
        if directive.name != "alias":
            continue
        for entry in directive.args:
            if "=" not in entry:
                continue
            alias, canonical = entry.split("=", 1)
            alias = alias.strip()
            canonical = canonical.strip()

            # Check reserved terms
            if alias in RESERVED_TERMS or canonical in RESERVED_TERMS:
                raise PolicyError(
                    "SDIF_POLICY_ALIAS_RESERVED",
                    f"Alias entry '{entry}' uses or targets a reserved term",
                )

            # Check duplicate collision
            if alias in aliases and aliases[alias] != canonical:
                raise PolicyError(
                    "SDIF_POLICY_ALIAS_COLLISION",
                    f"Alias collision: '{alias}' is mapped to both '{aliases[alias]}' and '{canonical}'",
                )
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
        directives.insert(0, Directive("sdif", ["1.0"]))
    return directives


def _expand_statement(
    statement: object,
    aliases: dict[str, str],
    expansion_count: list[int] | None = None,
    limit: int = 0,
) -> Statement:
    if isinstance(statement, Field):
        return Field(
            _expanded_name(statement.key, aliases, expansion_count, limit),
            statement.value,
            statement.quoted,
        )
    if isinstance(statement, ObjectBlock):
        return ObjectBlock(
            _expanded_name(statement.key, aliases, expansion_count, limit),
            [
                _expand_statement(child, aliases, expansion_count, limit)
                for child in statement.statements
            ],
        )
    if isinstance(statement, Table):
        columns: list[str] = []
        quoted_columns: set[int] = set(statement.quoted_columns)
        for index, column in enumerate(statement.columns):
            if column.endswith("$"):
                quoted_columns.add(index)
                column = column[:-1]
            columns.append(_expanded_name(column, aliases, expansion_count, limit))
        return Table(
            _expanded_name(statement.name, aliases, expansion_count, limit),
            columns,
            statement.rows,
            frozenset(quoted_columns),
        )
    if isinstance(statement, Relation):
        return Relation(
            statement.subject,
            _expanded_name(statement.predicate, aliases, expansion_count, limit),
            statement.object,
            statement.object_quoted,
        )
    if isinstance(statement, Rule):
        return statement
    if isinstance(statement, Narrative):
        return Narrative(
            _expanded_name(statement.key, aliases, expansion_count, limit),
            statement.text,
        )
    raise TypeError(f"unsupported statement: {statement!r}")


def _is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == value[-1] == '"'


def _unquote(value: str) -> str:
    return bytes(value[1:-1], "utf-8").decode("unicode_escape")


def _ai_columns_and_rows(
    table: Table, inverse: dict[str, str]
) -> tuple[list[str], list[list[str]]]:
    string_columns = {
        index
        for index in range(len(table.columns))
        if table.rows and all(_is_quoted(row[index]) for row in table.rows)
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


def _ensure_safe_projection(statements: Sequence[object]) -> None:
    for statement in statements:
        if isinstance(statement, ObjectBlock):
            _ensure_safe_projection(statement.statements)
        elif isinstance(statement, Table):
            _ensure_safe_table_projection(statement)


def _ensure_safe_table_projection(table: Table) -> None:
    for column_index, column in enumerate(table.columns):
        quoted = [_is_quoted(row[column_index]) for row in table.rows]
        if all(quoted):
            for row in table.rows:
                unquoted = _unquote(row[column_index])
                if "\t" in unquoted or "\n" in unquoted:
                    raise PolicyError(
                        "SDIF_AI_UNSAFE_PROJECTION",
                        f"table `{table.name}` column `{column}` contains a value unsafe for compact rows",
                    )


def _emit(statement: object, lines: list[str], inverse: dict[str, str], indent: int) -> None:
    prefix = " " * indent
    if isinstance(statement, Field):
        value = _quote(statement.value) if statement.quoted else statement.value
        lines.append(f"{prefix}{_name(statement.key, inverse)} {value}")
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
        relation_object = _quote(statement.object) if statement.object_quoted else statement.object
        lines.append(
            f"{' ' * (indent + 2)}{statement.subject} {statement.predicate} {relation_object}"
        )
    elif isinstance(statement, Rule):
        if not lines or lines[-1] != f"{prefix}rules:":
            lines.append(f"{prefix}rules:")
        lines.append(f"{' ' * (indent + 2)}{statement.source}")
    elif isinstance(statement, Narrative):
        lines.append(f'{prefix}{_name(statement.key, inverse)} """')
        lines.extend(f"{prefix}{line}" for line in statement.text.split("\n"))
        lines.append(f'{prefix}"""')


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
        relation_object = _quote(relation.object) if relation.object_quoted else relation.object
        lines.append(f"{row_prefix}{predicate} {relation_object}")


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'
