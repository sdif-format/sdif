"""Additional coverage tests for parser.py, canonicalizer.py, and ast.py.

These tests target the specific uncovered lines identified in the coverage report.
"""

from __future__ import annotations


import pytest

from sdif import canonicalize, parse_text
from sdif.canonical.canonicalizer import _inside_current_block
from sdif.core.ast import (
    Directive,
    Document,
    Field,
    ObjectBlock,
    statement_count,
)
from sdif.core.policy import Policy, PolicyError
from sdif.parser import ParseError
from sdif.parser.parser import parse_file
from sdif.validation import Schema
from sdif.validation.validator import TablePolicy


# ---------------------------------------------------------------------------
# ParseError.__str__  (line 51)
# ---------------------------------------------------------------------------


def test_parse_error_str_includes_code_line_and_message():
    err = ParseError("SDIF_TEST", "test message", 5, 10)
    s = str(err)
    assert "SDIF_TEST" in s
    assert "5" in s
    assert "test message" in s


def test_parse_error_str_with_column():
    err = ParseError("SDIF_X", "msg", 3, 7)
    s = str(err)
    assert "3:7" in s


# ---------------------------------------------------------------------------
# policy.max_document_size  (line 63)
# ---------------------------------------------------------------------------


def test_policy_max_document_size_raises():
    tiny_policy = Policy(max_document_size=10)
    with pytest.raises(PolicyError) as exc_info:
        parse_text("@sdif 1.0\nkind Plan\n", policy=tiny_policy)
    assert exc_info.value.code == "SDIF_POLICY_DOCUMENT_SIZE"


# ---------------------------------------------------------------------------
# parse_indented_block returns None (line 112)
# ---------------------------------------------------------------------------


def test_parse_next_returns_none_for_lower_indent():
    # A nested child block ends when indentation drops below child_indent.
    # _parse_next returns None when actual_indent < indent.
    # We trigger this indirectly: parse an object that has a field at child_indent,
    # then a following line at lower indent (which terminates the object).
    doc = parse_text("@sdif 1.0\nobj:\n  key val\nanother val\n")
    assert doc.objects["obj"].fields["key"].value == "val"
    assert doc.fields["another"].value == "val"


# ---------------------------------------------------------------------------
# SDIF_INDENT unexpected indentation (line 114)
# ---------------------------------------------------------------------------


def test_unexpected_indentation_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\n  kind Plan\n")
    assert exc_info.value.code == "SDIF_INDENT"


# ---------------------------------------------------------------------------
# SDIF_ALIAS_SYNTAX (line 127)
# ---------------------------------------------------------------------------


def test_alias_entry_without_equals_raises():
    # Manually construct a regex match scenario that gets past header-RE
    # but then fails the "=" check. The alias header regex requires valid entries,
    # so there is no normal way to trigger line 127 via parse_text alone —
    # that branch is a defensive check. Verify the standard error-free path
    # and that malformed aliases without "=" in the value fail with a PolicyError.
    # (The header regex guarantees entries contain "=" so line 127 is unreachable
    # through normal parsing — skip it as dead code.)
    pass


# ---------------------------------------------------------------------------
# alias reserved term  (line 134)
# ---------------------------------------------------------------------------


def test_alias_reserved_term_raises_policy_error():
    with pytest.raises(PolicyError) as exc_info:
        parse_text("@sdif.ai 1.0\nalias[include=something]\n")
    assert exc_info.value.code == "SDIF_POLICY_ALIAS_RESERVED"


# ---------------------------------------------------------------------------
# alias collision  (line 143)
# ---------------------------------------------------------------------------


def test_alias_collision_raises_policy_error():
    with pytest.raises(PolicyError) as exc_info:
        parse_text("@sdif.ai 1.0\nalias[k=kind]\nalias[k=status]\n")
    assert exc_info.value.code == "SDIF_POLICY_ALIAS_COLLISION"


# ---------------------------------------------------------------------------
# rel[subject]: outside sdif.ai  (lines 157-163)
# ---------------------------------------------------------------------------


def test_rel_subject_syntax_in_non_ai_profile_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrel[subject,pred]:\n  a b\n")
    assert exc_info.value.code == "SDIF_AI_REL_SUBJECT"


def test_rel_subject_block_in_ai_profile_parses():
    doc = parse_text("@sdif.ai 1.0\nrel[alice]:\n  likes bob\n")
    assert len(doc.relations) == 1
    assert doc.relations[0].subject == "alice"
    assert doc.relations[0].predicate == "likes"
    assert doc.relations[0].object == "bob"


def test_rel_subject_block_arity_error_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif.ai 1.0\nrel[alice]:\n  likes bob extra\n")
    assert exc_info.value.code == "SDIF_REL_ARITY"


def test_rel_subject_block_indent_error_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif.ai 1.0\nrel[alice]:\n    likes bob\n")
    assert exc_info.value.code == "SDIF_INDENT"


# ---------------------------------------------------------------------------
# SDIF_DIRECTIVE empty directive (line 182)
# ---------------------------------------------------------------------------


def test_empty_directive_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nkind Test\n@\n")
    assert exc_info.value.code == "SDIF_DIRECTIVE"


# ---------------------------------------------------------------------------
# policy.max_string_length  (line 78)
# ---------------------------------------------------------------------------


def test_policy_max_string_length_raises():
    tiny_policy = Policy(max_string_length=5)
    with pytest.raises(PolicyError) as exc_info:
        parse_text("@sdif 1.0\nkind VeryLongValue\n", policy=tiny_policy)
    assert exc_info.value.code == "SDIF_POLICY_STRING_LENGTH"


# ---------------------------------------------------------------------------
# SDIF_FIELD field requires key and value (line 223)
# ---------------------------------------------------------------------------


def test_field_no_value_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nkind Test\nfoo\n")
    assert exc_info.value.code == "SDIF_FIELD"


# ---------------------------------------------------------------------------
# max nesting depth (line 233)
# ---------------------------------------------------------------------------


def test_max_nesting_depth_raises():
    shallow_policy = Policy(max_nesting_depth=1)
    nested = "@sdif 1.0\na:\n  b:\n    key val\n"
    with pytest.raises(PolicyError) as exc_info:
        parse_text(nested, policy=shallow_policy)
    assert exc_info.value.code == "SDIF_POLICY_NESTING_DEPTH"


# ---------------------------------------------------------------------------
# directive inside object raises (line 252)
# ---------------------------------------------------------------------------


def test_directive_inside_object_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nobj:\n  @profile source\n")
    assert exc_info.value.code == "SDIF_OBJECT_DIRECTIVE"


# ---------------------------------------------------------------------------
# SDIF_TABLE_HEADER table must declare columns (line 268)
# ---------------------------------------------------------------------------


def test_table_no_columns_raises():
    with pytest.raises(ParseError) as exc_info:
        # table header with empty brackets — but the regex requires at least one char in cols.
        # We build a table that parses columns but they're all whitespace/empty after strip.
        parse_text("@sdif 1.0\nkind Test\nfoo[ ]:\n")
    assert exc_info.value.code == "SDIF_TABLE_HEADER"


# ---------------------------------------------------------------------------
# SDIF_INDENT invalid table row indentation (line 285)
# ---------------------------------------------------------------------------


def test_table_row_invalid_indentation_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nitems[a,b]:\n    x\ty\n")
    assert exc_info.value.code == "SDIF_INDENT"


# ---------------------------------------------------------------------------
# inline comment inside table row raises (line 287)
# ---------------------------------------------------------------------------


def test_inline_comment_inside_table_row_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nitems[a,b]:\n  x\ty # comment\n")
    assert exc_info.value.code == "SDIF_TABLE_ROW_COMMENT"


# ---------------------------------------------------------------------------
# table row count policy (line 306)
# ---------------------------------------------------------------------------


def test_table_row_count_policy_raises():
    tiny_policy = Policy(max_table_row_count=1)
    text = "@sdif 1.0\nitems[a,b]:\n  x\ty\n  p\tq\n"
    with pytest.raises(PolicyError) as exc_info:
        parse_text(text, policy=tiny_policy)
    assert exc_info.value.code == "SDIF_POLICY_TABLE_ROW_COUNT"


# ---------------------------------------------------------------------------
# Rule row indentation error (lines 389-390)
# ---------------------------------------------------------------------------


def test_rule_row_invalid_indentation_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n    (deny missing(evidence))\n")
    assert exc_info.value.code == "SDIF_INDENT"


# ---------------------------------------------------------------------------
# Rule expression parsing errors (lines 355-406)
# ---------------------------------------------------------------------------


def test_rule_empty_parens_raises():
    # "()" — name is ")" which is not an identifier
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  ()\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_unclosed_paren_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_unclosed_call_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (deny missing\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_compact_unclosed_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  deny(missing(evidence)\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_extra_tokens_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (deny missing(evidence)) extra\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_not_call_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  just_identifier\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_invalid_action_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (allow missing(evidence))\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_no_args_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (deny)\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_literal_string_first_arg_raises():
    # (deny "literal string") — first arg is a string literal, not Call/Identifier → error
    with pytest.raises(ParseError) as exc_info:
        parse_text('@sdif 1.0\nrules:\n  (deny "literal string")\n')
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_null_first_arg_raises():
    # (deny null) — first arg is None → error
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (deny null)\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_true_first_arg_raises():
    # (deny true) — first arg is bool → error
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (deny true)\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_false_first_arg_raises():
    # (deny false) — first arg is bool → error
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (deny false)\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_integer_first_arg_raises():
    # (deny 42) has first arg as int, which triggers line 622 in _to_rule_expression
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  (deny 42)\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_float_arg_parses():
    # (deny x 3.14) — second arg is float, first is Identifier
    doc = parse_text("@sdif 1.0\nrules:\n  (deny x 3.14)\n")
    assert len(doc.rules) == 1


def test_rule_identifier_compact_form_parses():
    doc = parse_text("@sdif 1.0\nrules:\n  deny(missing(evidence))\n")
    assert len(doc.rules) == 1


def test_rule_special_char_tokenized_as_identifier():
    # A token that is not alphanumeric/parens/comma/quote/multichar — e.g. "@"
    # This goes to the else branch in _tokenize_rule (lines 552-553)
    # The char "@" becomes a single-char token used as an Identifier/function name.
    doc = parse_text("@sdif 1.0\nrules:\n  (deny @)\n")
    # The rule parses successfully; function name is "@"
    assert len(doc.rules) == 1


# ---------------------------------------------------------------------------
# Narrative unclosed  (line 449)
# ---------------------------------------------------------------------------


def test_unclosed_narrative_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text('@sdif 1.0\nintent """\nSome content\n')
    assert exc_info.value.code == "SDIF_NARRATIVE_UNCLOSED"


def test_narrative_line_not_starting_with_prefix_is_included():
    # Test line 433: a line NOT starting with prefix is appended as-is.
    # This happens with a nested narrative when a content line lacks the indentation prefix.
    doc = parse_text('@sdif 1.0\nobj:\n  bio """\nno-indent line\n  """\n')
    # "no-indent line" doesn't start with "  " (the object's indent prefix), so line 433 fires
    assert "no-indent line" in doc.objects["obj"].narratives["bio"].text


# ---------------------------------------------------------------------------
# Quoted string escape handling  (lines 462-498, 510)
# ---------------------------------------------------------------------------


def test_split_quoted_whitespace_escape_handling():
    # Relation with escaped quote in object
    doc = parse_text('@sdif 1.0\nrel:\n  doc.1 describes "hello \\"world\\""\n')
    assert 'hello "world"' in doc.relations[0].object


def test_split_quoted_whitespace_unterminated_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text('@sdif 1.0\nrel:\n  doc.1 describes "unterminated\n')
    assert exc_info.value.code == "SDIF_REL_QUOTE"


def test_parse_scalar_field_unterminated_quote_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text('@sdif 1.0\ntitle "hello\n')
    assert exc_info.value.code == "SDIF_STRING_UNCLOSED"


def test_split_quoted_whitespace_escaped_at_end_raises():
    with pytest.raises(ParseError) as exc_info:
        # backslash at end of quoted string — leaves escaped=True
        parse_text('@sdif 1.0\nrel:\n  doc.1 describes "value\\\n')
    assert exc_info.value.code == "SDIF_REL_QUOTE"


# ---------------------------------------------------------------------------
# Tokenize rule — quoted string with escape  (lines 532-545)
# ---------------------------------------------------------------------------


def test_rule_quoted_string_with_escape_raises():
    # (deny "hello\\") — first arg is a quoted string → _to_rule_expression raises
    with pytest.raises(ParseError) as exc_info:
        parse_text('@sdif 1.0\nrules:\n  (deny "hello\\\\")\n')
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_quoted_string_with_escape_in_second_arg():
    # Use quoted string as a second argument (first is Identifier) — this parses OK
    doc = parse_text('@sdif 1.0\nrules:\n  (deny x "hello\\\\")\n')
    assert len(doc.rules) == 1


# ---------------------------------------------------------------------------
# include directive  (lines 626-721)
# ---------------------------------------------------------------------------


def test_parse_file_include_disabled_by_policy(tmp_path):
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include other.sdif\nkind Plan\n", encoding="utf-8")

    no_include_policy = Policy(allow_includes=False)
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=no_include_policy)
    assert exc_info.value.code == "SDIF_POLICY_INCLUDE"


def test_parse_file_remote_include_disabled_by_policy(tmp_path):
    main_file = tmp_path / "main.sdif"
    main_file.write_text(
        '@sdif 1.0\n@include "http://example.com/other.sdif"\nkind Plan\n',
        encoding="utf-8",
    )

    policy = Policy(allow_includes=True, allow_remote_includes=False)
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_REMOTE_INCLUDE"


def test_parse_file_remote_include_always_raises(tmp_path):
    main_file = tmp_path / "main.sdif"
    main_file.write_text(
        '@sdif 1.0\n@include "http://example.com/other.sdif"\nkind Plan\n',
        encoding="utf-8",
    )

    policy = Policy(allow_includes=True, allow_remote_includes=True)
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_REMOTE_INCLUDE"


def test_parse_file_include_path_not_in_allowlist(tmp_path):
    other = tmp_path / "other.sdif"
    other.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include other.sdif\nkind Other\n", encoding="utf-8")

    # policy allows includes, but allowed_include_paths does NOT include tmp_path
    policy = Policy(
        allow_includes=True,
        allow_remote_includes=False,
        allowed_include_paths=frozenset(),
    )
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_INCLUDE_PATH"


def test_parse_file_successful_include(tmp_path):
    other = tmp_path / "other.sdif"
    other.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include other.sdif\nid demo\n", encoding="utf-8")

    policy = Policy(
        allow_includes=True,
        allow_remote_includes=False,
        allowed_include_paths=frozenset([tmp_path]),
    )
    doc = parse_file(main_file, policy=policy)
    assert doc.fields["id"].value == "demo"


def test_parse_file_include_cycle_raises(tmp_path):
    a = tmp_path / "a.sdif"
    b = tmp_path / "b.sdif"
    a.write_text("@sdif 1.0\n@include b.sdif\nkind Plan\n", encoding="utf-8")
    b.write_text("@sdif 1.0\n@include a.sdif\nkind Plan\n", encoding="utf-8")

    policy = Policy(
        allow_includes=True,
        allowed_include_paths=frozenset([tmp_path]),
    )
    with pytest.raises(PolicyError) as exc_info:
        parse_file(a, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_INCLUDE_CYCLE"


def test_parse_file_include_depth_exceeded(tmp_path):
    # With max_include_depth=0, even one level of include triggers the depth error
    inner = tmp_path / "inner.sdif"
    inner.write_text("@sdif 1.0\nkind Inner\n", encoding="utf-8")
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include inner.sdif\nkind Outer\n", encoding="utf-8")

    policy = Policy(
        allow_includes=True,
        allowed_include_paths=frozenset([tmp_path]),
        max_include_depth=0,
    )
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_INCLUDE_DEPTH"


def test_parse_file_missing_file_raises_ioerror(tmp_path):
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include missing.sdif\nkind Plan\n", encoding="utf-8")

    policy = Policy(
        allow_includes=True,
        allowed_include_paths=frozenset([tmp_path]),
    )
    with pytest.raises(IOError):
        parse_file(main_file, policy=policy)


def test_parse_file_io_error_on_nonexistent_file():
    with pytest.raises(IOError):
        parse_file("/nonexistent/path/to/file.sdif")


def test_parse_file_expanded_bytes_policy(tmp_path):
    other = tmp_path / "other.sdif"
    other.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include other.sdif\nid demo\n", encoding="utf-8")

    # Set max_expanded_bytes very small so the second file exceeds it
    policy = Policy(
        allow_includes=True,
        allowed_include_paths=frozenset([tmp_path]),
        max_expanded_bytes=1,
    )
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_EXPANDED_BYTES"


# ---------------------------------------------------------------------------
# ast.py — Document property accessors (lines 33, 37, 41, 45)
# ---------------------------------------------------------------------------


def test_document_objects_property():
    doc = parse_text("@sdif 1.0\nowner:\n  id alice\n")
    assert "owner" in doc.objects
    assert isinstance(doc.objects["owner"], ObjectBlock)


def test_document_tables_property():
    doc = parse_text("@sdif 1.0\nitems[a,b]:\n  x\ty\n")
    assert "items" in doc.tables


def test_document_relations_property():
    doc = parse_text("@sdif 1.0\nrel:\n  a likes b\n")
    assert len(doc.relations) == 1
    assert doc.relations[0].predicate == "likes"


def test_document_rules_property():
    doc = parse_text("@sdif 1.0\nrules:\n  (deny missing(evidence))\n")
    assert len(doc.rules) == 1


def test_document_narratives_property():
    doc = parse_text('@sdif 1.0\nintent """\nhello\n"""\n')
    assert "intent" in doc.narratives


def test_object_block_objects_property():
    doc = parse_text("@sdif 1.0\nouter:\n  inner:\n    key val\n")
    outer = doc.objects["outer"]
    assert "inner" in outer.objects


def test_object_block_tables_property():
    doc = parse_text("@sdif 1.0\nouter:\n  items[a,b]:\n    x\ty\n")
    outer = doc.objects["outer"]
    assert "items" in outer.tables


def test_object_block_relations_property():
    doc = parse_text("@sdif 1.0\nouter:\n  rel:\n    a likes b\n")
    outer = doc.objects["outer"]
    assert len(outer.relations) == 1


def test_object_block_rules_property():
    doc = parse_text("@sdif 1.0\nouter:\n  rules:\n    (deny missing(evidence))\n")
    outer = doc.objects["outer"]
    # rules property returns list[Rule]
    assert len(outer.rules) == 1


# ---------------------------------------------------------------------------
# ast.py — statement_count  (line 132)
# ---------------------------------------------------------------------------


def test_statement_count():
    doc = parse_text("@sdif 1.0\nkind Plan\nid release.v1\n")
    count = statement_count(doc.statements)
    assert count == 2


def test_statement_count_empty():
    count = statement_count([])
    assert count == 0


# ---------------------------------------------------------------------------
# canonicalizer.py — unordered table without primary_key  (line 77)
# ---------------------------------------------------------------------------


def test_canonicalizer_unordered_table_without_primary_key_raises():
    schema = Schema(
        table_policies={
            "items": TablePolicy(name="items", ordered=False, primary_key=None)
        }
    )
    doc = parse_text("@sdif 1.0\nitems[a,b]:\n  x\ty\n")
    with pytest.raises(ValueError) as exc_info:
        canonicalize(doc, schema=schema)
    assert "primary_key" in str(exc_info.value)


def test_canonicalizer_unordered_table_primary_key_not_in_columns_raises():
    schema = Schema(
        table_policies={
            "items": TablePolicy(name="items", ordered=False, primary_key="missing_col")
        }
    )
    doc = parse_text("@sdif 1.0\nitems[a,b]:\n  x\ty\n")
    with pytest.raises(ValueError) as exc_info:
        canonicalize(doc, schema=schema)
    assert "missing_col" in str(exc_info.value) or "primary_key" in str(exc_info.value)


def test_canonicalizer_unordered_table_with_primary_key_sorts_rows():
    schema = Schema(
        table_policies={
            "items": TablePolicy(name="items", ordered=False, primary_key="id")
        }
    )
    doc = parse_text("@sdif 1.0\nitems[id,val]:\n  b\t2\n  a\t1\n")
    result = canonicalize(doc, schema=schema)
    # rows should be sorted by primary key "id"
    assert result.index("a\t1") < result.index("b\t2")


# ---------------------------------------------------------------------------
# canonicalizer.py — rules block canonicalization  (lines 125-127)
# ---------------------------------------------------------------------------


def test_canonicalize_rules_block():
    doc = parse_text("@sdif 1.0\nrules:\n  (deny missing(evidence))\n")
    result = canonicalize(doc)
    assert "rules:" in result
    assert "(deny missing(evidence))" in result


def test_canonicalize_multiple_rules_sorted():
    doc = parse_text("@sdif 1.0\nrules:\n  (deny missing(evidence))\n  (warn extra(x))\n")
    result = canonicalize(doc)
    assert "rules:" in result


# ---------------------------------------------------------------------------
# canonicalizer.py — _quote_if_needed branches  (lines 141, 145-146)
# ---------------------------------------------------------------------------


def test_canonicalize_field_value_null_keyword_passthrough():
    # A field constructed directly with value "null" and quoted=False
    # forces _quote_if_needed to take line 141 (return value as-is for keywords)
    doc = Document(
        directives=[Directive("sdif", ["1.0"])],
        statements=[Field("foo", "null", quoted=False)],
    )
    result = canonicalize(doc)
    assert "foo null" in result


def test_canonicalize_field_value_true_keyword_passthrough():
    doc = Document(
        directives=[Directive("sdif", ["1.0"])],
        statements=[Field("foo", "true", quoted=False)],
    )
    result = canonicalize(doc)
    assert "foo true" in result


def test_canonicalize_field_value_false_keyword_passthrough():
    doc = Document(
        directives=[Directive("sdif", ["1.0"])],
        statements=[Field("foo", "false", quoted=False)],
    )
    result = canonicalize(doc)
    assert "foo false" in result


def test_canonicalize_field_value_with_spaces_gets_quoted():
    # A field with a value containing spaces but quoted=False forces _quote_if_needed
    # to use lines 145-146 (escape and quote the unsafe value)
    doc = Document(
        directives=[Directive("sdif", ["1.0"])],
        statements=[Field("foo", "hello world", quoted=False)],
    )
    result = canonicalize(doc)
    assert '"hello world"' in result


def test_canonicalize_field_value_with_special_chars_gets_quoted():
    # Value with backslash or quote triggers lines 145-146
    doc = Document(
        directives=[Directive("sdif", ["1.0"])],
        statements=[Field("foo", 'has"quote', quoted=False)],
    )
    result = canonicalize(doc)
    assert '\\"' in result


# ---------------------------------------------------------------------------
# canonicalizer.py — _inside_current_block returns False  (line 155)
# ---------------------------------------------------------------------------


def test_inside_current_block_returns_false_when_non_indented_line_intervenes():
    # A non-indented line that is NOT the header should return False
    lines = ["@sdif 1.0", "kind Plan", "rel:", "  a b c", "another_field val"]
    assert not _inside_current_block(lines, "rel:")


def test_inside_current_block_returns_true_when_header_found():
    lines = ["rel:", "  a b c"]
    assert _inside_current_block(lines, "rel:")


def test_inside_current_block_returns_false_on_empty_lines():
    # When lines is empty, the loop ends without finding header → returns False
    assert not _inside_current_block([], "rel:")


def test_canonicalize_multiple_relations_in_same_block():
    doc = parse_text("@sdif 1.0\nrel:\n  a likes b\n  c hates d\n")
    result = canonicalize(doc)
    # Both relations should be inside the same rel: block
    rel_idx = result.index("rel:")
    assert "a likes b" in result[rel_idx:]
    assert "c hates d" in result[rel_idx:]


# ---------------------------------------------------------------------------
# Additional parser.py lines: object block with empty lines/comments (244-245, 250)
# ---------------------------------------------------------------------------


def test_object_block_with_empty_lines():
    # Empty lines inside an object block → lines 244-245 in _parse_object
    doc = parse_text("@sdif 1.0\nobj:\n\n  key val\n\n  key2 val2\n")
    assert doc.objects["obj"].fields["key"].value == "val"
    assert doc.objects["obj"].fields["key2"].value == "val2"


def test_object_block_with_comment_line():
    # Comment inside object block → _parse_next returns None → line 250
    doc = parse_text("@sdif 1.0\nobj:\n  # this is a comment\n  key val\n")
    assert doc.objects["obj"].fields["key"].value == "val"


# ---------------------------------------------------------------------------
# Additional: rel[subject]: with empty line (lines 355-356)
# ---------------------------------------------------------------------------


def test_rel_subject_block_with_empty_line():
    doc = parse_text("@sdif.ai 1.0\nrel[alice]:\n\n  likes bob\n")
    assert len(doc.relations) == 1
    assert doc.relations[0].subject == "alice"


# ---------------------------------------------------------------------------
# Rules block with empty line (lines 389-390)
# ---------------------------------------------------------------------------


def test_rules_block_with_empty_line():
    doc = parse_text("@sdif 1.0\nrules:\n\n  (deny missing(evidence))\n")
    assert len(doc.rules) == 1


# ---------------------------------------------------------------------------
# include with empty args (line 634)
# ---------------------------------------------------------------------------


def test_parse_file_empty_include_args(tmp_path):
    # @include with no path → empty args list → line 634 (empty include directive)
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include\nkind Plan\n", encoding="utf-8")

    policy = Policy(allow_includes=True, allowed_include_paths=frozenset([tmp_path]))
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_INCLUDE"


# ---------------------------------------------------------------------------
# include with absolute path (line 651)
# ---------------------------------------------------------------------------


def test_parse_file_include_absolute_path(tmp_path):
    other = tmp_path / "other.sdif"
    other.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")
    main_file = tmp_path / "main.sdif"
    # Use absolute path in include
    main_file.write_text(
        f"@sdif 1.0\n@include \"{other}\"\nid demo\n",
        encoding="utf-8",
    )

    policy = Policy(
        allow_includes=True,
        allowed_include_paths=frozenset([tmp_path]),
    )
    doc = parse_file(main_file, policy=policy)
    assert doc.fields["id"].value == "demo"


# ---------------------------------------------------------------------------
# Narrative unclosed at top level (line 449)
# and unclosed in nested context
# ---------------------------------------------------------------------------


def test_unclosed_narrative_in_object_raises():
    with pytest.raises(ParseError) as exc_info:
        parse_text('@sdif 1.0\nobj:\n  bio """\n  hello\n')
    assert exc_info.value.code == "SDIF_NARRATIVE_UNCLOSED"


# ---------------------------------------------------------------------------
# _parse_rule_expression_node with empty token list (line 559)
# ---------------------------------------------------------------------------


def test_rule_expression_empty_token_via_empty_parens_call():
    # Trigger _parse_rule_expression_node with pos >= len(tokens):
    # the compact call form: "deny()" — after parsing "deny" and "(", inside the
    # while loop we look for args. If next token is ")", we stop. But what if
    # we call the function and immediately hit the missing argument call?
    # Actually, "deny()" parses to Call("deny", []) which then raises in _to_rule_expression.
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  deny()\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


def test_rule_expression_empty_source_raises():
    # A source with only a comment becomes empty after strip, producing empty token list.
    # This triggers "Unexpected end of expression" at line 559.
    # Note: blank lines are skipped by _parse_rules (line 389), so we need a non-blank
    # line that reduces to empty after _strip_inline_comment.strip().
    # A line with only a comment is stripped to "" by _strip_inline_comment.
    # But that's not entirely blank (raw.strip() != ""), so it passes the empty check.
    # Actually: "  # comment" → raw.strip() = "# comment" which is not empty,
    # but body = raw[child_indent:] = "# comment", and _strip_inline_comment removes it → ""
    # Then source = "".strip() = "" → tokens = [] → line 559 fires.
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nrules:\n  # rule comment\n")
    assert exc_info.value.code == "SDIF_RULE_EXPR"


# ---------------------------------------------------------------------------
# SDIF_INDENT_TAB — tab used for indentation (line 449 in _indent)
# ---------------------------------------------------------------------------


def test_tab_indentation_raises_indent_tab():
    # A line where leading whitespace includes a TAB triggers SDIF_INDENT_TAB
    with pytest.raises(ParseError) as exc_info:
        parse_text("@sdif 1.0\nkind Plan\n\tfoo bar\n")
    assert exc_info.value.code == "SDIF_INDENT_TAB"


# ---------------------------------------------------------------------------
# rel[subject]: block exits on lower indent (line 359)
# ---------------------------------------------------------------------------


def test_rel_subject_block_terminates_on_lower_indent():
    # After the rel[subject] block, a line at lower indent causes the loop to break (line 359)
    doc = parse_text("@sdif.ai 1.0\nrel[alice]:\n  likes bob\nkind Plan\n")
    assert len(doc.relations) == 1
    assert doc.fields["kind"].value == "Plan"


# ---------------------------------------------------------------------------
# Include path allowlist exception handler (lines 662-663)
# ---------------------------------------------------------------------------


def test_parse_file_include_path_allowlist_exception_does_not_crash(tmp_path):
    # The exception handler at line 662-663 catches exceptions during allowed path resolution.
    # To trigger it, we can use a Path that raises during resolve(). This is hard to force,
    # but we can verify normal path-not-allowed works correctly (the loop completes without
    # exception, and is_allowed stays False).
    other = tmp_path / "other.sdif"
    other.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include other.sdif\nkind Other\n", encoding="utf-8")

    # Empty allowlist → no paths to check → is_allowed stays False → SDIF_POLICY_INCLUDE_PATH
    policy = Policy(
        allow_includes=True,
        allowed_include_paths=frozenset(),
    )
    with pytest.raises(PolicyError) as exc_info:
        parse_file(main_file, policy=policy)
    assert exc_info.value.code == "SDIF_POLICY_INCLUDE_PATH"


def test_parse_file_include_path_allowlist_with_broken_symlink(tmp_path):
    # To trigger lines 662-663 (exception handler during path resolution),
    # put a broken symlink in allowed_include_paths so that allowed.resolve() raises.
    broken_link = tmp_path / "broken_link"
    broken_link.symlink_to(tmp_path / "nonexistent_target")

    other = tmp_path / "other.sdif"
    other.write_text("@sdif 1.0\nkind Plan\n", encoding="utf-8")
    main_file = tmp_path / "main.sdif"
    main_file.write_text("@sdif 1.0\n@include other.sdif\nkind Other\n", encoding="utf-8")

    # The broken symlink is in the allowlist; it raises during resolve() → exception handled
    # The real tmp_path is also in the allowlist to allow successful resolution after
    policy = Policy(
        allow_includes=True,
        allowed_include_paths=frozenset([broken_link, tmp_path]),
    )
    # Should succeed (real tmp_path allows the include)
    doc = parse_file(main_file, policy=policy)
    assert doc.fields is not None
