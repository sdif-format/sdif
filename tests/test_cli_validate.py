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
        [sys.executable, "tools/sdif-cli.py", "validate", str(doc), "--schema", str(schema), "--json"],
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
