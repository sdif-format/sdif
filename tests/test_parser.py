import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

from sdif import canonicalize, parse_text, sdif_hash
from sdif.parser import ParseError


def test_parse_core_document_constructs_ast():
    text = '''
# comments are source-only
@sdif 0.1
@profile source
kind Plan
id release.v2.validation_plan
owner:
  id team.platform
  role maintainer
milestones[id,status,gate,evidence]:
  R1\tdone\tvalidate-syntax\treports/syntax.md
  R2\tpending\tvalidate-schema\treports/schema.md
rel:
  R2 depends_on R1
rules:
  (deny missing(evidence))
intent """
Keep this bounded.
And multiline.
"""
'''

    doc = parse_text(text)

    assert [(d.name, d.args) for d in doc.directives] == [
        ("sdif", ["0.1"]),
        ("profile", ["source"]),
    ]
    assert doc.fields["kind"].value == "Plan"
    assert doc.objects["owner"].fields["role"].value == "maintainer"
    assert doc.tables["milestones"].columns == ["id", "status", "gate", "evidence"]
    assert doc.tables["milestones"].rows[1] == [
        "R2",
        "pending",
        "validate-schema",
        "reports/schema.md",
    ]
    assert doc.relations[0].predicate == "depends_on"
    assert doc.rules[0].source == "(deny missing(evidence))"
    assert doc.narratives["intent"].text == "Keep this bounded.\nAnd multiline."


def test_table_rows_must_use_htab_and_match_header_arity():
    with pytest.raises(ParseError) as excinfo:
        parse_text('''
@sdif 0.1
items[id,status]:
  item.1 open
''')

    assert excinfo.value.code == "SDIF_TABLE_ARITY"
    assert "literal HTAB" in excinfo.value.message


def test_relation_rows_have_exactly_three_parts():
    with pytest.raises(ParseError) as excinfo:
        parse_text('''
@sdif 0.1
rel:
  a depends_on b extra
''')

    assert excinfo.value.code == "SDIF_REL_ARITY"


def test_canonicalization_removes_comments_and_hashes_stable_bytes():
    left = '''
# source comment
@profile source
@sdif 0.1
id release.v2
kind Plan
milestones[id,status]:
  R1\tdone
'''
    right = '''
@sdif 0.1
@profile source
kind Plan
id release.v2 # inline comment

milestones[id,status]:
  R1\tdone
'''

    canon = canonicalize(left)

    assert canon == canonicalize(right)
    assert "#" not in canon
    assert canon.startswith("@sdif 0.1\n@profile source\n")
    assert canon.endswith("\n")
    assert sdif_hash(left) == hashlib.sha256(canon.encode("utf-8")).hexdigest()


def test_cli_parse_canon_hash_and_tokens(tmp_path):
    fixture = tmp_path / "doc.sdif"
    fixture.write_text("@sdif 0.1\nkind Plan\nid demo\n", encoding="utf-8")

    parse_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "parse", str(fixture)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    assert "directives=1" in parse_run.stdout
    assert "statements=2" in parse_run.stdout

    canon_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "canon", str(fixture)],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    assert canon_run.stdout == "@sdif 0.1\nkind Plan\nid demo\n"

    hash_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "hash", str(fixture)],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    assert len(hash_run.stdout.strip()) == 64

    token_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "tokens", str(fixture)],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    assert "bytes=" in token_run.stdout
    assert "tokens_estimate=" in token_run.stdout


def test_table_cells_preserve_spaces_as_data():
    padded = "  padded label  "

    doc = parse_text(f'''
@sdif 0.1
items[id,label]:
  item.1	{padded}
''')

    assert doc.tables["items"].rows == [["item.1", padded]]


def test_relation_object_supports_quoted_strings_with_spaces():
    doc = parse_text('''
@sdif 0.1
rel:
  doc.1 describes "hello world"
''')

    assert doc.relations[0].object == "hello world"
    assert canonicalize(doc) == '@sdif 0.1\nrel:\n  doc.1 describes "hello world"\n'


@pytest.mark.parametrize("block", ["rel", "rules"])
def test_relation_and_rule_rows_require_exact_child_indentation(block):
    body = "a depends_on b" if block == "rel" else "(deny missing(evidence))"

    with pytest.raises(ParseError) as excinfo:
        parse_text(f'''
@sdif 0.1
{block}:
    {body}
''')

    assert excinfo.value.code == "SDIF_INDENT"


def test_repository_examples_parse_successfully():
    for path in sorted(Path("examples").glob("*.sdif")):
        parse_text(path.read_text(encoding="utf-8"))
