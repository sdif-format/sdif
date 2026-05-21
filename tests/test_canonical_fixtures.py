import hashlib
import subprocess
import sys
from pathlib import Path

from sdif import Policy, canonicalize, parse_text, sdif_hash
from sdif.validation import Schema

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_ROOT = ROOT / "examples" / "golden"
PLAN_SCHEMA = ROOT / "examples" / "schema.sdif"


def _schema_for_fixture(name: str) -> Schema | None:
    if name != "plan":
        return None
    return Schema.from_document(parse_text(PLAN_SCHEMA.read_text(encoding="utf-8")))


def test_golden_sources_match_canonical_fixtures_and_hashes():
    policy = Policy(max_document_size=10_000_000)
    for source in sorted(GOLDEN_ROOT.glob("*/source.sdif")):
        fixture_dir = source.parent
        schema = _schema_for_fixture(fixture_dir.name)
        expected_canonical = (fixture_dir / "canonical.sdif").read_text(encoding="utf-8")
        expected_hash = (fixture_dir / "canonical.sha256").read_text(encoding="utf-8").strip()

        canonical = canonicalize(source.read_text(encoding="utf-8"), schema=schema, policy=policy)

        assert canonical == expected_canonical, fixture_dir.name
        assert sdif_hash(source.read_text(encoding="utf-8"), schema=schema, policy=policy) == expected_hash
        assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == expected_hash



def test_cli_canon_and_hash_accept_schema_policy(tmp_path):
    schema = tmp_path / "schema.sdif"
    schema.write_text(
        """
@sdif 0.1
kind Schema
tables[name,ordered,primary_key]:
  milestones	false	id
""".lstrip(),
        encoding="utf-8",
    )
    source = tmp_path / "plan.sdif"
    source.write_text(
        """
@sdif 0.1
kind Plan
milestones[id,status]:
  R2	pending
  R1	done
""".lstrip(),
        encoding="utf-8",
    )

    canon_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "canon", str(source), "--schema", str(schema)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    assert (
        canon_run.stdout
        == """\
@sdif 0.1
kind Plan
milestones[id,status]:
  R1	done
  R2	pending
"""
    )

    hash_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "hash", str(source), "--schema", str(schema)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    assert hash_run.stdout.strip() == hashlib.sha256(canon_run.stdout.encode("utf-8")).hexdigest()


def test_cli_schema_option_rejects_non_schema_document(tmp_path):
    source = tmp_path / "plan.sdif"
    source.write_text("@sdif 0.1\nkind Plan\n", encoding="utf-8")
    not_schema = tmp_path / "canonical.sdif"
    not_schema.write_text("@sdif 0.1\nkind Plan\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "canon", str(source), "--schema", str(not_schema)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode != 0
    assert "expected schema document with `kind Schema`" in run.stderr


def test_cli_validate_rejects_non_schema_document(tmp_path):
    source = tmp_path / "plan.sdif"
    source.write_text("@sdif 0.1\nkind Plan\n", encoding="utf-8")
    not_schema = tmp_path / "canonical.sdif"
    not_schema.write_text("@sdif 0.1\nkind Plan\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "validate", str(source), "--schema", str(not_schema)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode != 0
    assert "expected schema document with `kind Schema`" in run.stderr
