"""JSON <-> SDIF conversion helpers.

The JSON document is the semantic source of truth for generated benchmark fixtures.
The SDIF encoder is intentionally strict where the current grammar would be
ambiguous. It preserves JSON semantics by using compact SDIF tables for scalar
uniform arrays and a reserved repeated ``__item`` object convention for nested
or heterogeneous arrays.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TypeAlias

from sdif.core.ast import Document, Field, Narrative, ObjectBlock, Relation, Rule, Table

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_INTEGER_RE = re.compile(r"^[+-]?(0|[1-9][0-9]*)$")
_DECIMAL_RE = re.compile(r"^[+-]?(0|[1-9][0-9]*)\.[0-9]+$")
_RESERVED_ARRAY_ITEM_KEY = "__item"
_RESERVED_ARRAY_VALUE_KEY = "__value"
_RESERVED_KEYS = {_RESERVED_ARRAY_ITEM_KEY, _RESERVED_ARRAY_VALUE_KEY}


def document_to_json_data(doc: Document) -> dict[str, JsonValue]:
    """Convert a parsed SDIF document into JSON-compatible data.

    This is the inverse of :func:`json_data_to_sdif` for the supported shapes:
    scalar fields, scalar lists, nested objects, uniform scalar-cell tables,
    relations, rules, narrative text blocks, and generated nested arrays encoded
    through repeated ``__item`` blocks.
    """

    value = _statements_to_json_value(doc.statements)
    if not isinstance(value, dict):  # pragma: no cover - top-level parser cannot create this today
        raise ValueError("top-level SDIF JSON conversion requires a mapping document")
    return value


def json_data_to_sdif(data: Mapping[str, object], *, include_header: bool = True) -> str:
    """Encode a JSON mapping as SDIF.

    ``include_header`` defaults to true because v1 documents require an
    explicit ``@sdif 1.0`` format contract.
    """

    _assert_mapping_has_no_reserved_keys(data, path="$")
    lines: list[str] = []
    if include_header:
        lines.append("@sdif 1.0")
    _emit_mapping(data, lines, indent=0)
    return "\n".join(lines).rstrip() + "\n"


def _statements_to_json_value(statements: Sequence[object]) -> JsonValue:
    if statements and all(_is_array_item_statement(statement) for statement in statements):
        return [_array_item_to_json_value(statement) for statement in statements]

    data: dict[str, JsonValue] = {}
    relations: list[JsonValue] = []
    rules: list[JsonValue] = []

    for statement in statements:
        if isinstance(statement, Field):
            data[statement.key] = _parse_value(
                statement.value, quoted=getattr(statement, "quoted", False)
            )
        elif isinstance(statement, ObjectBlock):
            data[statement.key] = _statements_to_json_value(statement.statements)
        elif isinstance(statement, Table):
            data[statement.name] = [
                {
                    _json_column_name(column): _parse_table_cell(
                        column, cell, quoted=column_index in statement.quoted_columns
                    )
                    for column_index, (column, cell) in enumerate(
                        zip(statement.columns, row, strict=True)
                    )
                }
                for row in statement.rows
            ]
        elif isinstance(statement, Relation):
            relations.append(
                {
                    "subject": statement.subject,
                    "predicate": statement.predicate,
                    "object": _parse_value(
                        statement.object, quoted=getattr(statement, "object_quoted", False)
                    ),
                }
            )
        elif isinstance(statement, Rule):
            rules.append(statement.source)
        elif isinstance(statement, Narrative):
            data[statement.key] = statement.text

    if relations:
        data["rel"] = relations
    if rules:
        data["rules"] = rules
    return data


def _json_column_name(column: str) -> str:
    if column.endswith("$"):
        return column[:-1]
    return column


def _parse_table_cell(column: str, cell: str, *, quoted: bool = False) -> JsonValue:
    if quoted or column.endswith("$"):
        if _is_quoted(cell):
            return _unquote(cell)
        return cell
    return _parse_value(cell)


def _is_array_item_statement(statement: object) -> bool:
    return isinstance(statement, ObjectBlock) and statement.key == _RESERVED_ARRAY_ITEM_KEY


def _array_item_to_json_value(statement: object) -> JsonValue:
    if not isinstance(statement, ObjectBlock):  # pragma: no cover - guarded by caller
        raise TypeError(f"unsupported array item statement: {statement!r}")

    if _is_wrapped_scalar_or_array_item(statement):
        wrapped = statement.statements[0]
        if isinstance(wrapped, Field):
            return _parse_value(wrapped.value, quoted=getattr(wrapped, "quoted", False))
        if isinstance(wrapped, ObjectBlock):
            return _statements_to_json_value(wrapped.statements)
        if isinstance(wrapped, Narrative):
            return wrapped.text

    return _statements_to_json_value(statement.statements)


def _is_wrapped_scalar_or_array_item(statement: ObjectBlock) -> bool:
    if len(statement.statements) != 1:
        return False
    wrapped = statement.statements[0]
    return (
        isinstance(wrapped, Field | ObjectBlock | Narrative)
        and getattr(wrapped, "key", None) == _RESERVED_ARRAY_VALUE_KEY
    )


def _emit_mapping(data: Mapping[str, object], lines: list[str], indent: int) -> None:
    prefix = " " * indent
    for key, value in data.items():
        _validate_identifier(key, "key")

        if key == "rel" and isinstance(value, list) and _is_relation_list(value):
            lines.append(f"{prefix}rel:")
            for item in value:
                relation = item  # type: ignore[assignment]
                lines.append(
                    f"{' ' * (indent + 2)}"
                    f"{_format_scalar(relation['subject'])} "
                    f"{_format_scalar(relation['predicate'])} "
                    f"{_format_scalar(relation['object'])}"
                )
        elif (
            key == "rules"
            and isinstance(value, list)
            and all(isinstance(item, str) for item in value)
        ):
            lines.append(f"{prefix}rules:")
            for item in value:
                lines.append(f"{' ' * (indent + 2)}{item}")
        elif _can_emit_as_table(value):
            _emit_table(key, value, lines, indent)  # type: ignore[arg-type]
        elif isinstance(value, list):
            _emit_list(key, value, lines, indent)
        elif isinstance(value, Mapping):
            lines.append(f"{prefix}{key}:")
            _emit_mapping(value, lines, indent + 2)
        elif isinstance(value, str) and "\n" in value and indent == 0:
            lines.append(f'{prefix}{key} """')
            lines.extend(value.split("\n"))
            lines.append(f'{prefix}"""')
        else:
            lines.append(f"{prefix}{key} {_format_scalar(value)}")


def _emit_list(key: str, value: Sequence[object], lines: list[str], indent: int) -> None:
    prefix = " " * indent
    if not value:
        lines.append(f"{prefix}{key} []")
        return

    if all(_is_json_scalar(item) for item in value):
        lines.append(f"{prefix}{key} [{','.join(_format_list_item(item) for item in value)}]")
        return

    lines.append(f"{prefix}{key}:")
    for item in value:
        _emit_array_item(item, lines, indent + 2)


def _emit_array_item(value: object, lines: list[str], indent: int) -> None:
    prefix = " " * indent
    lines.append(f"{prefix}{_RESERVED_ARRAY_ITEM_KEY}:")

    if isinstance(value, Mapping):
        _emit_mapping(value, lines, indent + 2)
    elif isinstance(value, list):
        lines.append(f"{' ' * (indent + 2)}{_RESERVED_ARRAY_VALUE_KEY}:")
        for item in value:
            _emit_array_item(item, lines, indent + 4)
    else:
        lines.append(f"{' ' * (indent + 2)}{_RESERVED_ARRAY_VALUE_KEY} {_format_scalar(value)}")


def _can_emit_as_table(value: object) -> bool:
    if not isinstance(value, list) or not value:
        return False
    if not all(isinstance(item, Mapping) for item in value):
        return False

    mappings = [_as_mapping(row, "<candidate>") for row in value]
    columns = list(mappings[0].keys())
    if not columns:
        return False
    expected = set(columns)

    return all(
        set(row.keys()) == expected and all(_is_json_scalar(cell) for cell in row.values())
        for row in mappings
    )


def _emit_table(name: str, rows: Sequence[object], lines: list[str], indent: int) -> None:
    mappings = [_as_mapping(row, name) for row in rows]
    columns = list(mappings[0].keys())
    if not columns:
        raise ValueError(f"table `{name}` cannot be generated from empty objects")
    for column in columns:
        _validate_identifier(column, f"column in `{name}`")
    expected = set(columns)
    for row_idx, row in enumerate(mappings):
        if set(row.keys()) != expected:
            raise ValueError(
                f"table `{name}` row {row_idx} is not uniform; "
                f"expected columns {columns}, got {list(row.keys())}"
            )
        for column, value in row.items():
            if not _is_json_scalar(value):
                raise ValueError(
                    f"table `{name}` column `{column}` contains a nested value; "
                    "nested arrays must be encoded as block lists"
                )
    prefix = " " * indent
    lines.append(f"{prefix}{name}[{','.join(columns)}]:")
    for row in mappings:
        rendered = [_format_table_cell(row[column]) for column in columns]
        lines.append(" " * (indent + 2) + "\t".join(rendered))


def _as_mapping(row: object, table_name: str) -> Mapping[str, object]:
    if not isinstance(row, Mapping):
        raise ValueError(f"table `{table_name}` rows must be JSON objects")
    return row


def _is_relation_list(value: list[object]) -> bool:
    return all(
        isinstance(item, Mapping) and {"subject", "predicate", "object"}.issubset(item.keys())
        for item in value
    )


def _is_json_scalar(value: object) -> bool:
    return value is None or isinstance(value, str | int | float | bool)


def _format_scalar(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int | float) and not isinstance(value, bool):
        return str(value)

    text = str(value)
    if _must_quote_string(text):
        return _quote(text)
    return text


def _format_list_item(value: object) -> str:
    if isinstance(value, str) and "," in value:
        return _quote(value)
    return _format_scalar(value)


def _format_table_cell(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int | float) and not isinstance(value, bool):
        return str(value)

    text = str(value)
    if "\t" in text or "\n" in text:
        raise ValueError(
            "the SDIF v1 table encoder cannot represent tabs or newlines in table cells"
        )
    if _must_quote_table_cell(text):
        return _quote(text)
    return text


def _must_quote_table_cell(value: str) -> bool:
    if value == "":
        return True
    if value in {"null", "true", "false"}:
        return True
    if _INTEGER_RE.fullmatch(value) or _DECIMAL_RE.fullmatch(value):
        return True
    if _is_list_literal(value):
        return True
    return bool(any(char in value for char in ['"', "\\", "\n", "\t"]))


def _must_quote_string(value: str) -> bool:
    if value == "":
        return True
    if value in {"null", "true", "false"}:
        return True
    if _INTEGER_RE.fullmatch(value) or _DECIMAL_RE.fullmatch(value):
        return True
    if _is_list_literal(value):
        return True
    if any(char in value for char in ['"', "\\", "\n", "\t", " "]):
        return True
    return "#" in value


def _quote(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
    )
    return f'"{escaped}"'


def _parse_value(value: str, *, quoted: bool = False) -> JsonValue:
    if quoted:
        return value
    if _is_quoted(value):
        return _unquote(value)
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if _is_list_literal(value):
        return [_parse_value(item) for item in _split_list_items(value[1:-1])]
    if _INTEGER_RE.fullmatch(value):
        return int(value)
    if _DECIMAL_RE.fullmatch(value):
        return float(value)
    return value


def _is_list_literal(value: str) -> bool:
    return len(value) >= 2 and value[0] == "[" and value[-1] == "]"


def _split_list_items(source: str) -> list[str]:
    if source == "":
        return []
    items: list[str] = []
    current: list[str] = []
    in_quote = False
    escaped = False
    for char in source:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\" and in_quote:
            current.append(char)
            escaped = True
            continue
        if char == '"':
            current.append(char)
            in_quote = not in_quote
            continue
        if char == "," and not in_quote:
            items.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if in_quote or escaped:
        raise ValueError("unterminated quoted list value")
    items.append("".join(current).strip())
    return items


def _is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == value[-1] == '"'


def _unquote(value: str) -> str:
    if _is_quoted(value):
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    return value


def _validate_identifier(value: str, label: str) -> None:
    if not _IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"invalid SDIF {label}: `{value}`")
    if value in _RESERVED_KEYS:
        raise ValueError(f"invalid SDIF {label}: `{value}` is reserved for JSON array encoding")


def _assert_mapping_has_no_reserved_keys(data: Mapping[str, object], *, path: str) -> None:
    for key, value in data.items():
        if key in _RESERVED_KEYS:
            raise ValueError(f"JSON key `{path}.{key}` is reserved for SDIF array encoding")
        if isinstance(value, Mapping):
            _assert_mapping_has_no_reserved_keys(value, path=f"{path}.{key}")
        elif isinstance(value, list):
            _assert_list_has_no_reserved_keys(value, path=f"{path}.{key}")


def _assert_list_has_no_reserved_keys(values: Sequence[object], *, path: str) -> None:
    for index, value in enumerate(values):
        item_path = f"{path}[{index}]"
        if isinstance(value, Mapping):
            _assert_mapping_has_no_reserved_keys(value, path=item_path)
        elif isinstance(value, list):
            _assert_list_has_no_reserved_keys(value, path=item_path)
