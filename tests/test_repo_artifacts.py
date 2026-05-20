from pathlib import Path


def test_ci_tree_sitter_and_docs_artifacts_exist():
    assert Path(".github/workflows/ci.yml").is_file()
    assert Path("tree-sitter-sdif/grammar.js").is_file()
    docs = Path("docs/spec.md").read_text(encoding="utf-8")
    assert "Minimum normative AST" in docs
    assert "Canonicalization" in docs
    assert "CLI" in docs


def test_normative_docs_table_examples_use_literal_htab_rows():
    for path in (Path("docs/spec.md"), Path("docs/sdif_v0.1.md"), Path("README.md"), Path("docs/comparison.md")):
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
