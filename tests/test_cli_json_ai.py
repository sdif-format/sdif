import json
import subprocess
import sys


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/sdif-cli.py", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def test_cli_to_json_from_json_and_ai_alias_projection(tmp_path):
    sdif = tmp_path / "doc.sdif"
    sdif.write_text(
        "@sdif 0.1\nkind Plan\nid demo\nmilestones[id,status]:\n  R1\tdone\n",
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
    assert ai_run.stdout.startswith("@sdif.ai 0.1\nalias[k=kind,st=status]\n")
    assert "k Plan\n" in ai_run.stdout
    assert "milestones[id,st]:\nR1\tdone\n" in ai_run.stdout


def test_ai_projection_omits_table_row_indent_for_token_density(tmp_path):
    source = tmp_path / "doc.sdif"
    source.write_text(
        "@sdif 0.1\nkind Plan\nitems[id,status]:\n  R1\tdone\n  R2\tpending\n",
        encoding="utf-8",
    )

    run = run_cli("ai", str(source))

    assert run.stdout == "@sdif.ai 0.1\nkind Plan\nitems[id,status]:\nR1\tdone\nR2\tpending\n"


def test_ai_projection_marks_string_columns_to_remove_repeated_scalar_quotes(tmp_path):
    source = tmp_path / "doc.sdif"
    source.write_text(
        '@sdif 0.1\nitems[id,value]:\n  I1\t"null"\n  I2\t"42"\n',
        encoding="utf-8",
    )

    run = run_cli("ai", str(source))

    assert run.stdout == "@sdif.ai 0.1\nitems[id,value$]:\nI1\tnull\nI2\t42\n"
