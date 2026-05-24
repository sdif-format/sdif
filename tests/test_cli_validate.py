import json
import subprocess
import sys


def test_cli_validate_outputs_structured_diagnostics_json(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text(
        """
@sdif 1.0
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
@sdif 1.0
kind Plan
status blocked
rules:
  (deny unknown_func(evidence))
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
        capture_output=True,
        check=False,
        timeout=30,
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
@sdif 1.0
kind Schema
fields[name,type,required,default]:
  kind\tIdentifier\ttrue\tnull
  id\tIdentifier\ttrue\tnull
""".strip()
        + "\n",
        encoding="utf-8",
    )
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nkind Plan\nid demo\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--schema", str(schema)],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 0
    assert run.stdout.strip() == "valid"


def test_cli_validate_json_reports_parse_errors_as_structured_diagnostics(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text("@sdif 1.0\nkind Schema\n", encoding="utf-8")
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nitems[id,status]:\n  one open\n", encoding="utf-8")

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
        capture_output=True,
        check=False,
        timeout=30,
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
                "message": "table row has 1 cells but header declares 2 columns",
                "path": "$parse",
                "line": 3,
                "column": 3,
                "hint": "check HTAB separators and missing cells",
            }
        ],
    }


def test_cli_validate_text_reports_parse_errors_without_traceback(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text("@sdif 1.0\nkind Schema\n", encoding="utf-8")
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nitems[id,status]:\n  one open\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--schema", str(schema)],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 1
    assert run.stderr == ""
    assert run.stdout == (
        "error: SDIF_TABLE_ARITY $parse: table row has 1 cells but header declares 2 columns\n"
    )


def test_cli_validate_reports_malformed_schema_without_traceback(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text(
        "@sdif 1.0\nkind Schema\nfields[name,type]:\n  kind\tIdentifier\n",
        encoding="utf-8",
    )
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--schema", str(schema)],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode != 0
    assert "Traceback" not in run.stderr
    assert "invalid --schema" in run.stderr
    assert "schema table `fields` requires `required` column" in run.stderr


# ---------------------------------------------------------------------------
# Schema-optional (syntactic-only) validation
# ---------------------------------------------------------------------------


def test_cli_validate_no_schema_valid(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc)],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 0
    assert run.stdout.strip() == "valid"


def test_cli_validate_no_schema_invalid(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nitems[id,status]:\n  one open\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc)],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 1
    assert "SDIF_TABLE_ARITY" in run.stdout


def test_cli_validate_no_schema_file_not_found(tmp_path):
    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(tmp_path / "missing.sdif")],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 2
    assert run.stderr != ""
    assert run.stdout == ""


# ---------------------------------------------------------------------------
# --quiet mode
# ---------------------------------------------------------------------------


def test_cli_validate_quiet_valid(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--quiet"],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 0
    assert run.stdout == ""
    assert run.stderr == ""


def test_cli_validate_quiet_invalid(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nitems[id,status]:\n  one open\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--quiet"],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 1
    assert run.stdout == ""


def test_cli_validate_quiet_json_quiet_wins(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--quiet", "--json"],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 0
    assert run.stdout == ""


def test_cli_validate_quiet_file_not_found_stderr_allowed(tmp_path):
    run = subprocess.run(
        [
            sys.executable,
            "tools/sdif-cli.py",
            "validate",
            str(tmp_path / "missing.sdif"),
            "--quiet",
        ],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert run.returncode == 2
    assert run.stderr != ""
    assert run.stdout == ""
