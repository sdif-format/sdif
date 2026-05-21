"""Minimal schema and validation layer for SDIF MVP fixtures."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime

from sdif.core.ast import Document, Field, Table

_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_./:-][A-Za-z0-9_./:-]*$")
_INTEGER_RE = re.compile(r"^[+-]?[0-9]+$")
_DECIMAL_RE = re.compile(r"^[+-]?[0-9]+\.[0-9]+$")


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    path: str
    line: int | None = None
    column: int | None = None
    hint: str | None = None


@dataclass(frozen=True)
class RuleFunction:
    name: str
    min_args: int
    max_args: int


@dataclass(frozen=True)
class TablePolicy:
    name: str
    ordered: bool = True
    primary_key: str | None = None


class SchemaError(ValueError):
    """Raised when a document cannot be used as an SDIF schema."""


@dataclass(frozen=True)
class RelationPolicy:
    predicate: str
    subject_type: str = "Identifier"
    object_type: str = "Identifier"
    required: bool = False


@dataclass(frozen=True)
class Schema:
    required_fields: set[str] = field(default_factory=set)
    field_types: dict[str, str] = field(default_factory=dict)
    required_table_columns: dict[str, set[str]] = field(default_factory=dict)
    table_column_types: dict[str, dict[str, str]] = field(default_factory=dict)
    rule_functions: dict[str, RuleFunction] = field(default_factory=dict)
    table_policies: dict[str, TablePolicy] = field(default_factory=dict)
    relation_policies: dict[str, RelationPolicy] = field(default_factory=dict)

    @classmethod
    def from_document(cls, doc: Document) -> "Schema":
        kind = doc.fields.get("kind")
        if kind is None or kind.value != "Schema":
            actual = "<missing>" if kind is None else kind.value
            raise SchemaError(f"expected schema document with `kind Schema`, got `{actual}`")

        required_fields: set[str] = set()
        field_types: dict[str, str] = {}
        required_columns: dict[str, set[str]] = {}
        table_column_types: dict[str, dict[str, str]] = {}
        rule_functions: dict[str, RuleFunction] = {}
        table_policies: dict[str, TablePolicy] = {}
        relation_policies: dict[str, RelationPolicy] = {}

        tables_policy = doc.tables.get("tables")
        if tables_policy:
            name_idx = _required_column(tables_policy.columns, "name", "tables")
            ordered_idx = _optional_column(tables_policy.columns, "ordered")
            pk_idx = _optional_column(tables_policy.columns, "primary_key")
            for row in tables_policy.rows:
                name = row[name_idx]
                ordered = True if ordered_idx is None else row[ordered_idx] == "true"
                primary_key = None if pk_idx is None or row[pk_idx] == "null" else row[pk_idx]
                table_policies[name] = TablePolicy(
                    name=name, ordered=ordered, primary_key=primary_key
                )

        fields_table = doc.tables.get("fields")
        if fields_table:
            name_idx = _required_column(fields_table.columns, "name", "fields")
            type_idx = _optional_column(fields_table.columns, "type")
            required_idx = _required_column(fields_table.columns, "required", "fields")
            for row in fields_table.rows:
                name = row[name_idx]
                if row[required_idx] == "true":
                    required_fields.add(name)
                if type_idx is not None:
                    field_types[name] = row[type_idx]

        columns_table = doc.tables.get("columns")
        if columns_table:
            table_idx = _required_column(columns_table.columns, "table", "columns")
            name_idx = _required_column(columns_table.columns, "name", "columns")
            type_idx = _optional_column(columns_table.columns, "type")
            required_idx = _required_column(columns_table.columns, "required", "columns")
            for row in columns_table.rows:
                table_name = row[table_idx]
                column_name = row[name_idx]
                if row[required_idx] == "true":
                    required_columns.setdefault(table_name, set()).add(column_name)
                if type_idx is not None:
                    table_column_types.setdefault(table_name, {})[column_name] = row[type_idx]

        relations_table = doc.tables.get("relations")
        if relations_table:
            predicate_idx = _required_column(relations_table.columns, "predicate", "relations")
            subject_type_idx = _optional_column(relations_table.columns, "subject_type")
            object_type_idx = _optional_column(relations_table.columns, "object_type")
            rel_required_idx = _optional_column(relations_table.columns, "required")
            for row in relations_table.rows:
                predicate = row[predicate_idx]
                subject_type = "Identifier" if subject_type_idx is None else row[subject_type_idx]
                object_type = "Identifier" if object_type_idx is None else row[object_type_idx]
                required = False if rel_required_idx is None else row[rel_required_idx] == "true"
                relation_policies[predicate] = RelationPolicy(
                    predicate=predicate,
                    subject_type=subject_type,
                    object_type=object_type,
                    required=required,
                )

        funcs_table = doc.tables.get("rule_functions")
        if funcs_table:
            name_idx = _required_column(funcs_table.columns, "name", "rule_functions")
            min_idx = _required_column(funcs_table.columns, "min_args", "rule_functions")
            max_idx = _required_column(funcs_table.columns, "max_args", "rule_functions")
            for row in funcs_table.rows:
                rule_functions[row[name_idx]] = RuleFunction(
                    name=row[name_idx], min_args=int(row[min_idx]), max_args=int(row[max_idx])
                )

        return cls(
            required_fields=required_fields,
            field_types=field_types,
            required_table_columns=required_columns,
            table_column_types=table_column_types,
            rule_functions=rule_functions,
            table_policies=table_policies,
            relation_policies=relation_policies,
        )


def diagnostics_to_json(diagnostics: list[Diagnostic]) -> list[dict[str, object]]:
    return [
        {key: value for key, value in asdict(diagnostic).items() if value is not None}
        for diagnostic in diagnostics
    ]


def validate_document(doc: Document, schema: Schema) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_validate_unique_top_level(doc))
    diagnostics.extend(_validate_allowed_tables(doc, schema))
    fields = doc.fields
    for field_name in sorted(schema.required_fields):
        if field_name not in fields:
            diagnostics.append(
                Diagnostic(
                    code="SDIF_REQUIRED_FIELD",
                    severity="error",
                    message=f"missing required field: {field_name}",
                    path=field_name,
                    hint=f"add `{field_name}` to the document",
                )
            )

    for field_name, type_name in schema.field_types.items():
        if field_name not in fields:
            continue
        diagnostics.extend(_validate_value(fields[field_name].value, type_name, field_name))

    tables = doc.tables
    for table_name in sorted(schema.required_table_columns):
        if table_name not in tables:
            diagnostics.append(
                Diagnostic(
                    code="SDIF_REQUIRED_TABLE",
                    severity="error",
                    message=f"missing required table: {table_name}",
                    path=table_name,
                    hint=f"add `{table_name}[...]` table",
                )
            )
            continue
        table = tables[table_name]
        present = set(table.columns)
        for column in sorted(schema.required_table_columns[table_name] - present):
            diagnostics.append(
                Diagnostic(
                    code="SDIF_REQUIRED_COLUMN",
                    severity="error",
                    message=f"missing required column: {table_name}.{column}",
                    path=f"{table_name}.{column}",
                    hint=f"add `{column}` to `{table_name}` table header",
                )
            )

    for table_name, column_types in schema.table_column_types.items():
        if table_name not in tables:
            continue
        table = tables[table_name]
        for column, type_name in column_types.items():
            if column not in table.columns:
                continue
            column_idx = table.columns.index(column)
            for row_idx, row in enumerate(table.rows):
                diagnostics.extend(
                    _validate_value(row[column_idx], type_name, f"{table_name}[{row_idx}].{column}")
                )

    if schema.relation_policies:
        diagnostics.extend(_validate_relations(doc, schema))

    if schema.rule_functions:
        for rule_idx, rule in enumerate(doc.rules):
            diagnostics.extend(_validate_rule(rule.source, schema, f"rules[{rule_idx}]"))

    return diagnostics


def _validate_unique_top_level(doc: Document) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen_fields: set[str] = set()
    seen_tables: set[str] = set()
    for statement in doc.statements:
        if isinstance(statement, Field):
            if statement.key in seen_fields:
                diagnostics.append(
                    _diag(
                        "SDIF_DUPLICATE_FIELD", statement.key, f"duplicate field `{statement.key}`"
                    )
                )
            seen_fields.add(statement.key)
        elif isinstance(statement, Table):
            if statement.name in seen_tables:
                diagnostics.append(
                    _diag(
                        "SDIF_DUPLICATE_TABLE",
                        statement.name,
                        f"duplicate table `{statement.name}`",
                    )
                )
            seen_tables.add(statement.name)
    return diagnostics


def _validate_allowed_tables(doc: Document, schema: Schema) -> list[Diagnostic]:
    if not schema.table_policies:
        return []
    allowed = set(schema.table_policies)
    diagnostics: list[Diagnostic] = []
    for table in (statement for statement in doc.statements if isinstance(statement, Table)):
        if table.name not in allowed:
            diagnostics.append(
                _diag(
                    "SDIF_TABLE_UNKNOWN",
                    table.name,
                    f"table `{table.name}` is not declared by the schema",
                )
            )
    return diagnostics


def _validate_relations(doc: Document, schema: Schema) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen_predicates = {relation.predicate for relation in doc.relations}
    for predicate, policy in sorted(schema.relation_policies.items()):
        if policy.required and predicate not in seen_predicates:
            diagnostics.append(
                _diag(
                    "SDIF_REQUIRED_RELATION",
                    f"rel.{predicate}",
                    f"missing required relation predicate `{predicate}`",
                )
            )

    for relation_idx, relation in enumerate(doc.relations):
        path = f"rel[{relation_idx}]"
        rel_policy = schema.relation_policies.get(relation.predicate)
        if rel_policy is None:
            diagnostics.append(
                _diag(
                    "SDIF_REL_PREDICATE",
                    f"{path}.predicate",
                    f"relation predicate `{relation.predicate}` is not declared by the schema",
                )
            )
            continue
        diagnostics.extend(
            _validate_value(relation.subject, rel_policy.subject_type, f"{path}.subject")
        )
        diagnostics.extend(
            _validate_value(relation.object, rel_policy.object_type, f"{path}.object")
        )
    return diagnostics


def _validate_value(value: str, type_name: str, path: str) -> list[Diagnostic]:
    enum_values = _enum_values(type_name)
    if enum_values is not None:
        if value not in enum_values:
            return [
                _diag("SDIF_ENUM", path, f"value `{value}` is not in enum {sorted(enum_values)}")
            ]
        return []

    ok = True
    if type_name == "Boolean":
        ok = value in {"true", "false"}
    elif type_name == "Integer":
        ok = bool(_INTEGER_RE.match(value))
    elif type_name == "Decimal":
        ok = bool(_DECIMAL_RE.match(value) or _INTEGER_RE.match(value))
    elif type_name in {"Identifier", "Path", "String"}:
        ok = bool(value) if type_name == "String" else bool(_IDENTIFIER_RE.match(value))
    elif type_name == "Date":
        ok = _valid_date(value)
    elif type_name == "DateTime":
        ok = _valid_datetime(value)
    elif type_name in {"Null", "Duration"}:
        ok = value == "null" if type_name == "Null" else value.startswith("P")
    else:
        ok = True
    return (
        [] if ok else [_diag("SDIF_TYPE", path, f"value `{value}` does not match type {type_name}")]
    )


def _validate_rule(source: str, schema: Schema, path: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for name, args in _extract_rule_calls(source):
        function = schema.rule_functions.get(name)
        if function is None:
            diagnostics.append(_diag("SDIF_RULE_FUNCTION", path, f"unknown rule function `{name}`"))
            continue
        arg_count = len(args)
        if arg_count < function.min_args or arg_count > function.max_args:
            diagnostics.append(
                _diag(
                    "SDIF_RULE_ARITY",
                    path,
                    f"rule function `{name}` expects {function.min_args}..{function.max_args} args, got {arg_count}",
                )
            )
    return diagnostics


def _extract_rule_calls(source: str) -> list[tuple[str, list[str]]]:
    source = source.strip()
    calls: list[tuple[str, list[str]]] = []
    if source.startswith("("):
        close = _matching_paren(source, 0)
        if close is not None:
            inner = source[1:close].strip()
            name, args_text = _leading_name_and_args(inner)
            if name:
                args = _split_top_level_args(args_text) if args_text else []
                calls.append((name, args))
                calls.extend(_extract_inline_calls(args_text))
            return calls
    calls.extend(_extract_inline_calls(source))
    return calls


def _extract_inline_calls(text: str) -> list[tuple[str, list[str]]]:
    calls: list[tuple[str, list[str]]] = []
    idx = 0
    while idx < len(text):
        if not (text[idx].isalpha() or text[idx] == "_"):
            idx += 1
            continue
        name_start = idx
        idx += 1
        while idx < len(text) and (text[idx].isalnum() or text[idx] in "_-"):
            idx += 1
        name = text[name_start:idx]
        if idx >= len(text) or text[idx] != "(":
            continue
        close = _matching_paren(text, idx)
        if close is None:
            break
        args_text = text[idx + 1 : close].strip()
        args = _split_top_level_args(args_text) if args_text else []
        calls.append((name, args))
        calls.extend(_extract_inline_calls(args_text))
        idx = close + 1
    return calls


def _leading_name_and_args(inner: str) -> tuple[str, str]:
    idx = 0
    while idx < len(inner) and (inner[idx].isalnum() or inner[idx] in "_-"):
        idx += 1
    if idx == 0:
        return "", ""
    return inner[:idx], inner[idx:].strip()


def _matching_paren(source: str, open_idx: int) -> int | None:
    depth = 0
    for idx in range(open_idx, len(source)):
        if source[idx] == "(":
            depth += 1
        elif source[idx] == ")":
            depth -= 1
            if depth == 0:
                return idx
    return None


def _count_call_args(source: str, start: int) -> int:
    depth = 1
    current = []
    args: list[str] = []
    idx = start
    while idx < len(source):
        char = source[idx]
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            if depth == 0:
                arg = "".join(current).strip()
                if arg:
                    args.extend(_split_top_level_args(arg))
                return len(args)
            current.append(char)
        else:
            current.append(char)
        idx += 1
    return 0


def _split_top_level_args(text: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if (char.isspace() or char == ",") and depth == 0:
            if current:
                args.append("".join(current).strip())
                current = []
            continue
        current.append(char)
    if current:
        args.append("".join(current).strip())
    return args


def _enum_values(type_name: str) -> set[str] | None:
    if not type_name.startswith("Enum(") or not type_name.endswith(")"):
        return None
    return {item.strip() for item in type_name[5:-1].split(",") if item.strip()}


def _valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _valid_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _diag(code: str, path: str, message: str) -> Diagnostic:
    return Diagnostic(code=code, severity="error", message=message, path=path)


def _required_column(columns: list[str], name: str, table: str) -> int:
    try:
        return columns.index(name)
    except ValueError as exc:
        raise SchemaError(f"schema table `{table}` requires `{name}` column") from exc


def _optional_column(columns: list[str], name: str) -> int | None:
    try:
        return columns.index(name)
    except ValueError:
        return None
