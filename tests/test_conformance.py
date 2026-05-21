import subprocess
import sys
from pathlib import Path

from sdif import parse_text


def test_conformance_manifest_is_sdif_and_lists_portable_core_agent_case():
    manifest = Path("conformance/manifest.sdif")
    doc = parse_text(manifest.read_text(encoding="utf-8"))

    assert doc.fields["kind"].value == "ConformanceManifest"
    cases = doc.tables["cases"]
    assert cases.columns == ["id", "profile", "source", "canonical", "tree", "sha256"]
    assert any(row[0] == "core-agent" for row in cases.rows)


def test_conformance_checker_passes_for_python_and_tree_sitter_shared_fixtures():
    run = subprocess.run(
        [sys.executable, "scripts/check_conformance_fixtures.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0, run.stderr
    assert "conformance fixtures OK" in run.stdout


def test_conformance_valid_invalid_fixtures():
    import pytest
    from sdif.parser import ParseError

    # Valid fixtures must parse successfully
    valid_dir = Path("conformance/valid")
    for path in sorted(valid_dir.glob("*.sdif")):
        parse_text(path.read_text(encoding="utf-8"))

    # Invalid fixtures must raise specific ParseErrors
    invalid_dir = Path("conformance/invalid")

    bad_close = invalid_dir / "nested_narrative_bad_close.sdif"
    with pytest.raises(ParseError) as excinfo:
        parse_text(bad_close.read_text(encoding="utf-8"))
    assert excinfo.value.code == "SDIF_NARRATIVE_CLOSE_ALIGN"

    too_few = invalid_dir / "table_too_few_cells.sdif"
    with pytest.raises(ParseError) as excinfo:
        parse_text(too_few.read_text(encoding="utf-8"))
    assert excinfo.value.code == "SDIF_TABLE_ARITY"

    too_many = invalid_dir / "table_too_many_cells.sdif"
    with pytest.raises(ParseError) as excinfo:
        parse_text(too_many.read_text(encoding="utf-8"))
    assert excinfo.value.code == "SDIF_TABLE_ARITY"
