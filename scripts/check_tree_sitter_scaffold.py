#!/usr/bin/env python3
"""Validate the SDIF Tree-sitter scaffold without requiring the Tree-sitter CLI.

This is a lightweight repository guard. It does not replace `tree-sitter test`,
but it catches stale package metadata, missing corpus/query files, and fixture
node names that no longer exist in `grammar.js`.
"""

from __future__ import annotations

import json
import re
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREE_SITTER_DIR = ROOT / "tree-sitter-sdif"


def main() -> int:
    errors: list[str] = []

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    package = _load_json(TREE_SITTER_DIR / "package.json", errors)
    config = _load_json(TREE_SITTER_DIR / "tree-sitter.json", errors)
    grammar = _read(TREE_SITTER_DIR / "grammar.js", errors)
    corpus = _read(TREE_SITTER_DIR / "test/corpus/core.txt", errors)
    highlights = _read(TREE_SITTER_DIR / "queries/highlights.scm", errors)

    if errors:
        return _fail(errors)

    project_version = pyproject["project"]["version"]
    _expect(
        package.get("version") == project_version,
        errors,
        "package.json version must match pyproject",
    )
    _expect(
        config.get("metadata", {}).get("version") == project_version,
        errors,
        "tree-sitter.json metadata version must match pyproject",
    )
    grammar_entry = config.get("grammars", [{}])[0]
    _expect(
        grammar_entry.get("scope") == "source.sdif", errors, "tree-sitter scope must be source.sdif"
    )
    _expect(
        "sdif" in grammar_entry.get("file-types", []),
        errors,
        "tree-sitter file type must include sdif",
    )
    _expect(
        "sdif.ai" in grammar_entry.get("file-types", []),
        errors,
        "tree-sitter file type must include sdif.ai",
    )
    _expect(
        grammar_entry.get("injection-regex") == r"^sdif(\.ai)?$",
        errors,
        "tree-sitter injection-regex must include sdif and sdif.ai",
    )
    package_entry = package.get("tree-sitter", [{}])[0]
    _expect(
        "sdif" in package_entry.get("file-types", []),
        errors,
        "package file types must include sdif",
    )
    _expect(
        "sdif.ai" in package_entry.get("file-types", []),
        errors,
        "package file types must include sdif.ai",
    )

    grammar_nodes = _grammar_rule_names(grammar)
    _expect("source_file" in grammar_nodes, errors, "grammar must declare source_file")
    _expect("JSON" not in corpus, errors, "agent-facing corpus should avoid JSON as working format")
    _expect("@sdif.ai 0.1" in corpus, errors, "corpus must cover the sdif.ai directive")
    _expect("alias[k=kind,st=status]" in corpus, errors, "corpus must cover sdif.ai alias headers")
    _expect(
        "checks[id,value$]:" in corpus, errors, "corpus must cover sdif.ai string-preserved columns"
    )
    _expect("C1\tnull" in corpus, errors, "corpus must cover compact sdif.ai table rows with HTAB")
    _expect("alias_header" in grammar_nodes, errors, "grammar must declare alias_header")
    _expect("alias_entry" in grammar_nodes, errors, "grammar must declare alias_entry")
    _expect("(column) @property" in highlights, errors, "highlights must tag table columns")
    _expect("(alias_entry) @property" in highlights, errors, "highlights must tag alias entries")

    corpus_nodes = _corpus_expected_nodes(corpus)
    missing_corpus_nodes = sorted(corpus_nodes - grammar_nodes)
    _expect(
        not missing_corpus_nodes,
        errors,
        f"corpus references undeclared grammar nodes: {', '.join(missing_corpus_nodes)}",
    )

    query_nodes = _query_node_names(highlights)
    missing_query_nodes = sorted(query_nodes - grammar_nodes)
    _expect(
        not missing_query_nodes,
        errors,
        f"highlight queries reference undeclared grammar nodes: {', '.join(missing_query_nodes)}",
    )

    if errors:
        return _fail(errors)

    print("tree-sitter-sdif scaffold OK")
    return 0


def _load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return {}


def _read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
    return ""


def _grammar_rule_names(grammar: str) -> set[str]:
    return set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[$_]\s*=>", grammar, re.MULTILINE))


def _corpus_expected_nodes(corpus: str) -> set[str]:
    _, _, expected = corpus.partition("---")
    return set(re.findall(r"\(([A-Za-z_][A-Za-z0-9_]*)", expected))


def _query_node_names(highlights: str) -> set[str]:
    names: set[str] = set()
    for line in highlights.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(";") or stripped.startswith('"'):
            continue
        for node in re.findall(r"\(([A-Za-z_][A-Za-z0-9_]*)", stripped):
            names.add(node)
    return names


def _expect(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def _fail(errors: list[str]) -> int:
    for error in errors:
        print(f"tree-sitter scaffold error: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
