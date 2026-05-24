import os
import subprocess
import sys
from pathlib import Path

from sdif import parse_text

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "conformance").is_dir():
    CONF_ROOT = ROOT
else:
    CONF_ROOT = Path(os.environ.get("SDIF_SPEC_REPO") or ROOT.parent / "sdif-spec").expanduser().resolve()

CONF_DIR = CONF_ROOT / "conformance"


def test_conformance_manifest_is_sdif_and_lists_portable_core_agent_case():
    manifest = CONF_DIR / "manifest.sdif"
    doc = parse_text(manifest.read_text(encoding="utf-8"))

    assert doc.fields["kind"].value == "ConformanceManifest"
    cases = doc.tables["cases"]
    assert cases.columns == ["id", "profile", "source", "canonical", "tree", "sha256"]
    assert any(row[0] == "core-agent" for row in cases.rows)


def test_conformance_checker_passes_for_python_and_tree_sitter_shared_fixtures():
    run = subprocess.run(
        [sys.executable, "scripts/check_conformance_fixtures.py"],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 0, run.stderr
    assert "conformance fixtures OK" in run.stdout


def test_conformance_valid_invalid_fixtures():
    import pytest
    from sdif.parser import ParseError

    # Valid fixtures must parse successfully
    valid_dir = CONF_DIR / "valid"
    for path in sorted(valid_dir.glob("*.sdif")):
        parse_text(path.read_text(encoding="utf-8"))

    # Invalid fixtures must raise specific ParseErrors
    invalid_dir = CONF_DIR / "invalid"

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

    for fixture_name, code in (
        ("version_missing.sdif", "SDIF_VERSION_MISSING"),
        ("version_unsupported.sdif", "SDIF_VERSION_UNSUPPORTED"),
        ("version_bad_token.sdif", "SDIF_VERSION_UNSUPPORTED"),
        ("directive_unknown.sdif", "SDIF_DIRECTIVE_UNKNOWN"),
        ("source_grouped_relation.sdif", "SDIF_AI_REL_SUBJECT"),
    ):
        with pytest.raises(ParseError) as excinfo:
            parse_text((invalid_dir / fixture_name).read_text(encoding="utf-8"))
        assert excinfo.value.code == code

    # Policy fixtures:
    from sdif import Policy, PolicyError, parse_file

    allowed_policy = Policy(
        allow_includes=True, allowed_include_paths=frozenset([CONF_DIR])
    )
    doc = parse_file(valid_dir / "policy_allowed_include.sdif", policy=allowed_policy)
    assert doc.fields["included_field"].value == "included_value"

    cycle_policy = Policy(
        allow_includes=True, allowed_include_paths=frozenset([CONF_DIR])
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
