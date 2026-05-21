"""Line-oriented lexer for the SDIF MVP parser."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenKind(str, Enum):
    COMMENT = "comment"
    DIRECTIVE = "directive"
    FIELD = "field"
    BLOCK = "block"
    TABLE_HEADER = "table_header"
    TABLE_ROW = "table_row"


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: str
    line: int
    column: int
    indent: int


def lex_lines(text: str) -> list[Token]:
    tokens: list[Token] = []
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for line_no, raw in enumerate(lines, start=1):
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        body = raw[indent:]
        if body.startswith("#"):
            kind = TokenKind.COMMENT
        elif body.startswith("@"):
            kind = TokenKind.DIRECTIVE
        elif "\t" in body:
            kind = TokenKind.TABLE_ROW
        elif _looks_like_table_header(body):
            kind = TokenKind.TABLE_HEADER
        elif body.endswith(":"):
            kind = TokenKind.BLOCK
        else:
            kind = TokenKind.FIELD
        tokens.append(Token(kind=kind, value=body, line=line_no, column=indent + 1, indent=indent))
    return tokens


def _looks_like_table_header(body: str) -> bool:
    return body.endswith(":") and "[" in body and "]" in body and body.index("[") < body.index("]")
