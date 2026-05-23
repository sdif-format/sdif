from dataclasses import dataclass, field
from pathlib import Path

RESERVED_TERMS = frozenset({"include", "alias"})


class PolicyError(Exception):
    """Raised when a security policy is violated."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Policy:
    allow_includes: bool = False
    allowed_include_paths: frozenset[Path] = field(default_factory=frozenset)
    allow_remote_includes: bool = False
    allow_remote_schemas: bool = False
    max_document_size: int = 1_000_000  # 1MB
    max_nesting_depth: int = 16
    max_string_length: int = 65536  # 64KB
    max_table_row_count: int = 10000
    max_include_depth: int = 5
    max_expanded_bytes: int = 2_000_000  # 2MB
    max_alias_expansion: int = 500
