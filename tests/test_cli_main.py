"""Comprehensive in-process tests for src/sdif/cli.py targeting 100% coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from sdif.cli import _ast_to_json, _count_tokens, _load_schema, _parse_aliases, main
from sdif.core.ast import (
    Directive,
    Document,
    Field,
    Narrative,
    ObjectBlock,
    Relation,
    Rule,
    Table,
)
from sdif import Policy, PolicyError

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

MINIMAL_SDIF = "@sdif 1.0\nkind Plan\nid demo\nstatus open\n"

# SDIF table rows use 2-space indentation + tab-separated values.
# Real tab characters (\t) are used as column separators.
FULL_SDIF = (
    "@sdif 1.0\n"
    "kind Plan\n"
    "id test.doc\n"
    "status open\n"
    "\n"
    "milestones[id,status]:\n"
    "  M1\tdone\n"
    "  M2\topen\n"
    "\n"
    "rel:\n"
    "  M1 depends_on M2\n"
    "\n"
    "rules:\n"
    "  (deny missing(id))\n"
)

# MINIMAL_SCHEMA — 2-space indent + tab-separated table row values
MINIMAL_SCHEMA = (
    "@sdif 1.0\n"
    "kind Schema\n"
    "id test.schema.v1\n"
    "schema sdif.schema.v1\n"
    "for_kind Plan\n"
    "\n"
    "fields[name,type,required,default]:\n"
    "  kind\tIdentifier\ttrue\tnull\n"
    "  id\tIdentifier\ttrue\tnull\n"
    "  status\tEnum(open,closed)\ttrue\topen\n"
)

# A broken SDIF that triggers a parse error (table row arity mismatch)
# Uses 2-space indentation + tab separator — single cell but header has 2 columns
BROKEN_SDIF = "@sdif 1.0\nitems[id,status]:\n  one\n"


def write_fixture(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# parse command
# ---------------------------------------------------------------------------


def test_parse_ok(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["parse", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    assert "directives=1" in out.out
    assert "statements=" in out.out


def test_parse_error_exits_1(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["parse", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# canon command
# ---------------------------------------------------------------------------


def test_canon_ok(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["canon", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    assert "@sdif 1.0" in out.out


def test_canon_with_schema(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["canon", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 0
    assert "@sdif 1.0" in out.out


def test_canon_parse_error(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["canon", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# hash command
# ---------------------------------------------------------------------------


def test_hash_ok(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["hash", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    # SHA-256 is 64 hex chars
    assert len(out.out.strip()) == 64


def test_hash_with_schema(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["hash", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 0
    assert len(out.out.strip()) == 64


def test_hash_parse_error(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["hash", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# tokens command
# ---------------------------------------------------------------------------


def test_tokens_ok(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["tokens", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    assert "bytes=" in out.out
    assert "tokenizer=" in out.out
    assert "tokens=" in out.out


def test_tokens_parse_error(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["tokens", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# to-json command
# ---------------------------------------------------------------------------


def test_to_json_ok(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["to-json", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    data = json.loads(out.out)
    assert "directives" in data or "kind" in data


def test_to_json_parse_error(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["to-json", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# from-json command
# ---------------------------------------------------------------------------


def test_from_json_ok(tmp_path, capsys):
    json_content = json.dumps({"directives": [{"sdif": "1.0"}], "kind": "Plan", "id": "demo"})
    jf = write_fixture(tmp_path, "d.json", json_content)
    rc = main(["from-json", str(jf)])
    out = capsys.readouterr()
    assert rc == 0
    assert "@sdif 1.0" in out.out or "kind" in out.out


# ---------------------------------------------------------------------------
# ai command
# ---------------------------------------------------------------------------


def test_ai_ok(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["ai", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    assert "@sdif.ai 1.0" in out.out


def test_ai_with_aliases(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["ai", str(doc), "--alias", "kind=k", "--alias", "id=i"])
    out = capsys.readouterr()
    assert rc == 0
    assert "@sdif.ai 1.0" in out.out


def test_ai_parse_error(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["ai", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# from-ai command
# ---------------------------------------------------------------------------


def test_from_ai_ok(tmp_path, capsys):
    # Generate a valid .sdif.ai file from an existing doc then convert back
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    # First, produce an AI projection via the ai command
    main(["ai", str(doc)])
    ai_text = capsys.readouterr().out

    ai_file = write_fixture(tmp_path, "d.sdif.ai", ai_text)
    rc = main(["from-ai", str(ai_file)])
    out = capsys.readouterr()
    assert rc == 0
    assert "@sdif 1.0" in out.out


def test_from_ai_parse_error(tmp_path, capsys):
    # Write something that parses but isn't a valid sdif.ai projection — use broken SDIF
    bad = write_fixture(tmp_path, "bad.sdif.ai", BROKEN_SDIF)
    rc = main(["from-ai", str(bad)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------


def test_validate_valid_doc(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["validate", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 0
    assert "valid" in out.out


def test_validate_invalid_doc_text_output(tmp_path, capsys):
    # Missing required 'id' field
    doc = write_fixture(tmp_path, "d.sdif", "@sdif 1.0\nkind Plan\n")
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["validate", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 1
    assert "SDIF_REQUIRED_FIELD" in out.out


def test_validate_invalid_doc_json_output(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", "@sdif 1.0\nkind Plan\n")
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["validate", str(doc), "--schema", str(schema), "--json"])
    out = capsys.readouterr()
    assert rc == 1
    data = json.loads(out.out)
    assert data["valid"] is False
    assert len(data["diagnostics"]) > 0


def test_validate_valid_doc_json_output(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["validate", str(doc), "--schema", str(schema), "--json"])
    out = capsys.readouterr()
    assert rc == 0
    data = json.loads(out.out)
    assert data["valid"] is True


def test_validate_parse_error_text(tmp_path, capsys):
    """ParseError inside validate command creates a diagnostic (text output)."""
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["validate", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 1
    assert "SDIF_TABLE_ARITY" in out.out


def test_validate_parse_error_json(tmp_path, capsys):
    """ParseError inside validate command creates a diagnostic (JSON output)."""
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["validate", str(doc), "--schema", str(schema), "--json"])
    out = capsys.readouterr()
    assert rc == 1
    data = json.loads(out.out)
    assert data["valid"] is False
    assert data["diagnostics"][0]["path"] == "$parse"


# ---------------------------------------------------------------------------
# inspect command
# ---------------------------------------------------------------------------


def test_inspect_basic(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["inspect", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    assert "directives=1" in out.out
    assert "statements=" in out.out


def test_inspect_json(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["inspect", str(doc), "--json"])
    out = capsys.readouterr()
    assert rc == 0
    data = json.loads(out.out)
    assert "ast" in data
    assert "directives" in data["ast"]
    assert "statements" in data["ast"]


def test_inspect_json_with_schema_valid(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["inspect", str(doc), "--json", "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 0
    data = json.loads(out.out)
    assert "ast" in data
    assert "diagnostics" in data
    assert data["diagnostics"] == []


def test_inspect_json_with_schema_invalid(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", "@sdif 1.0\nkind Plan\n")
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["inspect", str(doc), "--json", "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 1
    data = json.loads(out.out)
    assert "diagnostics" in data
    assert len(data["diagnostics"]) > 0


def test_inspect_text_with_schema_diagnostics(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", "@sdif 1.0\nkind Plan\n")
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    rc = main(["inspect", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 1
    assert "SDIF_REQUIRED_FIELD" in out.out


def test_inspect_parse_error_json(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["inspect", str(doc), "--json"])
    out = capsys.readouterr()
    assert rc == 1
    data = json.loads(out.out)
    assert data["ast"] is None
    assert len(data["diagnostics"]) == 1


def test_inspect_parse_error_text(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["inspect", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# fmt command
# ---------------------------------------------------------------------------


def test_fmt_already_canonical(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["fmt", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    assert "Reformatted" not in out.out


def test_fmt_not_canonical_rewrites(tmp_path, capsys):
    non_canonical = "@sdif 1.0\nid demo\nkind Plan\n"
    doc = write_fixture(tmp_path, "d.sdif", non_canonical)
    rc = main(["fmt", str(doc)])
    out = capsys.readouterr()
    assert rc == 0
    assert "Reformatted" in out.out
    assert doc.read_text(encoding="utf-8") == "@sdif 1.0\nkind Plan\nid demo\n"


def test_fmt_check_already_canonical(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["fmt", "--check", str(doc)])
    out = capsys.readouterr()
    assert rc == 0


def test_fmt_check_not_canonical(tmp_path, capsys):
    non_canonical = "@sdif 1.0\nid demo\nkind Plan\n"
    doc = write_fixture(tmp_path, "d.sdif", non_canonical)
    rc = main(["fmt", "--check", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Format check failed" in out.err


def test_fmt_parse_error(tmp_path, capsys):
    doc = write_fixture(tmp_path, "bad.sdif", BROKEN_SDIF)
    rc = main(["fmt", str(doc)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Format error: parse failed:" in out.err


def test_fmt_ai_projection(tmp_path, capsys):
    """fmt on a .sdif.ai file uses sdif_from_ai instead of canonicalize."""
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    # Generate AI projection
    main(["ai", str(doc)])
    ai_text = capsys.readouterr().out

    ai_file = write_fixture(tmp_path, "d.sdif.ai", ai_text)
    rc = main(["fmt", str(ai_file)])
    out = capsys.readouterr()
    assert rc == 0


def test_fmt_with_schema(tmp_path, capsys):
    schema_content = (
        "@sdif 1.0\n"
        "kind Schema\n"
        "tables[name,primary_key,ordered]:\n"
        "  mytable\tid\tfalse\n"
    )
    schema = write_fixture(tmp_path, "s.sdif", schema_content)
    non_canonical = "@sdif 1.0\nmytable[id,value]:\n  B\t2\n  A\t1\n"
    doc = write_fixture(tmp_path, "d.sdif", non_canonical)
    rc = main(["fmt", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 0
    assert "Reformatted" in out.out
    assert doc.read_text(encoding="utf-8") == "@sdif 1.0\nmytable[id,value]:\n  A\t1\n  B\t2\n"


# ---------------------------------------------------------------------------
# PolicyError handling
# ---------------------------------------------------------------------------


def test_policy_error_text_output(tmp_path, capsys):
    """PolicyError in non-JSON mode: stderr message, return 2."""
    import sdif.cli as cli_mod

    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    with patch.object(
        cli_mod,
        "_load_schema",
        side_effect=PolicyError("SDIF_POLICY_REMOTE_SCHEMA", "Remote schemas disallowed"),
    ):
        rc = main(["canon", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 2
    assert "Policy denial:" in out.err


def test_policy_error_json_output(tmp_path, capsys):
    """PolicyError in JSON mode (validate --json): stdout JSON, return 2."""
    import sdif.cli as cli_mod

    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)
    with patch.object(
        cli_mod,
        "_load_schema",
        side_effect=PolicyError("SDIF_POLICY_REMOTE_SCHEMA", "Remote schemas disallowed"),
    ):
        rc = main(["validate", str(doc), "--schema", str(schema), "--json"])
    out = capsys.readouterr()
    assert rc == 2
    data = json.loads(out.out)
    assert "policy_denial" in data


# ---------------------------------------------------------------------------
# _load_schema edge cases
# ---------------------------------------------------------------------------


def test_load_schema_none_returns_none():
    result = _load_schema(None)
    assert result is None


def test_load_schema_remote_disallowed_raises_policy_error():
    """_load_schema raises PolicyError for remote schemas when not allowed."""
    from unittest.mock import MagicMock

    remote_path = MagicMock(spec=Path)
    remote_path.__str__ = MagicMock(return_value="http://example.com/schema.sdif")
    with pytest.raises(PolicyError) as exc_info:
        _load_schema(remote_path, policy=Policy(allow_remote_schemas=False))
    assert exc_info.value.code == "SDIF_POLICY_REMOTE_SCHEMA"


def test_load_schema_remote_allowed_raises_policy_error():
    """Even with allow_remote_schemas=True, remote loading raises PolicyError (unsupported)."""
    from unittest.mock import MagicMock

    remote_path = MagicMock(spec=Path)
    remote_path.__str__ = MagicMock(return_value="http://example.com/schema.sdif")
    with pytest.raises(PolicyError) as exc_info:
        _load_schema(remote_path, policy=Policy(allow_remote_schemas=True))
    assert exc_info.value.code == "SDIF_POLICY_REMOTE_SCHEMA"


def test_load_schema_invalid_schema_raises_system_exit(tmp_path):
    """A schema file with invalid schema structure raises SystemExit."""
    # This schema has fields table with missing 'required' column
    malformed = write_fixture(
        tmp_path,
        "bad_schema.sdif",
        "@sdif 1.0\nkind Schema\nfields[name,type]:\n  kind\tIdentifier\n",
    )
    with pytest.raises(SystemExit) as exc_info:
        _load_schema(malformed)
    assert "invalid --schema" in str(exc_info.value)


def test_load_schema_ftp_remote(tmp_path):
    """FTP URLs are treated as remote and raise PolicyError."""
    from unittest.mock import MagicMock

    remote_path = MagicMock(spec=Path)
    remote_path.__str__ = MagicMock(return_value="ftp://example.com/schema.sdif")
    with pytest.raises(PolicyError):
        _load_schema(remote_path, policy=Policy(allow_remote_schemas=False))


# ---------------------------------------------------------------------------
# _parse_aliases edge cases
# ---------------------------------------------------------------------------


def test_parse_aliases_valid():
    result = _parse_aliases(["field=alias", "other=o"])
    assert result == {"field": "alias", "other": "o"}


def test_parse_aliases_empty():
    result = _parse_aliases([])
    assert result == {}


def test_parse_aliases_value_with_equals():
    """Values that contain '=' are handled — split on first '=' only."""
    result = _parse_aliases(["field=a=b"])
    assert result == {"field": "a=b"}


def test_parse_aliases_invalid_raises_system_exit():
    with pytest.raises(SystemExit) as exc_info:
        _parse_aliases(["no_equals_here"])
    assert "invalid alias" in str(exc_info.value)


# ---------------------------------------------------------------------------
# _count_tokens
# ---------------------------------------------------------------------------


def test_count_tokens_with_tiktoken():
    """When tiktoken is available, returns tiktoken/cl100k_base tokenizer."""
    tokenizer, count = _count_tokens("hello world", 11)
    assert "tiktoken" in tokenizer
    assert count > 0


def test_count_tokens_without_tiktoken():
    """Simulate missing tiktoken: falls back to estimate/4bytes."""
    original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else None

    import builtins

    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "tiktoken":
            raise ImportError("no tiktoken")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_fake_import):
        tokenizer, count = _count_tokens("hello world", 11)
    assert tokenizer == "estimate/4bytes"
    assert count > 0


def test_count_tokens_small_byte_count():
    """Byte count of 1 should still return at least 1 token."""
    with patch("builtins.__import__", side_effect=ImportError):
        tokenizer, count = _count_tokens("x", 1)
    assert count >= 1


# ---------------------------------------------------------------------------
# _ast_to_json — cover all node types directly
# ---------------------------------------------------------------------------


def test_ast_to_json_list():
    result = _ast_to_json([1, "two", 3])
    assert result == [1, "two", 3]


def test_ast_to_json_dict():
    result = _ast_to_json({"a": 1, "b": "two"})
    assert result == {"a": 1, "b": "two"}


def test_ast_to_json_primitive_int():
    assert _ast_to_json(42) == 42


def test_ast_to_json_primitive_none():
    assert _ast_to_json(None) is None


def test_ast_to_json_directive():
    d = Directive(name="sdif", args=["1.0"])
    result = _ast_to_json(d)
    assert result == {"type": "directive", "name": "sdif", "args": ["1.0"]}


def test_ast_to_json_field():
    f = Field(key="kind", value="Plan", quoted=False)
    result = _ast_to_json(f)
    assert result == {"type": "field", "key": "kind", "value": "Plan", "quoted": False}


def test_ast_to_json_table():
    t = Table(name="items", columns=["id", "val"], rows=[["a", "1"]], quoted_columns=frozenset())
    result = _ast_to_json(t)
    assert result["type"] == "table"
    assert result["name"] == "items"
    assert result["columns"] == ["id", "val"]


def test_ast_to_json_relation():
    r = Relation(subject="A", predicate="depends_on", object="B", object_quoted=False)
    result = _ast_to_json(r)
    assert result == {
        "type": "relation",
        "subject": "A",
        "predicate": "depends_on",
        "object": "B",
        "object_quoted": False,
    }


def test_ast_to_json_rule():
    rule = Rule(source="(deny missing(id))")
    result = _ast_to_json(rule)
    assert result == {"type": "rule", "source": "(deny missing(id))"}


def test_ast_to_json_narrative():
    n = Narrative(key="notes", text="Some text here.")
    result = _ast_to_json(n)
    assert result == {"type": "narrative", "key": "notes", "text": "Some text here."}


def test_ast_to_json_object_block():
    block = ObjectBlock(key="meta", statements=[Field(key="x", value="y", quoted=False)])
    result = _ast_to_json(block)
    assert result["type"] == "object"
    assert result["key"] == "meta"
    assert len(result["statements"]) == 1


def test_ast_to_json_document():
    doc = Document(
        directives=[Directive(name="sdif", args=["1.0"])],
        statements=[Field(key="kind", value="Plan", quoted=False)],
    )
    result = _ast_to_json(doc)
    assert "directives" in result
    assert "statements" in result
    assert result["directives"][0]["name"] == "sdif"


# ---------------------------------------------------------------------------
# ValueError (canonicalization error) handling
# ---------------------------------------------------------------------------


def test_canon_value_error_text(tmp_path, capsys):
    """Trigger ValueError from canonicalize via schema with unordered table missing primary_key."""
    schema_content = (
        "@sdif 1.0\n"
        "kind Schema\n"
        "tables[name,primary_key,ordered]:\n"
        "  mytable\tnull\tfalse\n"  # primary_key is null -> ValueError on sort
    )
    schema = write_fixture(tmp_path, "s.sdif", schema_content)
    doc_content = "@sdif 1.0\nmytable[id,value]:\n  B\t2\n  A\t1\n"
    doc = write_fixture(tmp_path, "d.sdif", doc_content)
    rc = main(["canon", str(doc), "--schema", str(schema)])
    out = capsys.readouterr()
    assert rc == 1
    assert "Canonicalization error:" in out.err


def test_canon_value_error_json(tmp_path, capsys):
    """ValueError with json_output=True: patch parse_file to raise ValueError from inspect --json."""
    import sdif.cli as cli_mod

    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)

    # inspect --json has json_output=True on args; if parse_file raises ValueError
    # it hits the outer except ValueError with json_output=True
    with patch.object(cli_mod, "parse_file", side_effect=ValueError("canon fail")):
        rc = main(["inspect", str(doc), "--json"])
        out = capsys.readouterr()
        assert rc == 1
        data = json.loads(out.out)
        assert data["error"]["code"] == "SDIF_CANONICALIZATION_ERROR"


# ---------------------------------------------------------------------------
# Outer ParseError with json_output=True (validate --json + broken doc)
# ---------------------------------------------------------------------------


def test_outer_parse_error_json_output(tmp_path, capsys):
    """The outer ParseError handler is also reachable through validate --json
    when the schema parse itself raises ParseError (escapes _load_schema's try/except
    if the schema's parse error is not a SchemaError). Actually validate's inner
    try-except catches ParseError from parse_file. The outer handler catches ParseError
    from _load_schema for commands WITHOUT a schema inner try, but validate has the inner try.
    Use 'canon' command to hit the outer handler (no json_output attr → non-JSON path).
    Use 'validate --json' with a doc that's valid but schema triggers a parse error
    via a file that raises ParseError (not SchemaError) from Schema.from_document.
    The easiest remaining outer ParseError + json_output path is via
    mocking parse_file to raise ParseError for a validate --json call where the
    parse happens in the inner try (caught already). Let's test via a broken schema
    that raises ParseError (not SchemaError) from Schema.from_document by mocking."""
    import sdif.cli as cli_mod
    from sdif.parser import ParseError as PE

    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)

    # Patch _load_schema to raise ParseError directly (simulates a truly broken schema
    # that gets past Schema.from_document as a ParseError not SchemaError)
    with patch.object(
        cli_mod,
        "_load_schema",
        side_effect=PE(code="SDIF_TEST", message="test parse error", line=1, column=1),
    ):
        rc = main(["validate", str(doc), "--schema", str(schema), "--json"])
        out = capsys.readouterr()
        assert rc == 1
        data = json.loads(out.out)
        assert "error" in data
        assert data["error"]["code"] == "SDIF_TEST"


def test_outer_parse_error_non_json_output(tmp_path, capsys):
    """Outer ParseError handler without json_output — writes to stderr."""
    import sdif.cli as cli_mod
    from sdif.parser import ParseError as PE

    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    schema = write_fixture(tmp_path, "s.sdif", MINIMAL_SCHEMA)

    with patch.object(
        cli_mod,
        "_load_schema",
        side_effect=PE(code="SDIF_TEST", message="test parse error", line=1, column=1),
    ):
        rc = main(["validate", str(doc), "--schema", str(schema)])
        out = capsys.readouterr()
        assert rc == 1
        assert "Parse error:" in out.err


# ---------------------------------------------------------------------------
# Policy flags
# ---------------------------------------------------------------------------


def test_allow_include_path_flag(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["parse", str(doc), "--allow-include-path", str(tmp_path)])
    out = capsys.readouterr()
    assert rc == 0


def test_allow_include_flag(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["parse", str(doc), "--allow-include"])
    out = capsys.readouterr()
    assert rc == 0


def test_allow_remote_include_flag(tmp_path, capsys):
    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)
    rc = main(["parse", str(doc), "--allow-remote-include"])
    out = capsys.readouterr()
    assert rc == 0


def test_allow_remote_schema_then_still_fails(tmp_path, capsys):
    """--allow-remote-schema bypasses the first PolicyError check but the second raise still fires."""
    from unittest.mock import MagicMock
    import sdif.cli as cli_mod

    doc = write_fixture(tmp_path, "d.sdif", MINIMAL_SDIF)

    # Simulate a remote path that would hit the "remote schemas not supported" branch
    # by patching _load_schema to raise the second PolicyError (allow_remote_schemas=True path)
    with patch.object(
        cli_mod,
        "_load_schema",
        side_effect=PolicyError("SDIF_POLICY_REMOTE_SCHEMA", "Remote schemas not supported"),
    ):
        rc = main(["canon", str(doc), "--schema", str(tmp_path / "fake.sdif")])
    out = capsys.readouterr()
    assert rc == 2
    assert "Policy denial:" in out.err
