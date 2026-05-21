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

    row_comment = invalid_dir / "table_row_comment.sdif"
    with pytest.raises(ParseError) as excinfo:
        parse_text(row_comment.read_text(encoding="utf-8"))
    assert excinfo.value.code == "SDIF_TABLE_ROW_COMMENT"

    # Policy fixtures:
    from sdif import Policy, PolicyError, parse_file

    allowed_policy = Policy(
        allow_includes=True, allowed_include_paths=frozenset([Path("conformance")])
    )
    doc = parse_file(valid_dir / "policy_allowed_include.sdif", policy=allowed_policy)
    assert doc.fields["included_field"].value == "included_value"

    cycle_policy = Policy(
        allow_includes=True, allowed_include_paths=frozenset([Path("conformance")])
    )
    with pytest.raises(PolicyError) as excinfo:
        parse_file(invalid_dir / "include_cycle.sdif", policy=cycle_policy)
    assert excinfo.value.code == "SDIF_POLICY_INCLUDE_CYCLE"

    with pytest.raises(PolicyError) as excinfo:
        parse_file(invalid_dir / "policy_nesting_depth.sdif")
    assert excinfo.value.code == "SDIF_POLICY_NESTING_DEPTH"

    # Alias policy checks:
    with pytest.raises(PolicyError) as excinfo:
        parse_text((invalid_dir / "alias_collision.sdif").read_text(encoding="utf-8"))
    assert excinfo.value.code == "SDIF_POLICY_ALIAS_COLLISION"

    with pytest.raises(PolicyError) as excinfo:
        parse_text((invalid_dir / "alias_reserved.sdif").read_text(encoding="utf-8"))
    assert excinfo.value.code == "SDIF_POLICY_ALIAS_RESERVED"
