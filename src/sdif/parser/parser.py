"""Normative parser for SDIF v1 source and AI projection syntax."""

from __future__ import annotations

from pathlib import Path
import re
from dataclasses import dataclass

from sdif.core.policy import Policy, PolicyError, RESERVED_TERMS
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
    Identifier,
    Call,
    RuleExpression,
)

_TABLE_HEADER_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_-]*)\[(?P<cols>[^\]]+)\]:$")
_ALIAS_HEADER_RE = re.compile(
    r"^alias\[(?P<entries>[A-Za-z_][A-Za-z0-9_-]*=[A-Za-z_][A-Za-z0-9_-]*(?:,[A-Za-z_][A-Za-z0-9_-]*=[A-Za-z_][A-Za-z0-9_-]*)*)\]$"
)
_BLOCK_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):$")
_NARRATIVE_RE = re.compile(r'^(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s+"""$')
_KNOWN_DIRECTIVES = {
    "sdif",
    "sdif.ai",
    "profile",
    "vocab",
    "base",
    "namespace",
    "include",
}


@dataclass
class ParseError(Exception):
    code: str
    message: str
    line: int
    column: int = 1
    hint: str | None = None

    def __str__(self) -> str:
        return f"{self.code} at {self.line}:{self.column}: {self.message}"


def parse_text(text: str, *, policy: Policy | None = None) -> Document:
    parser = _Parser(text, policy=policy)
    return parser.parse_document()


class _Parser:
    def __init__(self, text: str, *, policy: Policy | None = None) -> None:
        self.policy = policy or Policy()
        if len(text.encode("utf-8")) > self.policy.max_document_size:
            raise PolicyError(
                "SDIF_POLICY_DOCUMENT_SIZE",
                f"Document size exceeds maximum limit of {self.policy.max_document_size} bytes",
            )
        self.lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.index = 0
        self.is_ai_profile = False
        self.format_directive_name: str | None = None
        self.alias_to_canonical: dict[str, str] = {}
        self.current_nesting_depth = 0

    def _check_string_length(self, value: str, field_desc: str) -> None:
        if len(value) > self.policy.max_string_length:
            raise PolicyError(
                "SDIF_POLICY_STRING_LENGTH",
                f"{field_desc} length {len(value)} exceeds maximum limit of {self.policy.max_string_length}",
            )

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
        if self.format_directive_name is None:
            raise ParseError(
                "SDIF_VERSION_MISSING",
                "document must declare @sdif 1.0 or @sdif.ai 1.0",
                1,
            )
        return Document(directives=directives, statements=statements)

    def _parse_next(self, indent: int) -> object | list[object] | None:
        line_no = self.index + 1
        raw = self.lines[self.index]
        if raw.strip() == "" or raw.lstrip().startswith("#"):
            self.index += 1
            return None
        actual_indent = _indent(raw, line_no)
        if actual_indent < indent:  # pragma: no cover
            return None  # pragma: no cover
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
                if "=" not in entry:  # pragma: no cover
                    raise ParseError("SDIF_ALIAS_SYNTAX", "invalid alias entry syntax", line_no)  # pragma: no cover
                alias_name, canonical_name = entry.split("=", 1)
                alias_name = alias_name.strip()
                canonical_name = canonical_name.strip()

                # Check reserved terms
                if alias_name in RESERVED_TERMS or canonical_name in RESERVED_TERMS:
                    raise PolicyError(
                        "SDIF_POLICY_ALIAS_RESERVED",
                        f"Alias entry '{entry}' uses or targets a reserved term",
                    )
                # Check duplicate collision
                if (
                    alias_name in self.alias_to_canonical
                    and self.alias_to_canonical[alias_name] != canonical_name
                ):
                    raise PolicyError(
                        "SDIF_POLICY_ALIAS_COLLISION",
                        f"Alias collision: '{alias_name}' is mapped to both '{self.alias_to_canonical[alias_name]}' and '{canonical_name}'",
                    )
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
        name = parts[0]
        args = parts[1:]
        if name not in _KNOWN_DIRECTIVES:
            raise ParseError(
                "SDIF_DIRECTIVE_UNKNOWN",
                f"unknown directive @{name}",
                line_no,
                hint="v1 documents only allow known core directives",
            )
        if name in {"sdif", "sdif.ai"}:
            if len(args) != 1:
                raise ParseError(
                    "SDIF_VERSION_SYNTAX",
                    f"@{name} requires exactly one version argument",
                    line_no,
                )
            if args[0] != "1.0":
                raise ParseError(
                    "SDIF_VERSION_UNSUPPORTED",
                    f"unsupported @{name} version `{args[0]}`",
                    line_no,
                    hint="this implementation supports format version 1.0",
                )
            if self.format_directive_name is not None:
                raise ParseError(
                    "SDIF_VERSION_CONFLICT",
                    "document must declare exactly one format version directive",
                    line_no,
                )
            self.format_directive_name = name
        if name == "sdif.ai":
            self.is_ai_profile = True
        return Directive(name, args)

    def _is_relation_subject_header(self, name: str) -> bool:
        return name == "rel" or self.alias_to_canonical.get(name) == "rel"

    def _parse_field(self, body: str, line_no: int) -> Field:
        clean = _strip_inline_comment(body)
        if " " not in clean and "\t" not in clean:
            raise ParseError("SDIF_FIELD", "field requires a key and value", line_no)
        key, value = clean.split(None, 1)
        raw_value = value.strip()
        _ensure_scalar_quote_closed(raw_value, line_no)
        unquoted = _unquote(raw_value)
        self._check_string_length(unquoted, "Field value")
        return Field(key, unquoted, quoted=_is_quoted(raw_value))

    def _parse_object(self, key: str, indent: int, line_no: int) -> ObjectBlock:
        self.current_nesting_depth += 1
        if self.current_nesting_depth > self.policy.max_nesting_depth:
            raise PolicyError(
                "SDIF_POLICY_NESTING_DEPTH",
                f"Nesting depth {self.current_nesting_depth} exceeds maximum limit of {self.policy.max_nesting_depth}",
            )
        try:
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
        finally:
            self.current_nesting_depth -= 1

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
            if _strip_inline_comment(row_text) != row_text.rstrip():
                raise ParseError(
                    "SDIF_TABLE_ROW_COMMENT",
                    "inline comments inside table rows are prohibited in strict mode",
                    row_no,
                )
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
            for cell in cells:
                self._check_string_length(cell, "Table cell")
            rows.append(cells)
            if len(rows) > self.policy.max_table_row_count:
                raise PolicyError(
                    "SDIF_POLICY_TABLE_ROW_COUNT",
                    f"Table row count {len(rows)} exceeds maximum limit of {self.policy.max_table_row_count}",
                )
            self.index += 1
        return Table(name, columns, rows)

    def _parse_relations(self, indent: int, _line_no: int) -> list[Relation]:
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
            unquoted_obj = _unquote(parts[2])
            self._check_string_length(unquoted_obj, "Relation object")
            relations.append(
                Relation(parts[0], parts[1], unquoted_obj, object_quoted=_is_quoted(parts[2]))
            )
            self.index += 1
        return relations

    def _parse_relations_for_subject(
        self, subject: str, indent: int, _line_no: int
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
            unquoted_obj = _unquote(parts[1])
            self._check_string_length(unquoted_obj, "Relation object")
            relations.append(
                Relation(subject, parts[0], unquoted_obj, object_quoted=_is_quoted(parts[1]))
            )
            self.index += 1
        return relations

    def _parse_rules(self, indent: int, _line_no: int) -> list[Rule]:
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
            try:
                tokens = _tokenize_rule(source)
                expr_ast, pos = _parse_rule_expression_node(tokens, 0)
                if pos < len(tokens):
                    raise ValueError("Extra tokens at end of rule expression")
                if not isinstance(expr_ast, Call):
                    raise ValueError("Rule expression must start with a parenthesized action call")
                rule_expr = _to_rule_expression(expr_ast)
            except Exception as exc:
                raise ParseError("SDIF_RULE_EXPR", f"invalid rule expression: {exc}", row_no) from exc
            rules.append(Rule(source, rule_expr))
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
                content_str = "\n".join(content)
                self._check_string_length(content_str, "Narrative content")
                return Narrative(key, content_str)
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


def _ensure_scalar_quote_closed(value: str, line_no: int) -> None:
    if not value.startswith('"'):
        return
    escaped = False
    for idx, char in enumerate(value[1:], start=2):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            if idx != len(value):
                raise ParseError(
                    "SDIF_STRING_TRAILING",
                    "quoted scalar field has trailing content after closing quote",
                    line_no,
                    idx + 1,
                )
            return
    raise ParseError("SDIF_STRING_UNCLOSED", "unterminated quoted scalar field", line_no, len(value) + 1)


def _unquote(value: str) -> str:
    if _is_quoted(value):
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    return value


def _split_quoted_whitespace(source: str, line_no: int, error_code: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_quote = False
    escaped = False
    for _column, char in enumerate(source, start=1):
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


def _tokenize_rule(source: str) -> list[str]:
    tokens = []
    i = 0
    while i < len(source):
        if source[i].isspace():
            i += 1
            continue
        if source[i] in "()":
            tokens.append(source[i])
            i += 1
            continue
        if source[i] == ",":
            tokens.append(source[i])
            i += 1
            continue
        if source[i] == '"':
            start = i
            i += 1
            escaped = False
            while i < len(source):
                if escaped:
                    escaped = False
                elif source[i] == "\\":
                    escaped = True
                elif source[i] == '"':
                    i += 1
                    break
                i += 1
            tokens.append(source[start:i])
            continue
        start = i
        while i < len(source) and (source[i].isalnum() or source[i] in "_-./:[]"):
            i += 1
        if i > start:
            tokens.append(source[start:i])
        else:
            tokens.append(source[i])
            i += 1
    return tokens


def _parse_rule_expression_node(tokens: list[str], pos: int) -> tuple[object, int]:
    if pos >= len(tokens):
        raise ValueError("Unexpected end of expression")

    token = tokens[pos]
    if token == "(":
        pos += 1
        if pos >= len(tokens):
            raise ValueError("Unterminated parenthesis")
        name = tokens[pos]
        if not (name.isalnum() or name in "_-./:[]"):
            raise ValueError(f"Expected identifier for call name, got `{name}`")
        pos += 1
        args = []
        while pos < len(tokens) and tokens[pos] != ")":
            arg, pos = _parse_rule_expression_node(tokens, pos)
            args.append(arg)
        if pos >= len(tokens) or tokens[pos] != ")":
            raise ValueError("Expected `)` to close call")
        pos += 1
        return Call(name, args), pos

    if pos + 1 < len(tokens) and tokens[pos + 1] == "(":
        name = token
        pos += 2
        args = []
        while pos < len(tokens) and tokens[pos] != ")":
            if tokens[pos] == ",":
                pos += 1
                continue
            arg, pos = _parse_rule_expression_node(tokens, pos)
            args.append(arg)
        if pos >= len(tokens) or tokens[pos] != ")":
            raise ValueError("Expected `)` to close compact call")
        pos += 1
        return Call(name, args), pos

    pos += 1
    if token.startswith('"') and token.endswith('"'):
        return _unquote(token), pos
    if token == "null":
        return None, pos
    if token == "true":
        return True, pos
    if token == "false":
        return False, pos
    if re.match(r"^[+-]?[0-9]+$", token):
        return int(token), pos
    if re.match(r"^[+-]?[0-9]+\.[0-9]+$", token):
        return float(token), pos
    return Identifier(token), pos


def _to_rule_expression(call: Call) -> RuleExpression:
    if call.name not in {"deny", "warn"}:
        raise ValueError(f"Invalid rule action: `{call.name}`. Must be `deny` or `warn`.")
    if not call.args:
        raise ValueError("Rule expression must have at least one function or argument")

    first = call.args[0]
    if isinstance(first, Call):
        return RuleExpression(action=call.name, function=first.name, args=first.args)
    elif isinstance(first, Identifier):
        return RuleExpression(action=call.name, function=first.name, args=call.args[1:])
    else:
        raise ValueError(f"Invalid rule function or first argument: `{first}`")


def parse_file(filepath: Path | str, *, policy: Policy | None = None) -> Document:
    policy = policy or Policy()
    seen_paths: list[Path] = []
    expanded_bytes = [0]

    def _resolve_include_directive(dir_args: list[str], parent_path: Path) -> Document:
        if not policy.allow_includes:
            raise PolicyError("SDIF_POLICY_INCLUDE", "Includes are disabled by policy")
        if not dir_args:
            raise PolicyError("SDIF_POLICY_INCLUDE", "Empty include directive")

        target_path_str = dir_args[0].strip('"')

        is_remote = target_path_str.startswith(("http://", "https://", "ftp://"))
        if is_remote:
            if not policy.allow_remote_includes:
                raise PolicyError(
                    "SDIF_POLICY_REMOTE_INCLUDE",
                    f"Remote include of {target_path_str} is disabled by policy",
                )
            raise PolicyError(
                "SDIF_POLICY_REMOTE_INCLUDE", f"Remote includes not supported: {target_path_str}"
            )

        target_path = Path(target_path_str)
        if target_path.is_absolute():
            resolved_target = target_path.resolve()
        else:
            resolved_target = (parent_path.parent / target_path).resolve()

        is_allowed = False
        for allowed in policy.allowed_include_paths:
            try:
                abs_allowed = allowed.resolve()
                if resolved_target == abs_allowed or abs_allowed in resolved_target.parents:
                    is_allowed = True
                    break
            except Exception:  # pragma: no cover
                pass  # pragma: no cover

        if not is_allowed:
            raise PolicyError(
                "SDIF_POLICY_INCLUDE_PATH",
                f"Include path {target_path_str} (resolved to {resolved_target}) is not permitted by policy allowlist",
            )

        return _parse_file_inner(resolved_target)

    def _parse_file_inner(current_path: Path) -> Document:
        abs_path = current_path.resolve()
        if abs_path in seen_paths:
            cycle_str = " -> ".join(str(p) for p in seen_paths) + f" -> {abs_path}"
            raise PolicyError("SDIF_POLICY_INCLUDE_CYCLE", f"Include cycle detected: {cycle_str}")

        if len(seen_paths) > policy.max_include_depth:
            raise PolicyError(
                "SDIF_POLICY_INCLUDE_DEPTH",
                f"Include depth {len(seen_paths)} exceeds maximum limit of {policy.max_include_depth}",
            )

        try:
            content = abs_path.read_text(encoding="utf-8")
        except Exception as e:
            raise OSError(f"Failed to read file {abs_path}: {e}") from e

        file_bytes = len(content.encode("utf-8"))
        expanded_bytes[0] += file_bytes
        if expanded_bytes[0] > policy.max_expanded_bytes:
            raise PolicyError(
                "SDIF_POLICY_EXPANDED_BYTES",
                f"Total expanded bytes {expanded_bytes[0]} exceeds limit of {policy.max_expanded_bytes}",
            )

        seen_paths.append(abs_path)
        try:
            doc = parse_text(content, policy=policy)

            resolved_directives: list[Directive] = []
            resolved_statements: list[Statement] = []

            for directive in doc.directives:
                if directive.name == "include":
                    included_doc = _resolve_include_directive(directive.args, abs_path)
                    resolved_statements.extend(included_doc.statements)
                    for d in included_doc.directives:
                        if d.name not in {"include", "sdif", "sdif.ai"}:
                            resolved_directives.append(d)
                else:
                    resolved_directives.append(directive)

            return Document(
                directives=resolved_directives, statements=resolved_statements + doc.statements
            )
        finally:
            seen_paths.pop()

    return _parse_file_inner(Path(filepath))
