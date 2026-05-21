import pytest

from sdif import canonicalize, parse_text
from sdif.validation import Schema


def test_schema_policy_orders_table_rows_relations_and_rules_when_unordered():
    schema_doc = parse_text("""
@sdif 1.0
kind Schema
tables[name,ordered,primary_key]:
  milestones\tfalse\tid
""")
    schema = Schema.from_document(schema_doc)
    source = """
@sdif 1.0
kind Plan
id demo
milestones[id,status]:
  R2\tpending
  R1\tdone
rel:
  z depends_on a
  a depends_on b
rules:
  (warn missing(x))
  (deny missing(y))
"""

    assert (
        canonicalize(source, schema=schema)
        == """
@sdif 1.0
kind Plan
id demo
milestones[id,status]:
  R1\tdone
  R2\tpending
rel:
  a depends_on b
  z depends_on a
rules:
  (deny missing(y))
  (warn missing(x))
""".lstrip()
    )


def test_unordered_table_without_primary_key_is_not_strictly_canonicalizable():
    schema_doc = parse_text("""
@sdif 1.0
kind Schema
tables[name,ordered,primary_key]:
  milestones\tfalse\tnull
""")
    schema = Schema.from_document(schema_doc)
    source = """
@sdif 1.0
kind Plan
milestones[id,status]:
  R2\tpending
  R1\tdone
"""

    with pytest.raises(ValueError, match="unordered table `milestones` requires primary_key"):
        canonicalize(source, schema=schema)


def test_cli_reports_canonicalization_error_without_traceback(tmp_path):
    import subprocess
    import sys

    schema_path = tmp_path / "schema.sdif"
    source_path = tmp_path / "source.sdif"
    schema_path.write_text(
        "@sdif 1.0\n"
        "kind Schema\n"
        "tables[name,ordered]:\n"
        "  milestones\tfalse\n",
        encoding="utf-8",
    )
    source_path.write_text(
        "@sdif 1.0\n"
        "milestones[id,status]:\n"
        "  R2\tpending\n"
        "  R1\tdone\n",
        encoding="utf-8",
    )

    run = subprocess.run(
        [sys.executable, "-m", "sdif.cli", "canon", str(source_path), "--schema", str(schema_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )

    assert run.returncode == 1
    assert run.stdout == ""
    assert "Canonicalization error: unordered table `milestones` requires primary_key" in run.stderr
    assert "Traceback" not in run.stderr
