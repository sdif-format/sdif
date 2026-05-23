import json
import subprocess
import sys


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/sdif-cli.py", *args],
        text=True,
        capture_output=True,
        check=check,
        timeout=30,
    )


def test_cli_inspect_basic(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\nkind Plan\nid demo\n", encoding="utf-8")

    # Test inspect without --json
    run = run_cli("inspect", str(doc))
    assert run.returncode == 0
    assert "directives=1" in run.stdout
    assert "statements=2" in run.stdout

    # Test inspect with --json
    run_json = run_cli("inspect", str(doc), "--json")
    assert run_json.returncode == 0
    data = json.loads(run_json.stdout)
    assert "ast" in data
    ast = data["ast"]
    assert "directives" in ast
    assert "statements" in ast
    assert ast["directives"][0]["name"] == "sdif"
    assert ast["statements"][0]["type"] == "field"
    assert ast["statements"][0]["key"] == "kind"
    assert ast["statements"][0]["value"] == "Plan"


def test_cli_inspect_with_schema_diagnostics(tmp_path):
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
    doc.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")  # missing "id"

    # Test inspect --json with --schema
    run = run_cli("inspect", str(doc), "--json", "--schema", str(schema), check=False)
    assert run.returncode == 1
    data = json.loads(run.stdout)
    assert "ast" in data
    assert "diagnostics" in data
    diagnostics = data["diagnostics"]
    assert len(diagnostics) == 1
    assert diagnostics[0]["code"] == "SDIF_REQUIRED_FIELD"

    # Test inspect (text mode) with --schema
    run_text = run_cli("inspect", str(doc), "--schema", str(schema), check=False)
    assert run_text.returncode == 1
    assert "directives=1" in run_text.stdout
    assert "error: SDIF_REQUIRED_FIELD" in run_text.stdout


def test_cli_inspect_parse_error(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text(
        "@sdif 1.0\nkind Plan\ntable[col1]:\n  one\ttwo\n", encoding="utf-8"
    )  # Table row arity error

    # Test inspect --json on parse error
    run = run_cli("inspect", str(doc), "--json", check=False)
    assert run.returncode == 1
    data = json.loads(run.stdout)
    assert data["ast"] is None
    assert "diagnostics" in data
    assert len(data["diagnostics"]) == 1
    assert data["diagnostics"][0]["code"] == "SDIF_TABLE_ARITY"

    # Test inspect (text mode) on parse error
    run_text = run_cli("inspect", str(doc), check=False)
    assert run_text.returncode == 1
    assert "Parse error:" in run_text.stderr


def test_cli_fmt_check_and_inplace(tmp_path):
    doc = tmp_path / "doc.sdif"
    non_canonical = (
        "@sdif 1.0\nid demo\nkind Plan\n"  # "kind" should come before "id" in canonical order
    )
    doc.write_text(non_canonical, encoding="utf-8")

    # fmt --check should fail on non-canonical document
    run_check = run_cli("fmt", "--check", str(doc), check=False)
    assert run_check.returncode == 1
    assert "Format check failed" in run_check.stderr

    # fmt (without --check) should reform the file in-place
    run_fmt = run_cli("fmt", str(doc))
    assert run_fmt.returncode == 0
    assert "Reformatted" in run_fmt.stdout

    # Now fmt --check should succeed
    run_check_2 = run_cli("fmt", "--check", str(doc))
    assert run_check_2.returncode == 0
    assert doc.read_text(encoding="utf-8") == "@sdif 1.0\nkind Plan\nid demo\n"


def test_cli_fmt_check_with_schema(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text(
        """
@sdif 1.0
kind Schema
tables[name,primary_key,ordered]:
  mytable\tid\tfalse
""".strip()
        + "\n",
        encoding="utf-8",
    )
    doc = tmp_path / "doc.sdif"
    # rows are not ordered by primary key "id"
    non_canonical = "@sdif 1.0\nmytable[id,value]:\n  B\t2\n  A\t1\n"
    doc.write_text(non_canonical, encoding="utf-8")

    # fmt --check without schema will not sort rows (it does not know it is unordered table)
    run_check_no_schema = run_cli("fmt", "--check", str(doc))
    assert run_check_no_schema.returncode == 0

    # fmt --check with schema should fail because rows are not sorted
    run_check_schema = run_cli("fmt", "--check", str(doc), "--schema", str(schema), check=False)
    assert run_check_schema.returncode == 1

    # fmt with schema should sort in-place
    run_fmt = run_cli("fmt", str(doc), "--schema", str(schema))
    assert run_fmt.returncode == 0

    # now fmt --check with schema should pass
    run_check_schema_2 = run_cli("fmt", "--check", str(doc), "--schema", str(schema))
    assert run_check_schema_2.returncode == 0
    assert doc.read_text(encoding="utf-8") == "@sdif 1.0\nmytable[id,value]:\n  A\t1\n  B\t2\n"


def test_cli_fmt_parse_error(tmp_path):
    doc = tmp_path / "doc.sdif"
    doc.write_text("@sdif 1.0\ntable[col1]:\n  one\ttwo\n", encoding="utf-8")

    run = run_cli("fmt", "--check", str(doc), check=False)
    assert run.returncode == 1
    assert "Format error: parse failed:" in run.stderr
