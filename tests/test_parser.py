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
@sdif 1.0
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
        ("sdif", ["1.0"]),
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


def test_compact_ai_table_rows_may_omit_indentation_and_canonicalize_back():
    source = "\n@sdif.ai 1.0\nitems[id,status]:\nR1\tdone\nR2\tpending\nkind Plan\n"

    doc = parse_text(source)

    assert doc.tables["items"].rows == [["R1", "done"], ["R2", "pending"]]
    assert doc.fields["kind"].value == "Plan"
    assert canonicalize(doc) == (
        "@sdif.ai 1.0\nkind Plan\nitems[id,status]:\n  R1\tdone\n  R2\tpending\n"
    )


def test_sdif_ai_alias_header_is_parseable_and_canonicalized():
    source = "@sdif.ai 1.0\nalias[k=kind,st=status]\nk Plan\n"

    doc = parse_text(source)

    assert [(d.name, d.args) for d in doc.directives] == [
        ("sdif.ai", ["1.0"]),
        ("alias", ["k=kind", "st=status"]),
    ]
    assert doc.fields["k"].value == "Plan"
    assert canonicalize(doc) == source


@pytest.mark.parametrize(
    ("source", "code"),
    [
        ("@sdif banana\nkind Plan\n", "SDIF_VERSION_UNSUPPORTED"),
        ("@sdif 2.0\nkind Plan\n", "SDIF_VERSION_UNSUPPORTED"),
        ("@sdif\nkind Plan\n", "SDIF_VERSION_SYNTAX"),
        ("@sdif 1.0 extra\nkind Plan\n", "SDIF_VERSION_SYNTAX"),
        ("@sdif.ai banana\nkind Plan\n", "SDIF_VERSION_UNSUPPORTED"),
        ("@whatever x\nkind Plan\n", "SDIF_DIRECTIVE_UNKNOWN"),
        ("kind Plan\n", "SDIF_VERSION_MISSING"),
    ],
)
def test_format_version_directive_is_strict_for_v1(source, code):
    with pytest.raises(ParseError) as excinfo:
        parse_text(source)

    assert excinfo.value.code == code


def test_source_and_ai_version_directives_are_mutually_exclusive():
    with pytest.raises(ParseError) as excinfo:
        parse_text("@sdif 1.0\n@sdif.ai 1.0\nkind Plan\n")

    assert excinfo.value.code == "SDIF_VERSION_CONFLICT"


def test_table_rows_must_use_htab_and_match_header_arity():
    with pytest.raises(ParseError) as excinfo:
        parse_text("""
@sdif 1.0
items[id,status]:
  item.1 open
""")

    assert excinfo.value.code == "SDIF_TABLE_ARITY"
    assert "header declares" in excinfo.value.message
    assert "HTAB" in (excinfo.value.hint or "")


def test_relation_rows_have_exactly_three_parts():
    with pytest.raises(ParseError) as excinfo:
        parse_text("""
@sdif 1.0
rel:
  a depends_on b extra
""")

    assert excinfo.value.code == "SDIF_REL_ARITY"


def test_canonicalization_removes_comments_and_hashes_stable_bytes():
    left = """
# source comment
@profile source
@sdif 1.0
id release.v2
kind Plan
milestones[id,status]:
  R1\tdone
"""
    right = """
@sdif 1.0
@profile source
kind Plan
id release.v2 # inline comment

milestones[id,status]:
  R1\tdone
"""

    canon = canonicalize(left)

    assert canon == canonicalize(right)
    assert "#" not in canon
    assert canon.startswith("@sdif 1.0\n@profile source\n")
    assert canon.endswith("\n")
    assert sdif_hash(left) == hashlib.sha256(canon.encode("utf-8")).hexdigest()


def test_cli_parse_canon_hash_and_tokens(tmp_path):
    fixture = tmp_path / "doc.sdif"
    fixture.write_text("@sdif 1.0\nkind Plan\nid demo\n", encoding="utf-8")

    parse_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "parse", str(fixture)],
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    assert "directives=1" in parse_run.stdout
    assert "statements=2" in parse_run.stdout

    canon_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "canon", str(fixture)],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
        timeout=30,
    )
    assert canon_run.stdout == "@sdif 1.0\nkind Plan\nid demo\n"

    hash_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "hash", str(fixture)],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
        timeout=30,
    )
    assert len(hash_run.stdout.strip()) == 64

    token_run = subprocess.run(
        [sys.executable, "tools/sdif-cli.py", "tokens", str(fixture)],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
        timeout=30,
    )
    assert "bytes=" in token_run.stdout
    assert "tokenizer=" in token_run.stdout
    assert "tokens=" in token_run.stdout


def test_table_cells_preserve_spaces_as_data():
    padded = "  padded label  "

    doc = parse_text(f"""
@sdif 1.0
items[id,label]:
  item.1	{padded}
""")

    assert doc.tables["items"].rows == [["item.1", padded]]


def test_relation_object_supports_quoted_strings_with_spaces():
    doc = parse_text("""
@sdif 1.0
rel:
  doc.1 describes "hello world"
""")

    assert doc.relations[0].object == "hello world"
    assert canonicalize(doc) == '@sdif 1.0\nrel:\n  doc.1 describes "hello world"\n'


@pytest.mark.parametrize("block", ["rel", "rules"])
def test_relation_and_rule_rows_require_exact_child_indentation(block):
    body = "a depends_on b" if block == "rel" else "(deny missing(evidence))"

    with pytest.raises(ParseError) as excinfo:
        parse_text(f"""
@sdif 1.0
{block}:
    {body}
""")

    assert excinfo.value.code == "SDIF_INDENT"


def test_repository_examples_parse_successfully():
    for path in sorted(Path("examples").glob("*.sdif")):
        parse_text(path.read_text(encoding="utf-8"))


def test_valid_nested_narrative():
    doc = parse_text('''
@sdif 1.0
owner:
  bio """
  Hello
    indented line
  world
  """
''')
    assert doc.objects["owner"].narratives["bio"].text == "Hello\n  indented line\nworld"


def test_nested_narrative_canonicalization_remains_parseable_and_idempotent():
    source = '@sdif 1.0\nobj:\n  notes """\n  hello\n  """\n'

    canonical = canonicalize(source)

    parse_text(canonical)
    assert canonical == canonicalize(canonical)


def test_mismatched_nested_narrative_close():
    with pytest.raises(ParseError) as excinfo:
        parse_text('''
@sdif 1.0
owner:
  bio """
    Hello
"""
''')
    assert excinfo.value.code == "SDIF_NARRATIVE_CLOSE_ALIGN"
    assert "closing triple quotes must match" in excinfo.value.hint


def test_unclosed_nested_narrative():
    with pytest.raises(ParseError) as excinfo:
        parse_text('''
@sdif 1.0
owner:
  bio """
    Hello
''')
    assert excinfo.value.code == "SDIF_NARRATIVE_UNCLOSED"
    assert "make sure to close" in excinfo.value.hint
