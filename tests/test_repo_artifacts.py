import json
import re

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]
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

    tree_sitter_package = json.loads(
        Path("tree-sitter-sdif/package.json").read_text(encoding="utf-8")
    )
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

    script = Path("scripts/check_tree_sitter_scaffold.py").read_text(encoding="utf-8")
    assert "sdif.ai" in script
    assert "injection-regex" in script
    assert "checks[id,value$]:" in script
    assert "(column) @property" in script

    run = subprocess.run(
        [sys.executable, "scripts/check_tree_sitter_scaffold.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0, run.stderr
    assert "tree-sitter-sdif scaffold OK" in run.stdout


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


def test_benchmark_golden_corpus_has_representative_size_and_complexity_mix():
    golden_root = Path("examples/golden")
    fixture_paths = sorted(golden_root.glob("*/equivalent.json"))
    fixture_names = {path.parent.name for path in fixture_paths}
    sizes = {path.parent.name: path.stat().st_size for path in fixture_paths}

    small = [name for name, size in sizes.items() if size < 20 * 1024]
    medium = [name for name, size in sizes.items() if 20 * 1024 <= size <= 200 * 1024]
    large = [name for name, size in sizes.items() if size > 200 * 1024]

    assert len(fixture_paths) >= 18
    assert len(small) >= 4
    assert len(medium) >= 4
    assert len(large) >= 4
    assert "github.openapi" in fixture_names

    for required in (
        "wide-table-survey",
        "deep-hierarchy-project",
        "medium-observability-run",
        "large-audit-trail",
    ):
        assert required in fixture_names


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

    assert "scripts/token_comparison.py" in docs
    assert "token" in docs.lower()
    assert "sdif validate examples/plan.sdif --schema examples/schema.sdif" in docs


def test_spec_records_v1_m1_normative_decisions():
    spec = Path("docs/spec.md").read_text(encoding="utf-8")

    for term in (
        "`@sdif 1.0` will identify the first stable core syntax and semantic contract.",
        "The package version may advance independently from the document format version.",
        "Core v1 behavior includes parsing, the normative AST, schema-driven validation, canonical-syntax-v1, safe default policies, and `.sdif.ai` reversibility.",
        "Versioned extensions include remote includes, remote schemas, complex namespaces, deep graph validation, digital signatures, advanced type unions, and non-declarative rule execution.",
        "For the v1.0 stabilization track, strict mode prohibits inline comments inside table rows.",
        "Table cells are captured as raw strings in the initial AST.",
        "Schema-driven typing is applied during validation or normalization, not during raw parsing.",
        "The `$` suffix is a decoding hint only and is not part of the semantic column name.",
        "The v1 namespace form is `@namespace prefix iri`.",
        "Complex namespace behavior is a versioned extension.",
        "RuleExpression(action, function, args)",
        "`@include` is disabled by default",
        "Remote includes and remote schemas remain disabled unless an explicit policy enables them.",
    ):
        assert term in spec


def test_canonicalization_doc_records_m2_table_order_contract():
    docs = Path("docs/canonicalization.md").read_text(encoding="utf-8")

    for term in (
        "canonical-syntax-v1",
        "Without a schema, table row order is preserved.",
        "With a schema and `ordered=true`, table row order is preserved.",
        "With a schema, `ordered=false`, and a declared `primary_key`, rows are sorted by primary-key value.",
        "With a schema and `ordered=false` but no declared `primary_key`, strict canonicalization reports a canonicalization error rather than guessing semantic order.",
    ):
        assert term in docs


def test_spec_records_v1_m3_validation_contract():
    spec = Path("docs/spec.md").read_text(encoding="utf-8")

    for term in (
        "fields[name,type,required,default]:",
        "tables[name,ordered,primary_key]:",
        "columns[table,name,type,required]:",
        "relations[predicate,subject_type,object_type,required]:",
        "rule_functions[name,min_args,max_args]:",
        "* Required fields.",
        "* Types.",
        "* Enumerations.",
        "* Allowed tables.",
        "* Required columns.",
        "* Allowed relation predicates.",
        "* Allowed rule functions.",
    ):
        assert term in spec


def test_comparison_doc_includes_examples_for_all_compared_formats():
    docs = Path("docs/comparison.md").read_text(encoding="utf-8")

    for fence in ("```json", "```yaml", "```toon", "```sdif"):
        assert fence in docs
    assert "TOON" in docs
    assert "milestones[" in docs
