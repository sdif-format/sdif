import json
import subprocess
import sys


def test_cli_validate_outputs_structured_diagnostics_json(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text(
        """
@sdif 0.1
kind Schema
fields[name,type,required,default]:
  kind\tIdentifier\ttrue\tnull
  id\tIdentifier\ttrue\tnull
  status\tEnum(open,closed)\ttrue\topen
rule_functions[name,min_args,max_args]:
  deny\t1\t1
  missing\t1\t1
""".strip()
        + "\n",
        encoding="utf-8",
    )
    doc = tmp_path / "doc.sdif"
    doc.write_text(
        """
@sdif 0.1
kind Plan
status blocked
rules:
  (allow missing(evidence))
""".strip()
        + "\n",
        encoding="utf-8",
    )

    run = subprocess.run(
        [
            sys.executable,
            "tools/sdif-cli.py",
            "validate",
            str(doc),
            "--schema",
            str(schema),
            "--json",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 1
    payload = json.loads(run.stdout)
    assert payload["valid"] is False
    assert [(d["code"], d["path"]) for d in payload["diagnostics"]] == [
        ("SDIF_REQUIRED_FIELD", "id"),
        ("SDIF_ENUM", "status"),
        ("SDIF_RULE_FUNCTION", "rules[0]"),
    ]


def test_cli_validate_returns_zero_for_valid_document(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text(
        """
@sdif 0.1
kind Schema
fields[name,type,required,default]:
  kind\tIdentifier\ttrue\tnull
  id\tIdentifier\ttrue\tnull
""".strip()
        + "\n",
        encoding="utf-8",
    )
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 0.1\nkind Plan\nid demo\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--schema", str(schema)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0
    assert run.stdout.strip() == "valid"


def test_cli_validate_json_reports_parse_errors_as_structured_diagnostics(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text("@sdif 0.1\nkind Schema\n", encoding="utf-8")
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 0.1\nitems[id,status]:\n  one open\n", encoding="utf-8")

    run = subprocess.run(
        [
            sys.executable,
            "tools/sdif-cli.py",
            "validate",
            str(doc),
            "--schema",
            str(schema),
            "--json",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 1
    assert run.stderr == ""
    payload = json.loads(run.stdout)
    assert payload == {
        "valid": False,
        "diagnostics": [
            {
                "code": "SDIF_TABLE_ARITY",
                "severity": "error",
                "message": "row has 1 cells but table declares 2 columns; use literal HTAB as the column separator",
                "path": "$parse",
                "line": 3,
                "column": 3,
            }
        ],
    }


def test_cli_validate_text_reports_parse_errors_without_traceback(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text("@sdif 0.1\nkind Schema\n", encoding="utf-8")
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 0.1\nitems[id,status]:\n  one open\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--schema", str(schema)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 1
    assert run.stderr == ""
    assert run.stdout == (
        "error: SDIF_TABLE_ARITY $parse: "
        "row has 1 cells but table declares 2 columns; use literal HTAB as the column separator\n"
    )


def test_cli_validate_reports_malformed_schema_without_traceback(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text(
        "@sdif 0.1\nkind Schema\nfields[name,type]:\n  kind\tIdentifier\n",
        encoding="utf-8",
    )
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 0.1\nkind Plan\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--schema", str(schema)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode != 0
    assert "Traceback" not in run.stderr
    assert "invalid --schema" in run.stderr
    assert "schema table `fields` requires `required` column" in run.stderr
