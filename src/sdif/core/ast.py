"""Core AST nodes for the SDIF v1 parser."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Directive:
    name: str
    args: list[str]


@dataclass(frozen=True)
class Field:
    key: str
    value: str
    quoted: bool = False


@dataclass(frozen=True)
class ObjectBlock:
    key: str
    statements: list[object] = field(default_factory=list)

    @property
    def fields(self) -> dict[str, Field]:
        return {s.key: s for s in self.statements if isinstance(s, Field)}

    @property
    def objects(self) -> dict[str, ObjectBlock]:
        return {s.key: s for s in self.statements if isinstance(s, ObjectBlock)}

    @property
    def tables(self) -> dict[str, Table]:
        return {s.name: s for s in self.statements if isinstance(s, Table)}

    @property
    def relations(self) -> list[Relation]:
        return [s for s in self.statements if isinstance(s, Relation)]

    @property
    def rules(self) -> list[Rule]:
        return [s for s in self.statements if isinstance(s, Rule)]

    @property
    def narratives(self) -> dict[str, Narrative]:
        return {s.key: s for s in self.statements if isinstance(s, Narrative)}


@dataclass(frozen=True)
class Table:
    name: str
    columns: list[str]
    rows: list[list[str]]
    quoted_columns: frozenset[int] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Relation:
    subject: str
    predicate: str
    object: str
    object_quoted: bool = False


@dataclass(frozen=True)
class Identifier:
    name: str


@dataclass(frozen=True)
class Call:
    name: str
    args: list[object] = field(default_factory=list)


@dataclass(frozen=True)
class RuleExpression:
    action: str
    function: str
    args: list[object] = field(default_factory=list)


@dataclass(frozen=True)
class Rule:
    source: str
    expression: RuleExpression | None = None


@dataclass(frozen=True)
class Narrative:
    key: str
    text: str


Statement = Field | ObjectBlock | Table | Relation | Rule | Narrative


@dataclass(frozen=True)
class Document:
    directives: list[Directive] = field(default_factory=list)
    statements: list[Statement] = field(default_factory=list)

    @property
    def fields(self) -> dict[str, Field]:
        return {s.key: s for s in self.statements if isinstance(s, Field)}

    @property
    def objects(self) -> dict[str, ObjectBlock]:
        return {s.key: s for s in self.statements if isinstance(s, ObjectBlock)}

    @property
    def tables(self) -> dict[str, Table]:
        return {s.name: s for s in self.statements if isinstance(s, Table)}

    @property
    def relations(self) -> list[Relation]:
        return [s for s in self.statements if isinstance(s, Relation)]

    @property
    def rules(self) -> list[Rule]:
        return [s for s in self.statements if isinstance(s, Rule)]

    @property
    def narratives(self) -> dict[str, Narrative]:
        return {s.key: s for s in self.statements if isinstance(s, Narrative)}


def statement_count(statements: Iterable[Statement]) -> int:
    return sum(1 for _ in statements)
