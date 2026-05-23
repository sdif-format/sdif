import re

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]
from pathlib import Path


def test_ci_and_docs_artifacts_exist():
    assert Path(".github/workflows/ci.yml").is_file()
    docs = Path("docs/spec.md").read_text(encoding="utf-8")
    assert "Minimum normative AST" in docs
    assert "Canonicalization" in docs
    assert "CLI" in docs


def test_spec_version_matches_package_version():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    spec = Path("docs/spec.md").read_text(encoding="utf-8")
    match = re.search(
        r"^\*\*Version:\*\*\s+([0-9]+\.[0-9]+\.[0-9]+)$", spec, re.MULTILINE
    )

    assert match is not None
    assert match.group(1) == pyproject["project"]["version"]


def test_normative_docs_table_examples_use_literal_htab_rows():
    for path in (
        Path("docs/spec.md"),
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


def test_spec_records_v1_m1_normative_decisions():
    spec = Path("docs/spec.md").read_text(encoding="utf-8")

    for term in (
        "`@sdif 1.0` identifies the stable core syntax and semantic contract.",
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


def test_public_release_metadata_has_no_draft_or_alpha_contradictions():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    public_docs = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in ("README.md", "docs/spec.md", "docs/canonicalization.md")
    ).lower()

    assert "Development Status :: 5 - Production/Stable" in pyproject["project"]["classifiers"]
    for forbidden in (
        "still a draft",
        "specification draft",
        "open question",
        "open decision",
        "mvp",
        "alpha",
        "sha256:todo",
    ):
        assert forbidden not in public_docs


def test_release_process_uses_git_archive_and_documents_required_gates():
    makefile = Path("Makefile").read_text(encoding="utf-8")
    release_docs = Path("docs/release-process.md").read_text(encoding="utf-8")
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")

    assert "git archive --format=tar.gz --output=dist/sdif.tar.gz HEAD" in makefile
    assert "mkdir -p dist" in makefile
    for forbidden in ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv"):
        assert forbidden in release_docs
    for gate in (
        "scripts/check_conformance_fixtures.py",
        "python3 -m compileall -q src scripts tests tools",
        "python3 -m pytest -q",
    ):
        assert gate in release_docs
    for external_gate in (
        "sdif-benchmarks",
        "tree-sitter-sdif",
    ):
        assert external_gate in release_docs
    assert "## 1.0.0 - 2026-05-22" in changelog
    assert "@sdif 1.0" in changelog


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


def test_ai_speed_profile_documents_llm_latency_contract() -> None:
    docs = Path("docs/ai-speed-profile.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    for term in (
        "SDIF AI speed profile",
        "prefill",
        "locality",
        "summary.sdif.ai",
        "chunk manifest",
        "canonical hash",
        "delta",
        "useful_answer_ms",
        "aliases must remain semantic",
    ):
        assert term in docs

    assert "docs/ai-speed-profile.md" in readme
