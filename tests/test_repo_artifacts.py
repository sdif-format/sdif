import json
import re
import tomllib
from pathlib import Path


def test_ci_tree_sitter_and_docs_artifacts_exist():
    assert Path(".github/workflows/ci.yml").is_file()
    assert Path("tree-sitter-sdif/grammar.js").is_file()
    docs = Path("docs/spec.md").read_text(encoding="utf-8")
    assert "Minimum normative AST" in docs
    assert "Canonicalization" in docs
    assert "CLI" in docs


def test_spec_version_matches_package_version():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    spec = Path("docs/spec.md").read_text(encoding="utf-8")
    match = re.search(r"^\*\*Version:\*\*\s+([0-9]+\.[0-9]+\.[0-9]+)-draft$", spec, re.MULTILINE)

    assert match is not None
    assert match.group(1) == pyproject["project"]["version"]

    tree_sitter_package = json.loads(Path("tree-sitter-sdif/package.json").read_text(encoding="utf-8"))
    assert tree_sitter_package["version"] == pyproject["project"]["version"]


def test_tree_sitter_metadata_recognizes_sdif_ai_files():
    package = json.loads(Path("tree-sitter-sdif/package.json").read_text(encoding="utf-8"))
    config = json.loads(Path("tree-sitter-sdif/tree-sitter.json").read_text(encoding="utf-8"))

    package_file_types = package["tree-sitter"][0]["file-types"]
    config_file_types = config["grammars"][0]["file-types"]

    assert "sdif" in package_file_types
    assert "sdif.ai" in package_file_types
    assert "sdif" in config_file_types
    assert "sdif.ai" in config_file_types
    assert config["grammars"][0]["injection-regex"] == "^sdif(\\.ai)?$"

def test_tree_sitter_tooling_has_package_corpus_and_highlight_queries():
    package = Path("tree-sitter-sdif/package.json").read_text(encoding="utf-8")
    config = Path("tree-sitter-sdif/tree-sitter.json").read_text(encoding="utf-8")
    corpus = Path("tree-sitter-sdif/test/corpus/core.txt").read_text(encoding="utf-8")
    highlights = Path("tree-sitter-sdif/queries/highlights.scm").read_text(encoding="utf-8")

    assert '"name": "tree-sitter-sdif"' in package
    assert '"scope": "source.sdif"' in config
    assert "@sdif 0.1" in corpus
    assert "milestones[id,status,gate]:" in corpus
    assert "(directive" in highlights
    assert "(table_header" in highlights


def test_tree_sitter_scaffold_checker_passes():
    import subprocess
    import sys

    run = subprocess.run(
        [sys.executable, "scripts/check_tree_sitter_scaffold.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0, run.stderr
    assert "tree-sitter-sdif scaffold OK" in run.stdout


def test_tree_sitter_corpus_covers_compact_sdif_ai_tables():
    corpus = Path("tree-sitter-sdif/test/corpus/core.txt").read_text(encoding="utf-8")
    highlights = Path("tree-sitter-sdif/queries/highlights.scm").read_text(encoding="utf-8")

    assert "@sdif.ai 0.1" in corpus
    assert "checks[id,value$]:" in corpus
    assert "C1\tnull" in corpus
    assert "(column" in corpus
    assert "(column) @property" in highlights

def test_tree_sitter_grammar_names_core_syntax_nodes_for_highlighting():
    grammar = Path("tree-sitter-sdif/grammar.js").read_text(encoding="utf-8")

    for node in (
        "table_header",
        "table_row",
        "relation_block",
        "relation_row",
        "rules_block",
        "rule_row",
        "narrative_block",
    ):
        assert f"{node}:" in grammar


def test_normative_docs_table_examples_use_literal_htab_rows():
    for path in (
        Path("docs/spec.md"),
        Path("docs/sdif_v0.1.md"),
        Path("README.md"),
        Path("docs/comparison.md"),
    ):
        _assert_sdif_table_rows_use_htab(path)


def _assert_sdif_table_rows_use_htab(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    in_sdif_block = False
    active_table_columns: int | None = None
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line == "```sdif":
            in_sdif_block = True
            active_table_columns = None
            continue
        if in_sdif_block and line == "```":
            in_sdif_block = False
            active_table_columns = None
            continue
        if not in_sdif_block:
            continue
        stripped = line.strip()
        if not stripped:
            active_table_columns = None
            continue
        if not line.startswith(" ") and "[" in line and stripped.endswith(":"):
            header = stripped[stripped.index("[") + 1 : stripped.index("]")]
            active_table_columns = len([column for column in header.split(",") if column.strip()])
            continue
        if not line.startswith("  ") or stripped.endswith(":"):
            active_table_columns = None
            continue
        if active_table_columns is not None and active_table_columns > 1:
            assert "\t" in line, f"{path}:{line_no} table row must use literal HTAB separators"


def test_docs_examples_describe_current_golden_fixture_policy():
    docs = Path("docs/examples/README.md").read_text(encoding="utf-8")

    assert "equivalent.json" in docs
    assert "source.sdif" in docs
    assert "canonical.sdif" in docs
    assert "canonical.sha256" in docs
    assert "equivalent.yaml" not in docs
    assert "equivalent.toon" not in docs
    assert "JSON is the semantic source" in docs


def test_versioned_spec_is_pointer_to_authoritative_spec():
    legacy = Path("docs/sdif_v0.1.md").read_text(encoding="utf-8")
    spec = Path("docs/spec.md").read_text(encoding="utf-8")

    assert "docs/spec.md" in legacy
    assert "authoritative" in legacy.lower()
    assert len(legacy) < len(spec) // 10


def test_semantic_quality_methodology_is_documented_separately_from_token_benchmark():
    docs = Path("docs/semantic-quality.md").read_text(encoding="utf-8")

    for term in (
        "relational expressivity",
        "round-trip fidelity",
        "schema validation",
        "SDIF AI",
        "canonicalization",
    ):
        assert term in docs

    assert "benchmarks/token_comparison.py" in docs
    assert "token" in docs.lower()
    assert "sdif validate examples/plan.sdif --schema examples/schema.sdif" in docs

def test_comparison_doc_includes_examples_for_all_compared_formats():
    docs = Path("docs/comparison.md").read_text(encoding="utf-8")

    for fence in ("```json", "```yaml", "```toon", "```sdif"):
        assert fence in docs
    assert "TOON" in docs
    assert "milestones[" in docs
