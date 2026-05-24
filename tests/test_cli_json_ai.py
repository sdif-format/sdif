import json
import subprocess
import sys

from sdif import canonicalize, sdif_hash
from sdif.ai import ai_view, sdif_from_ai


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "sdif.cli", *args],
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )


def test_cli_to_json_from_json_and_ai_alias_projection(tmp_path):
    sdif = tmp_path / "doc.sdif"
    sdif.write_text(
        "@sdif 1.0\nkind Plan\nid demo\nmilestones[id,status]:\n  R1\tdone\n",
        encoding="utf-8",
    )

    json_run = run_cli("to-json", str(sdif))
    assert json.loads(json_run.stdout)["milestones"] == [{"id": "R1", "status": "done"}]

    source_json = tmp_path / "doc.json"
    source_json.write_text(
        json.dumps({"kind": "Plan", "id": "demo", "items": [{"id": "I1", "status": "open"}]}),
        encoding="utf-8",
    )
    from_json_run = run_cli("from-json", str(source_json))
    assert "items[id,status]:\n  I1\topen\n" in from_json_run.stdout

    ai_run = run_cli("ai", str(sdif), "--alias", "kind=k", "--alias", "status=st")
    assert ai_run.stdout.startswith("@sdif.ai 1.0\nalias[k=kind,st=status]\n")
    assert "k Plan\n" in ai_run.stdout
    assert "milestones[id,st]:\nR1\tdone\n" in ai_run.stdout


def test_ai_projection_omits_table_row_indent_for_token_density(tmp_path):
    source = tmp_path / "doc.sdif"
    source.write_text(
        "@sdif 1.0\nkind Plan\nitems[id,status]:\n  R1\tdone\n  R2\tpending\n",
        encoding="utf-8",
    )

    run = run_cli("ai", str(source))

    assert run.stdout == "@sdif.ai 1.0\nkind Plan\nitems[id,status]:\nR1\tdone\nR2\tpending\n"


def test_ai_projection_marks_string_columns_to_remove_repeated_scalar_quotes(tmp_path):
    source = tmp_path / "doc.sdif"
    source.write_text(
        '@sdif 1.0\nitems[id,value]:\n  I1\t"null"\n  I2\t"42"\n',
        encoding="utf-8",
    )

    run = run_cli("ai", str(source))

    assert run.stdout == "@sdif.ai 1.0\nitems[id,value$]:\nI1\tnull\nI2\t42\n"


def test_ai_projection_preserves_quoted_scalar_string_roundtrip():
    source = '@sdif 1.0\nvalue "null"\n'

    ai = ai_view(source, {})

    assert ai == '@sdif.ai 1.0\nvalue "null"\n'
    assert canonicalize(sdif_from_ai(ai)) == canonicalize(source)


def test_ai_projection_preserves_mixed_table_column_cell_types():
    source = '@sdif 1.0\nitems[id,value]:\n  A\t42\n  B\t"null"\n'

    ai = ai_view(source, {})

    assert ai == '@sdif.ai 1.0\nitems[id,value]:\nA\t42\nB\t"null"\n'
    assert canonicalize(sdif_from_ai(ai)) == canonicalize(source)


def test_ai_projection_preserves_subject_group_relation_quoted_object_spaces():
    source = '@sdif 1.0\nrel:\n  doc describes "hello world"\n'

    ai = ai_view(source, {})

    assert ai == '@sdif.ai 1.0\nrel[doc]:\n  describes "hello world"\n'
    assert canonicalize(sdif_from_ai(ai)) == canonicalize(source)


def test_cli_from_ai_expands_aliases_to_canonical_sdif(tmp_path):
    ai = tmp_path / "doc.sdif.ai"
    ai.write_text(
        "@sdif.ai 1.0\nalias[k=kind,st=status]\nk Plan\nid demo\nitems[id,st]:\nI1\topen\n",
        encoding="utf-8",
    )

    run = run_cli("from-ai", str(ai))

    assert run.stdout == "@sdif 1.0\nkind Plan\nid demo\nitems[id,status]:\n  I1\topen\n"


def test_cli_from_ai_restores_string_columns_marked_with_dollar(tmp_path):
    ai = tmp_path / "doc.sdif.ai"
    ai.write_text("@sdif.ai 1.0\nitems[id,value$]:\nI1\tnull\nI2\t42\n", encoding="utf-8")

    run = run_cli("from-ai", str(ai))

    assert run.stdout == '@sdif 1.0\nitems[id,value]:\n  I1\t"null"\n  I2\t"42"\n'


def test_fmt_on_sdif_ai_writes_canonical_source_sdif(tmp_path):
    ai = tmp_path / "doc.sdif.ai"
    ai.write_text(
        "@sdif.ai 1.0\nalias[k=kind,st=status]\nk Plan\nitems[id,st]:\nI1\tdone\n",
        encoding="utf-8",
    )

    run = run_cli("fmt", str(ai))

    assert run.stdout == f"Reformatted {ai}\n"
    assert ai.read_text(encoding="utf-8") == (
        "@sdif 1.0\nkind Plan\nitems[id,status]:\n  I1\tdone\n"
    )


def test_ai_projection_round_trips_to_canonical_source_sdif():
    source = '@sdif 1.0\nkind Plan\nid demo\nitems[id,status,value]:\n  I1\topen\t"null"\n'

    ai = ai_view(source, {"kind": "k", "status": "st"})

    assert canonicalize(sdif_from_ai(ai)) == canonicalize(source)


def test_ai_projection_preserves_canonical_hash_after_roundtrip():
    source = (
        "@sdif 1.0\n"
        "kind Plan\n"
        "id release.v2\n"
        "items[id,status,value]:\n"
        '  I1\topen\t"null"\n'
        "rel:\n"
        "  release.v2 depends_on release.v1\n"
        "  release.v2 validated_by validation.report.v2\n"
        "  release.v2 governed_by policy.v1\n"
    )
    aliases = {
        "kind": "k",
        "status": "st",
        "rel": "r",
        "depends_on": "dep",
        "validated_by": "vby",
        "governed_by": "gov",
    }

    assert sdif_hash(source) == sdif_hash(sdif_from_ai(ai_view(source, aliases)))


def test_ai_projection_groups_relations_by_subject_with_aliases(tmp_path):
    source = tmp_path / "doc.sdif"
    source.write_text(
        "@sdif 1.0\n"
        "id release.v2\n"
        "rel:\n"
        "  release.v2 depends_on release.v1\n"
        "  release.v2 validated_by validation.report.v2\n"
        "  release.v2 governed_by policy.v1\n",
        encoding="utf-8",
    )

    run = run_cli(
        "ai",
        str(source),
        "--alias",
        "rel=r",
        "--alias",
        "depends_on=dep",
        "--alias",
        "validated_by=vby",
        "--alias",
        "governed_by=gov",
    )

    assert run.stdout == (
        "@sdif.ai 1.0\n"
        "alias[dep=depends_on,gov=governed_by,r=rel,vby=validated_by]\n"
        "id release.v2\n"
        "r[release.v2]:\n"
        "  dep release.v1\n"
        "  vby validation.report.v2\n"
        "  gov policy.v1\n"
    )


def test_cli_from_ai_expands_subject_grouped_relations(tmp_path):
    ai = tmp_path / "doc.sdif.ai"
    ai.write_text(
        "@sdif.ai 1.0\n"
        "alias[dep=depends_on,gov=governed_by,r=rel,vby=validated_by]\n"
        "id release.v2\n"
        "r[release.v2]:\n"
        "  dep release.v1\n"
        "  vby validation.report.v2\n"
        "  gov policy.v1\n",
        encoding="utf-8",
    )

    run = run_cli("from-ai", str(ai))

    assert run.stdout == (
        "@sdif 1.0\n"
        "id release.v2\n"
        "rel:\n"
        "  release.v2 depends_on release.v1\n"
        "  release.v2 governed_by policy.v1\n"
        "  release.v2 validated_by validation.report.v2\n"
    )


def test_source_sdif_rejects_subject_grouped_relations():
    from sdif.parser import ParseError, parse_text

    try:
        parse_text("@sdif 1.0\nrel[release.v2]:\n  depends_on release.v1\n")
    except ParseError as exc:
        assert exc.code == "SDIF_AI_REL_SUBJECT"
    else:  # pragma: no cover - defensive assertion message
        raise AssertionError("source SDIF must not accept rel[subject]: syntax")


def test_alias_projection_filtering_collision_and_keys():
    source = (
        "@sdif 1.0\n"
        "api_name compact-service-api\n"
        "endpoints[id,method,path,tag,auth]:\n"
        "  END-001\tPOST\t/v1/resources/1\tbilling\tuser\n"
    )
    aliases = {
        "authority": "auth",
        "description": "desc",
        "version": "v",
    }
    ai = ai_view(source, aliases)
    assert "alias[" not in ai
    assert "endpoints[id,method,path,tag,auth]:" in ai

    source2 = (
        "@sdif 1.0\n"
        "authority compact-service-api\n"
    )
    ai2 = ai_view(source2, aliases)
    assert "alias[auth=authority]" in ai2
    assert "auth compact-service-api" in ai2

    source3 = (
        "@sdif 1.0\n"
        "authority compact-service-api\n"
        "auth oauth\n"
    )
    ai3 = ai_view(source3, aliases)
    assert "alias[" not in ai3
    assert "authority compact-service-api" in ai3
    assert "auth oauth" in ai3

