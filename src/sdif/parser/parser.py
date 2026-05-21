"""A deliberately small normative parser slice for SDIF 0.1 MVP syntax."""

from __future__ import annotations

import re
from dataclasses import dataclass

from sdif.core.ast import (
    Directive,
    Document,
    Field,
    Narrative,
    ObjectBlock,
    Relation,
    Rule,
    Table,
    Statement,
)

_TABLE_HEADER_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_-]*)\[(?P<cols>[^\]]+)\]:$")
_ALIAS_HEADER_RE = re.compile(
    r"^alias\[(?P<entries>[A-Za-z_][A-Za-z0-9_-]*=[A-Za-z_][A-Za-z0-9_-]*(?:,[A-Za-z_][A-Za-z0-9_-]*=[A-Za-z_][A-Za-z0-9_-]*)*)\]$"
)
_BLOCK_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):$")
_NARRATIVE_RE = re.compile(r'^(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s+"""$')


@dataclass
class ParseError(Exception):
    code: str
    message: str
    line: int
    column: int = 1
    hint: str | None = None

    def __str__(self) -> str:
        return f"{self.code} at {self.line}:{self.column}: {self.message}"


def parse_text(text: str) -> Document:
    parser = _Parser(text)
    return parser.parse_document()


class _Parser:
    def __init__(self, text: str) -> None:
        self.lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.index = 0
        self.is_ai_profile = False
        self.alias_to_canonical: dict[str, str] = {}

    def parse_document(self) -> Document:
        directives: list[Directive] = []
        statements: list[Statement] = []
        while self.index < len(self.lines):
            parsed = self._parse_next(indent=0)
            if parsed is None:
                continue
            if isinstance(parsed, Directive):
                directives.append(parsed)
            elif isinstance(parsed, list):
                statements.extend(parsed)  # type: ignore[arg-type]
            else:
                statements.append(parsed)  # type: ignore[arg-type]
        return Document(directives=directives, statements=statements)

    def _parse_next(self, indent: int) -> object | list[object] | None:
        line_no = self.index + 1
        raw = self.lines[self.index]
        if raw.strip() == "" or raw.lstrip().startswith("#"):
            self.index += 1
            return None
        actual_indent = _indent(raw, line_no)
        if actual_indent < indent:
            return None
        if actual_indent > indent:
            raise ParseError("SDIF_INDENT", "unexpected indentation", line_no, actual_indent + 1)

        body = raw[indent:]
        if body.startswith("@"):
            self.index += 1
            return self._parse_directive(body, line_no)

        alias = _ALIAS_HEADER_RE.match(_strip_inline_comment(body))
        if alias:
            self.index += 1
            entries = alias.group("entries").split(",")
            for entry in entries:
                alias_name, canonical_name = entry.split("=", 1)
                self.alias_to_canonical[alias_name] = canonical_name
            return Directive("alias", entries)

        narrative = _NARRATIVE_RE.match(body)
        if narrative:
            return self._parse_narrative(narrative.group("key"), actual_indent, line_no)

        table = _TABLE_HEADER_RE.match(_strip_inline_comment(body))
        if table:
            if self._is_relation_subject_header(table.group("name")):
                if not self.is_ai_profile:
                    raise ParseError(
                        "SDIF_AI_REL_SUBJECT",
                        "rel[subject]: syntax is only valid in .sdif.ai documents",
                        line_no,
                    )
                return self._parse_relations_for_subject(table.group("cols"), indent, line_no)
            return self._parse_table(table, indent, line_no)

        block = _BLOCK_RE.match(_strip_inline_comment(body))
        if block:
            key = block.group("key")
            if key == "rel":
                return self._parse_relations(indent, line_no)
            if key == "rules":
                return self._parse_rules(indent, line_no)
            return self._parse_object(key, indent, line_no)

        self.index += 1
        return self._parse_field(body, line_no)

    def _parse_directive(self, body: str, line_no: int) -> Directive:
        body = _strip_inline_comment(body)
        parts = body[1:].split()
        if not parts:
            raise ParseError("SDIF_DIRECTIVE", "empty directive", line_no)
        if parts[0] == "sdif.ai":
            self.is_ai_profile = True
        return Directive(parts[0], parts[1:])

    def _is_relation_subject_header(self, name: str) -> bool:
        return name == "rel" or self.alias_to_canonical.get(name) == "rel"

    def _parse_field(self, body: str, line_no: int) -> Field:
        clean = _strip_inline_comment(body)
        if " " not in clean and "\t" not in clean:
            raise ParseError("SDIF_FIELD", "field requires a key and value", line_no)
        key, value = clean.split(None, 1)
        raw_value = value.strip()
        return Field(key, _unquote(raw_value), quoted=_is_quoted(raw_value))

    def _parse_object(self, key: str, indent: int, line_no: int) -> ObjectBlock:
        self.index += 1
        child_indent = indent + 2
        statements: list[object] = []
        while self.index < len(self.lines):
            raw = self.lines[self.index]
            if raw.strip() == "":
                self.index += 1
                continue
            if _indent(raw, self.index + 1) < child_indent:
                break
            parsed = self._parse_next(child_indent)
            if parsed is None:
                continue
            if isinstance(parsed, Directive):
                raise ParseError(
                    "SDIF_OBJECT_DIRECTIVE", "directive not allowed inside object", line_no
                )
            if isinstance(parsed, list):
                statements.extend(parsed)
            else:
                statements.append(parsed)
        return ObjectBlock(key, statements)

    def _parse_table(self, match: re.Match[str], indent: int, line_no: int) -> Table:
        self.index += 1
        name = match.group("name")
        columns = [c.strip() for c in match.group("cols").split(",") if c.strip()]
        if not columns:
            raise ParseError("SDIF_TABLE_HEADER", "table must declare columns", line_no)
        rows: list[list[str]] = []
        child_indent = indent + 2
        while self.index < len(self.lines):
            row_no = self.index + 1
            raw = self.lines[self.index]
            if raw.strip() == "":
                self.index += 1
                continue
            actual = _indent(raw, row_no)
            if actual == child_indent:
                row_text = raw[child_indent:]
            elif actual == indent and "\t" in raw[indent:]:
                row_text = raw[indent:]
            elif actual < child_indent:
                break
            else:
                raise ParseError("SDIF_INDENT", "invalid table row indentation", row_no, actual + 1)
            cells = row_text.split("\t")
            if len(cells) != len(columns):
                msg = f"table row has {len(cells)} cells but header declares {len(columns)} columns"
                raise ParseError(
                    "SDIF_TABLE_ARITY",
                    msg,
                    row_no,
                    column=child_indent + 1,
                    hint="check HTAB separators and missing cells",
                )
            rows.append(cells)
            self.index += 1
        return Table(name, columns, rows)

    def _parse_relations(self, indent: int, line_no: int) -> list[Relation]:
        self.index += 1
        child_indent = indent + 2
        relations: list[Relation] = []
        while self.index < len(self.lines):
            row_no = self.index + 1
            raw = self.lines[self.index]
            if raw.strip() == "":
                self.index += 1
                continue
            actual = _indent(raw, row_no)
            if actual < child_indent:
                break
            if actual != child_indent:
                raise ParseError(
                    "SDIF_INDENT", "invalid relation row indentation", row_no, actual + 1
                )
            parts = _split_quoted_whitespace(
                _strip_inline_comment(raw[child_indent:]), row_no, "SDIF_REL_QUOTE"
            )
            if len(parts) != 3:
                raise ParseError(
                    "SDIF_REL_ARITY", "relation row must have exactly three parts", row_no
                )
            relations.append(
                Relation(parts[0], parts[1], _unquote(parts[2]), object_quoted=_is_quoted(parts[2]))
            )
            self.index += 1
        return relations

    def _parse_relations_for_subject(
        self, subject: str, indent: int, line_no: int
    ) -> list[Relation]:
        self.index += 1
        child_indent = indent + 2
        relations: list[Relation] = []
        while self.index < len(self.lines):
            row_no = self.index + 1
            raw = self.lines[self.index]
            if raw.strip() == "":
                self.index += 1
                continue
            actual = _indent(raw, row_no)
            if actual < child_indent:
                break
            if actual != child_indent:
                raise ParseError(
                    "SDIF_INDENT", "invalid relation row indentation", row_no, actual + 1
                )
            parts = _split_quoted_whitespace(
                _strip_inline_comment(raw[child_indent:]), row_no, "SDIF_REL_QUOTE"
            )
            if len(parts) != 2:
                raise ParseError(
                    "SDIF_REL_ARITY",
                    "subject-grouped relation row must have exactly two parts",
                    row_no,
                )
            relations.append(
                Relation(subject, parts[0], _unquote(parts[1]), object_quoted=_is_quoted(parts[1]))
            )
            self.index += 1
        return relations

    def _parse_rules(self, indent: int, line_no: int) -> list[Rule]:
        self.index += 1
        child_indent = indent + 2
        rules: list[Rule] = []
        while self.index < len(self.lines):
            row_no = self.index + 1
            raw = self.lines[self.index]
            if raw.strip() == "":
                self.index += 1
                continue
            actual = _indent(raw, row_no)
            if actual < child_indent:
                break
            if actual != child_indent:
                raise ParseError("SDIF_INDENT", "invalid rule row indentation", row_no, actual + 1)
            source = _strip_inline_comment(raw[child_indent:]).strip()
            if not _balanced_parens(source):
                raise ParseError(
                    "SDIF_RULE_EXPR", "rule expression must have balanced parentheses", row_no
                )
            rules.append(Rule(source))
            self.index += 1
        return rules

    def _parse_narrative(self, key: str, indent: int, line_no: int) -> Narrative:
        self.index += 1
        content: list[str] = []
        prefix = " " * indent
        while self.index < len(self.lines):
            raw = self.lines[self.index]
            if raw.strip() == '"""':
                if raw != prefix + '"""':
                    raise ParseError(
                        "SDIF_NARRATIVE_CLOSE_ALIGN",
                        "unterminated narrative block or mismatched alignment at close",
                        self.index + 1,
                        column=len(raw) - len(raw.lstrip()) + 1,
                        hint="closing triple quotes must match the indentation of the opening block",
                    )
                self.index += 1
                return Narrative(key, "\n".join(content))
            if raw.startswith(prefix):
                content.append(raw[len(prefix) :])
            else:
                content.append(raw)
            self.index += 1
        raise ParseError(
            "SDIF_NARRATIVE_UNCLOSED",
            "unterminated narrative block",
            line_no,
            hint="make sure to close the narrative block with triple quotes aligned to the opening indentation",
        )


def _indent(raw: str, line_no: int) -> int:
    count = 0
    for char in raw:
        if char == " ":
            count += 1
        elif char == "\t":
            raise ParseError(
                "SDIF_INDENT_TAB", "tabs must not be used for indentation", line_no, count + 1
            )
        else:
            break
    return count


def _strip_inline_comment(body: str) -> str:
    in_quote = False
    escaped = False
    for idx, char in enumerate(body):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_quote:
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if char == "#" and not in_quote and (idx == 0 or body[idx - 1].isspace()):
            return body[:idx].rstrip()
    return body.rstrip()


def _is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == value[-1] == '"'


def _unquote(value: str) -> str:
    if _is_quoted(value):
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    return value


def _split_quoted_whitespace(source: str, line_no: int, error_code: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_quote = False
    escaped = False
    for column, char in enumerate(source, start=1):
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
        if char.isspace() and not in_quote:
            if current:
                parts.append("".join(current))
                current = []
            continue
        current.append(char)
    if escaped or in_quote:
        raise ParseError(error_code, "unterminated quoted value", line_no, len(source) + 1)
    if current:
        parts.append("".join(current))
    return parts


def _balanced_parens(source: str) -> bool:
    depth = 0
    for char in source:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0 and source.startswith("(") and source.endswith(")")
