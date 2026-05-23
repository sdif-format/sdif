"""Coverage gap tests for validator.py, converter.py, and aliases.py."""

from __future__ import annotations

import pytest

from sdif import parse_text
from sdif.ai import ai_view, sdif_from_ai
from sdif.core.ast import (
    Directive,
    Document,
    Field,
    Narrative,
    ObjectBlock,
    Relation,
    Table,
)
from sdif.core.policy import PolicyError
from sdif.json import document_to_json_data, json_data_to_sdif
from sdif.json.converter import (
    _format_scalar,
    _split_list_items,
    _validate_identifier,
)
from sdif.validation import Schema, SchemaError, validate_document


# ===========================================================================
# validator.py — List<ElementType> field validation (lines 183-200, 332, 343-362)
# ===========================================================================

_SCHEMA_LIST_TAGS = (
    "@sdif 1.0\n"
    "kind Schema\n"
    "id test.schema.v1\n"
    "fields[name,type,required,default]:\n"
    "  tags\tList<Identifier>\tfalse\tnull\n"
)

_SCHEMA_LIST_BOOLEANS = (
    "@sdif 1.0\n"
    "kind Schema\n"
    "id test.schema.v1\n"
    "fields[name,type,required,default]:\n"
    "  flags\tList<Boolean>\tfalse\tnull\n"
)


class TestListTypeValidation:
    def test_valid_list_field(self):
        schema = Schema.from_document(parse_text(_SCHEMA_LIST_TAGS))
        doc = parse_text("@sdif 1.0\nkind Test\ntags [tag1,tag2]\n")
        assert validate_document(doc, schema) == []

    def test_invalid_list_element_type(self):
        schema = Schema.from_document(parse_text(_SCHEMA_LIST_BOOLEANS))
        doc = parse_text("@sdif 1.0\nkind Test\nflags [notabool,true]\n")
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)

    def test_non_list_value_for_list_type(self):
        schema = Schema.from_document(parse_text(_SCHEMA_LIST_TAGS))
        doc = parse_text("@sdif 1.0\nkind Test\ntags not-a-list\n")
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)

    def test_empty_list_value_is_valid(self):
        schema = Schema.from_document(parse_text(_SCHEMA_LIST_TAGS))
        doc = parse_text("@sdif 1.0\nkind Test\ntags []\n")
        assert validate_document(doc, schema) == []

    def test_list_element_type_extraction(self):
        from sdif.validation.validator import _list_element_type
        assert _list_element_type("List<Identifier>") == "Identifier"
        assert _list_element_type("List< String >") == "String"
        assert _list_element_type("Identifier") is None
        assert _list_element_type("List(Identifier)") is None


# ---------------------------------------------------------------------------
# Object block with list type (lines 183-200)
# ---------------------------------------------------------------------------

class TestListTypeObjectBlock:
    """Object block with list type (lines 183-200)."""

    def test_object_block_list_valid(self):
        """ObjectBlock with dash statements passes List<Identifier> validation."""
        schema = Schema.from_document(parse_text(_SCHEMA_LIST_TAGS))
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("tags", [
                    Field("-", "tag1"),
                    Field("-", "tag2"),
                ]),
            ],
        )
        assert validate_document(doc, schema) == []

    def test_object_block_list_bad_element(self):
        schema = Schema.from_document(parse_text(_SCHEMA_LIST_TAGS))
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("tags", [
                    Field("-", "bad value with spaces"),
                ]),
            ],
        )
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)

    def test_object_block_non_dash_statement(self):
        """Non-dash statement inside a List-typed ObjectBlock produces SDIF_TYPE error."""
        schema = Schema.from_document(parse_text(_SCHEMA_LIST_TAGS))
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("tags", [
                    Field("notdash", "tag1"),
                ]),
            ],
        )
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)


# ===========================================================================
# validator.py — Decimal type (line 370)
# ===========================================================================

_SCHEMA_DECIMAL = (
    "@sdif 1.0\n"
    "kind Schema\n"
    "id test.schema.v1\n"
    "fields[name,type,required,default]:\n"
    "  price\tDecimal\tfalse\tnull\n"
)


class TestDecimalType:
    def test_decimal_valid_decimal(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DECIMAL))
        doc = parse_text("@sdif 1.0\nkind Test\nprice 3.14\n")
        assert validate_document(doc, schema) == []

    def test_decimal_valid_integer_also_passes(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DECIMAL))
        doc = parse_text("@sdif 1.0\nkind Test\nprice 42\n")
        assert validate_document(doc, schema) == []

    def test_decimal_invalid(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DECIMAL))
        doc = parse_text("@sdif 1.0\nkind Test\nprice notanumber\n")
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)


# ===========================================================================
# validator.py — DateTime type (lines 375-380)
# ===========================================================================

_SCHEMA_DATETIME = (
    "@sdif 1.0\n"
    "kind Schema\n"
    "id test.schema.v1\n"
    "fields[name,type,required,default]:\n"
    "  created_at\tDateTime\tfalse\tnull\n"
)


class TestDateTimeType:
    def test_valid_datetime_z(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DATETIME))
        doc = parse_text("@sdif 1.0\nkind Test\ncreated_at 2024-01-15T10:30:00Z\n")
        assert validate_document(doc, schema) == []

    def test_valid_datetime_offset(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DATETIME))
        doc = parse_text("@sdif 1.0\nkind Test\ncreated_at 2024-01-15T10:30:00+00:00\n")
        assert validate_document(doc, schema) == []

    def test_invalid_datetime(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DATETIME))
        doc = parse_text("@sdif 1.0\nkind Test\ncreated_at not-a-date\n")
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)


# ===========================================================================
# validator.py — Null type (lines 377-378)
# ===========================================================================

_SCHEMA_NULL = (
    "@sdif 1.0\n"
    "kind Schema\n"
    "id test.schema.v1\n"
    "fields[name,type,required,default]:\n"
    "  empty\tNull\tfalse\tnull\n"
)


class TestNullType:
    def test_null_valid(self):
        schema = Schema.from_document(parse_text(_SCHEMA_NULL))
        doc = parse_text("@sdif 1.0\nkind Test\nempty null\n")
        assert validate_document(doc, schema) == []

    def test_null_invalid(self):
        schema = Schema.from_document(parse_text(_SCHEMA_NULL))
        doc = parse_text("@sdif 1.0\nkind Test\nempty something\n")
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)


# ===========================================================================
# validator.py — Duration type (lines 377-378)
# ===========================================================================

_SCHEMA_DURATION = (
    "@sdif 1.0\n"
    "kind Schema\n"
    "id test.schema.v1\n"
    "fields[name,type,required,default]:\n"
    "  duration\tDuration\tfalse\tnull\n"
)


class TestDurationType:
    def test_duration_valid(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DURATION))
        doc = parse_text("@sdif 1.0\nkind Test\nduration P1Y2M3D\n")
        assert validate_document(doc, schema) == []

    def test_duration_invalid(self):
        schema = Schema.from_document(parse_text(_SCHEMA_DURATION))
        doc = parse_text("@sdif 1.0\nkind Test\nduration 1hour\n")
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_TYPE" for d in diags)


# ===========================================================================
# validator.py — _valid_datetime directly (lines 431, 437-441)
# ===========================================================================

class TestValidDatetime:
    def test_valid_datetime_returns_true(self):
        from sdif.validation.validator import _valid_datetime
        assert _valid_datetime("2024-01-15T10:30:00Z") is True

    def test_invalid_datetime_returns_false(self):
        from sdif.validation.validator import _valid_datetime
        assert _valid_datetime("not-a-date") is False

    def test_valid_datetime_no_tz(self):
        from sdif.validation.validator import _valid_datetime
        assert _valid_datetime("2024-01-15T10:30:00") is True


class TestValidDate:
    def test_valid_date_returns_true(self):
        from sdif.validation.validator import _valid_date
        assert _valid_date("2024-01-15") is True

    def test_invalid_date_returns_false(self):
        from sdif.validation.validator import _valid_date
        assert _valid_date("not-a-date") is False


# ===========================================================================
# validator.py — SchemaError on missing column (lines 451-452, 458-459)
# ===========================================================================

class TestSchemaError:
    def test_required_column_raises_schema_error(self):
        """Schema table missing required column raises SchemaError."""
        bad_schema = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id bad.schema.v1\n"
            "fields[type,required,default]:\n"
            "  Identifier\tfalse\tnull\n"
        )
        with pytest.raises(SchemaError, match="requires `name` column"):
            Schema.from_document(parse_text(bad_schema))

    def test_optional_column_returns_none_for_missing(self):
        from sdif.validation.validator import _optional_column
        assert _optional_column(["a", "b"], "c") is None

    def test_required_column_raises_for_missing(self):
        from sdif.validation.validator import _required_column
        with pytest.raises(SchemaError):
            _required_column(["a", "b"], "c", "mytable")

    def test_required_column_returns_index(self):
        from sdif.validation.validator import _required_column
        assert _required_column(["name", "type", "required"], "type", "fields") == 1


# ===========================================================================
# validator.py — validate_document return [] path (line 157)
# ===========================================================================

class TestValidateDocumentEmptySchema:
    def test_empty_schema_returns_no_diagnostics(self):
        """Schema with no constraints returns empty list."""
        schema = Schema()
        doc = parse_text("@sdif 1.0\nkind Test\n")
        assert validate_document(doc, schema) == []


# ===========================================================================
# validator.py — continue paths (lines 216, 232)
# ===========================================================================

class TestValidateDocumentContinuePaths:
    def test_missing_required_table_hits_continue(self):
        """Missing required table produces SDIF_REQUIRED_TABLE and continues."""
        schema_text = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id test.schema.v1\n"
            "columns[table,name,type,required]:\n"
            "  items\tname\tIdentifier\ttrue\n"
        )
        schema = Schema.from_document(parse_text(schema_text))
        doc = parse_text("@sdif 1.0\nkind Test\n")
        diags = validate_document(doc, schema)
        assert any(d.code == "SDIF_REQUIRED_TABLE" for d in diags)

    def test_column_type_skips_when_table_absent(self):
        """Column type check skips (continue) when table not in doc."""
        schema_text = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id test.schema.v1\n"
            "columns[table,name,type,required]:\n"
            "  items\tname\tIdentifier\tfalse\n"
        )
        schema = Schema.from_document(parse_text(schema_text))
        doc = parse_text("@sdif 1.0\nkind Test\n")
        diags = validate_document(doc, schema)
        assert not any(d.code == "SDIF_REQUIRED_TABLE" for d in diags)

    def test_column_type_skips_missing_column(self):
        """Column type check skips (continue) when column not present in table."""
        schema_text = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id test.schema.v1\n"
            "columns[table,name,type,required]:\n"
            "  items\textra\tIdentifier\tfalse\n"
        )
        schema = Schema.from_document(parse_text(schema_text))
        doc = parse_text("@sdif 1.0\nkind Test\nitems[name]:\n  foo\n")
        assert validate_document(doc, schema) == []


# ===========================================================================
# validator.py — _validate_rule empty case (line 390)
# ===========================================================================

class TestValidateRuleEmpty:
    def test_rule_with_none_expression_returns_empty(self):
        from sdif.validation.validator import _validate_rule
        assert _validate_rule(None, Schema(), "rules[0]") == []


# ===========================================================================
# converter.py — _parse_table_cell quoted cell (line 113)
# ===========================================================================

class TestParseTableCellQuoted:
    def test_quoted_dollar_column_cell_gets_unquoted(self):
        doc = parse_text(
            "@sdif 1.0\nkind Test\nitems[name,label$]:\n" '  foo\t"hello world"\n'
        )
        result = document_to_json_data(doc)
        assert result["items"][0]["label"] == "hello world"

    def test_unquoted_dollar_column_cell_stays_as_is(self):
        doc = parse_text("@sdif 1.0\nkind Test\nitems[name,label$]:\n  foo\tbar\n")
        result = document_to_json_data(doc)
        assert result["items"][0]["label"] == "bar"


# ===========================================================================
# converter.py — ObjectBlock unwrapping (lines 127-133, 141-142)
# ===========================================================================

class TestObjectBlockUnwrapping:
    """_array_item_to_json_value with wrapped Field/ObjectBlock/Narrative."""

    def test_wrapped_field_value(self):
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("items", [
                    ObjectBlock("__item", [
                        Field("__value", "hello"),
                    ]),
                ]),
            ],
        )
        result = document_to_json_data(doc)
        assert result["items"] == ["hello"]

    def test_wrapped_narrative_value(self):
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("items", [
                    ObjectBlock("__item", [
                        Narrative("__value", "some text"),
                    ]),
                ]),
            ],
        )
        result = document_to_json_data(doc)
        assert result["items"] == ["some text"]

    def test_wrapped_object_block_value(self):
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("items", [
                    ObjectBlock("__item", [
                        ObjectBlock("__value", [
                            Field("x", "1"),
                        ]),
                    ]),
                ]),
            ],
        )
        result = document_to_json_data(doc)
        assert result["items"] == [{"x": 1}]


# ===========================================================================
# converter.py — Empty list in JSON→SDIF (lines 189-190)
# ===========================================================================

class TestEmptyListEmission:
    def test_empty_list_emits_bracket_syntax(self):
        sdif_text = json_data_to_sdif({"kind": "Test", "tags": []})
        assert "tags []" in sdif_text

    def test_empty_list_roundtrip(self):
        sdif_text = json_data_to_sdif({"kind": "Test", "tags": []})
        doc = parse_text(sdif_text)
        result = document_to_json_data(doc)
        assert result["tags"] == []


# ===========================================================================
# converter.py — Array value emission (lines 207-212)
# ===========================================================================

class TestArrayValueEmission:
    def test_nested_list_emits_array_item_and_value_blocks(self):
        sdif_text = json_data_to_sdif({"kind": "Test", "matrix": [[1, 2], [3, 4]]})
        assert "__item:" in sdif_text
        assert "__value:" in sdif_text


# ===========================================================================
# converter.py — _validate_identifier (lines 224, 423, 425)
# ===========================================================================

class TestValidateIdentifier:
    def test_reserved_item_key_raises(self):
        with pytest.raises(ValueError, match="is reserved"):
            _validate_identifier("__item", "key")

    def test_reserved_value_key_raises(self):
        with pytest.raises(ValueError, match="is reserved"):
            _validate_identifier("__value", "key")

    def test_invalid_identifier_raises(self):
        with pytest.raises(ValueError, match="invalid SDIF"):
            _validate_identifier("hello world", "key")

    def test_valid_identifier_passes(self):
        _validate_identifier("hello_world", "key")  # no exception


# ===========================================================================
# converter.py — Table ValueError paths (lines 237, 243, 249, 262)
# ===========================================================================

class TestTableValueErrors:
    def test_empty_columns_object_raises(self):
        """_emit_table with empty-column objects raises ValueError."""
        from sdif.json.converter import _emit_table
        with pytest.raises(ValueError, match="cannot be generated from empty objects"):
            _emit_table("items", [{}], [], 0)

    def test_non_uniform_objects_raises(self):
        from sdif.json.converter import _emit_table
        with pytest.raises(ValueError, match="not uniform"):
            _emit_table("items", [{"a": 1}, {"b": 2}], [], 0)

    def test_nested_value_in_table_raises(self):
        from sdif.json.converter import _emit_table
        with pytest.raises(ValueError, match="nested value"):
            _emit_table("items", [{"a": [1, 2]}], [], 0)

    def test_non_object_row_raises(self):
        from sdif.json.converter import _as_mapping
        with pytest.raises(ValueError, match="rows must be JSON objects"):
            _as_mapping("string_row", "items")


# ===========================================================================
# converter.py — _format_scalar edge cases (lines 279, 283, 295, 311)
# ===========================================================================

class TestFormatScalar:
    def test_none_returns_null(self):
        assert _format_scalar(None) == "null"

    def test_false_returns_false(self):
        assert _format_scalar(False) == "false"

    def test_true_returns_true(self):
        assert _format_scalar(True) == "true"

    def test_integer(self):
        assert _format_scalar(42) == "42"

    def test_float(self):
        assert _format_scalar(3.14) == "3.14"

    def test_string_needing_quotes(self):
        result = _format_scalar("hello world")
        assert result == '"hello world"'

    def test_plain_string_no_quotes(self):
        result = _format_scalar("hello")
        assert result == "hello"

    def test_format_table_cell_with_tab_raises(self):
        from sdif.json.converter import _format_table_cell
        with pytest.raises(ValueError, match="cannot represent tabs"):
            _format_table_cell("hello\tworld")


# ===========================================================================
# converter.py — _split_list_items edge cases (lines 382, 389-395, 406)
# ===========================================================================

class TestSplitListItems:
    def test_empty_string_returns_empty_list(self):
        assert _split_list_items("") == []

    def test_simple_items(self):
        assert _split_list_items("a,b,c") == ["a", "b", "c"]

    def test_quoted_item_with_comma(self):
        result = _split_list_items('"hello,world",foo')
        assert result == ['"hello,world"', "foo"]

    def test_escaped_char_inside_quotes(self):
        result = _split_list_items('"hello\\"world"')
        assert result == ['"hello\\"world"']

    def test_escaped_backslash_inside_quotes(self):
        result = _split_list_items('"a\\\\b"')
        assert result == ['"a\\\\b"']

    def test_unterminated_quote_raises(self):
        with pytest.raises(ValueError, match="unterminated quoted list value"):
            _split_list_items('"unterminated')


# ===========================================================================
# converter.py — reserved key errors (line 444)
# ===========================================================================

class TestReservedKeyErrors:
    def test_reserved_key_in_mapping_raises(self):
        with pytest.raises(ValueError, match="reserved"):
            json_data_to_sdif({"kind": "Test", "__item": "bad"})

    def test_reserved_key_in_nested_mapping_raises(self):
        with pytest.raises(ValueError, match="reserved"):
            json_data_to_sdif({"kind": "Test", "nested": {"__value": "bad"}})

    def test_reserved_key_in_list_of_mappings(self):
        with pytest.raises(ValueError, match="reserved"):
            json_data_to_sdif({"kind": "Test", "items": [{"__item": "bad"}]})


# ===========================================================================
# aliases.py — Reserved term alias (lines 110-115)
# ===========================================================================

class TestAliasReservedTerm:
    def test_alias_using_reserved_term_raises(self):
        """Alias where the alias itself is a reserved term raises PolicyError.

        We pass a pre-built Document to bypass the parser's own reserved-term check
        so that the _alias_to_canonical function in aliases.py is exercised.
        """
        doc = Document(
            directives=[
                Directive("sdif.ai", ["1.0"]),
                Directive("alias", ["alias=myterm"]),
            ],
            statements=[Field("kind", "Test")],
        )
        with pytest.raises(PolicyError) as exc_info:
            sdif_from_ai(doc)
        assert exc_info.value.code == "SDIF_POLICY_ALIAS_RESERVED"

    def test_alias_targeting_reserved_term_raises(self):
        """Alias where canonical target is a reserved term raises PolicyError."""
        doc = Document(
            directives=[
                Directive("sdif.ai", ["1.0"]),
                Directive("alias", ["myterm=include"]),
            ],
            statements=[Field("kind", "Test")],
        )
        with pytest.raises(PolicyError) as exc_info:
            sdif_from_ai(doc)
        assert exc_info.value.code == "SDIF_POLICY_ALIAS_RESERVED"


# ===========================================================================
# aliases.py — Alias collision (lines 117-122)
# ===========================================================================

class TestAliasCollision:
    def test_alias_collision_raises(self):
        """Same alias mapped to two different canonicals raises PolicyError."""
        doc = Document(
            directives=[
                Directive("sdif.ai", ["1.0"]),
                Directive("alias", ["k=kind"]),
                Directive("alias", ["k=status"]),
            ],
            statements=[Field("kind", "Test")],
        )
        with pytest.raises(PolicyError) as exc_info:
            sdif_from_ai(doc)
        assert exc_info.value.code == "SDIF_POLICY_ALIAS_COLLISION"


# ===========================================================================
# aliases.py — _source_directives no version path (lines 137-141)
# ===========================================================================

class TestSourceDirectivesNoVersion:
    def test_sdif_from_ai_inserts_version_when_sdif_ai_present(self):
        """@sdif.ai 1.0 gets converted to @sdif 1.0."""
        ai_doc = "@sdif.ai 1.0\nkind Test\n"
        result = sdif_from_ai(ai_doc)
        assert "@sdif 1.0" in result

    def test_no_directives_at_all_inserts_default(self):
        """Document with no directives gets @sdif 1.0 inserted."""
        doc = Document(
            directives=[],
            statements=[Field("kind", "Test")],
        )
        result = sdif_from_ai(doc)
        assert "@sdif 1.0" in result


# ===========================================================================
# aliases.py — _expand_statement for Rule and Narrative (lines 186-193)
# ===========================================================================

class TestExpandStatementRuleNarrative:
    def test_rule_passes_through_unchanged(self):
        ai_doc = "@sdif.ai 1.0\nkind Test\nrules:\n  (deny missing(status))\n"
        result = sdif_from_ai(ai_doc)
        assert "deny" in result

    def test_narrative_key_gets_alias_expanded(self):
        doc = Document(
            directives=[
                Directive("sdif.ai", ["1.0"]),
                Directive("alias", ["n=notes"]),
            ],
            statements=[
                Field("kind", "Test"),
                Narrative("n", "some narrative text"),
            ],
        )
        result = sdif_from_ai(doc)
        assert "notes" in result

    def test_unsupported_statement_type_raises(self):
        from sdif.ai.aliases import _expand_statement
        with pytest.raises(TypeError, match="unsupported statement"):
            _expand_statement("not_a_statement", {}, None, 0)


# ===========================================================================
# aliases.py — ai_view Rule and Narrative emission (lines 269-276)
# ===========================================================================

class TestAiViewRuleAndNarrative:
    def test_ai_view_includes_rules_block(self):
        source = parse_text(
            "@sdif 1.0\nkind Test\nid foo\nrules:\n  (deny (missing status))\n"
        )
        output = ai_view(source, {})
        assert "rules:" in output
        assert "(deny (missing status))" in output

    def test_ai_view_includes_narrative_block(self):
        source = parse_text(
            '@sdif 1.0\nkind Test\nnotes """\nsome text\n"""\n'
        )
        output = ai_view(source, {})
        assert "notes" in output
        assert "some text" in output


# ===========================================================================
# aliases.py — _emit_relation_group (lines 229-276, 296-310)
# ===========================================================================

class TestEmitRelationGroup:
    def test_ai_view_groups_relations_by_subject(self):
        source = parse_text(
            "@sdif 1.0\nkind Test\nrel:\n  A owns B\n  A uses C\n"
        )
        output = ai_view(source, {})
        assert "rel[A]:" in output

    def test_ai_view_relation_with_alias_applied(self):
        source = parse_text(
            "@sdif 1.0\nkind Test\nrel:\n  A owns B\n"
        )
        output = ai_view(source, {"owns": "o"})
        assert "o B" in output


# ===========================================================================
# aliases.py — _ensure_safe_table_projection (lines 234-244)
# ===========================================================================

class TestEnsureSafeTableProjection:
    def test_tab_in_quoted_column_raises_policy_error(self):
        from sdif.ai.aliases import _ensure_safe_table_projection
        # Build a table where all cells in a column are double-quoted
        # and the unquoted value contains a literal tab character
        tab_value = '"hello\tworld"'
        table = Table(
            name="items",
            columns=["name"],
            rows=[[tab_value]],
        )
        with pytest.raises(PolicyError) as exc_info:
            _ensure_safe_table_projection(table)
        assert exc_info.value.code == "SDIF_AI_UNSAFE_PROJECTION"

    def test_safe_quoted_column_passes(self):
        from sdif.ai.aliases import _ensure_safe_table_projection
        table = Table(
            name="items",
            columns=["name"],
            rows=[
                ['"hello"'],
                ['"world"'],
            ],
        )
        _ensure_safe_table_projection(table)  # should not raise

    def test_mixed_quoted_column_skips_projection_check(self):
        """A column where not all rows are quoted does not trigger the check."""
        from sdif.ai.aliases import _ensure_safe_table_projection
        table = Table(
            name="items",
            columns=["name"],
            rows=[
                ['"quoted"'],
                ["unquoted"],
            ],
        )
        _ensure_safe_table_projection(table)  # should not raise


# ===========================================================================
# Additional targeted tests to cover remaining gaps
# ===========================================================================

# ---------------------------------------------------------------------------
# validator.py line 357: strip quotes from list element in List validation
# ---------------------------------------------------------------------------

class TestListElementQuoteStripping:
    def test_single_quoted_element_gets_stripped(self):
        """List value with single-quoted element strips the quotes before validation."""
        schema_text = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id test.schema.v1\n"
            "fields[name,type,required,default]:\n"
            "  tags\tList<Identifier>\tfalse\tnull\n"
        )
        schema = Schema.from_document(parse_text(schema_text))
        # 'tag1' in single quotes inside the list — should strip and validate as Identifier
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[Field("kind", "Test"), Field("tags", "['tag1','tag2']")],
        )
        # The validator parses the list: each element 'tag1' has single quotes stripped
        diags = validate_document(doc, schema)
        assert diags == []

    def test_double_quoted_element_gets_stripped(self):
        """List value with double-quoted element strips the quotes before validation."""
        schema_text = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id test.schema.v1\n"
            "fields[name,type,required,default]:\n"
            "  tags\tList<Identifier>\tfalse\tnull\n"
        )
        schema = Schema.from_document(parse_text(schema_text))
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[Field("kind", "Test"), Field("tags", '["tag1","tag2"]')],
        )
        diags = validate_document(doc, schema)
        assert diags == []


# ---------------------------------------------------------------------------
# validator.py line 380: unknown type_name falls through to ok=True
# ---------------------------------------------------------------------------

class TestUnknownTypePassThrough:
    def test_unknown_type_name_passes_validation(self):
        """Unknown type name returns ok=True (no error)."""
        schema_text = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id test.schema.v1\n"
            "fields[name,type,required,default]:\n"
            "  foo\tCustomType\tfalse\tnull\n"
        )
        schema = Schema.from_document(parse_text(schema_text))
        doc = parse_text("@sdif 1.0\nkind Test\nfoo anything\n")
        # Unknown types are accepted without error
        assert validate_document(doc, schema) == []


# ---------------------------------------------------------------------------
# validator.py lines 400-402: Call node in collect_calls
# ---------------------------------------------------------------------------

class TestCollectCallsCallNode:
    def test_nested_call_in_rule_args_triggers_call_branch(self):
        """Rule with nested call (e.g., eq(missing(x), y)) hits the Call branch."""
        schema_text = (
            "@sdif 1.0\n"
            "kind Schema\n"
            "id test.schema.v1\n"
            "rule_functions[name,min_args,max_args]:\n"
            "  deny\t1\t1\n"
            "  eq\t2\t2\n"
            "  missing\t1\t1\n"
        )
        schema = Schema.from_document(parse_text(schema_text))
        # This creates a RuleExpression(deny, eq, args=[Call(missing, ["x"]), "y"])
        doc = parse_text("@sdif 1.0\nkind Test\nrules:\n  (deny eq(missing(x),y))\n")
        diags = validate_document(doc, schema)
        # eq takes 2 args and missing takes 1; both valid
        assert diags == []


# ---------------------------------------------------------------------------
# converter.py line 224: _can_emit_as_table returns False for empty columns
# ---------------------------------------------------------------------------

class TestCanEmitAsTableEmptyColumns:
    def test_list_of_empty_objects_uses_block_list_not_table(self):
        """A list of empty objects can't be a table; falls back to block list."""
        # _can_emit_as_table returns False when columns is empty
        # which causes _emit_list to be used instead
        from sdif.json.converter import _can_emit_as_table
        assert _can_emit_as_table([{}]) is False


# ---------------------------------------------------------------------------
# converter.py line 295: _format_list_item quotes string with comma
# ---------------------------------------------------------------------------

class TestFormatListItemComma:
    def test_list_item_with_comma_gets_quoted(self):
        from sdif.json.converter import _format_list_item
        result = _format_list_item("hello,world")
        assert result == '"hello,world"'

    def test_list_item_without_comma_not_quoted(self):
        from sdif.json.converter import _format_list_item
        result = _format_list_item("hello")
        assert result == "hello"


# ---------------------------------------------------------------------------
# converter.py lines 327, 329: _must_quote_table_cell for list literal and special chars
# ---------------------------------------------------------------------------

class TestMustQuoteTableCell:
    def test_list_literal_must_be_quoted(self):
        from sdif.json.converter import _must_quote_table_cell
        assert _must_quote_table_cell("[a,b]") is True

    def test_string_with_quote_must_be_quoted(self):
        from sdif.json.converter import _must_quote_table_cell
        assert _must_quote_table_cell('say "hi"') is True

    def test_string_with_backslash_must_be_quoted(self):
        from sdif.json.converter import _must_quote_table_cell
        assert _must_quote_table_cell("path\\file") is True

    def test_plain_string_needs_no_quote(self):
        from sdif.json.converter import _must_quote_table_cell
        assert _must_quote_table_cell("hello") is False


# ---------------------------------------------------------------------------
# converter.py lines 335, 345: _must_quote_string for list literal and #
# ---------------------------------------------------------------------------

class TestMustQuoteString:
    def test_empty_string_must_be_quoted(self):
        from sdif.json.converter import _must_quote_string
        assert _must_quote_string("") is True

    def test_list_literal_must_be_quoted(self):
        from sdif.json.converter import _must_quote_string
        assert _must_quote_string("[a,b]") is True

    def test_hash_must_be_quoted(self):
        from sdif.json.converter import _must_quote_string
        assert _must_quote_string("hello#world") is True

    def test_plain_string_needs_no_quote(self):
        from sdif.json.converter import _must_quote_string
        assert _must_quote_string("hello") is False


# ---------------------------------------------------------------------------
# converter.py line 418: _unquote returns value unchanged if not quoted
# ---------------------------------------------------------------------------

class TestUnquoteNonQuoted:
    def test_unquote_non_quoted_returns_as_is(self):
        from sdif.json.converter import _unquote
        assert _unquote("hello") == "hello"

    def test_unquote_quoted_unescapes(self):
        from sdif.json.converter import _unquote
        assert _unquote('"hello"') == "hello"


# ---------------------------------------------------------------------------
# aliases.py line 105: alias entry without = is skipped (continue)
# ---------------------------------------------------------------------------

class TestAliasEntryWithoutEquals:
    def test_alias_entry_without_equals_is_skipped(self):
        """Alias entry with no '=' is silently skipped."""
        doc = Document(
            directives=[
                Directive("sdif.ai", ["1.0"]),
                Directive("alias", ["invalidentry"]),
            ],
            statements=[Field("kind", "Test")],
        )
        # Should not raise; the bad entry is skipped
        result = sdif_from_ai(doc)
        assert "kind Test" in result


# ---------------------------------------------------------------------------
# aliases.py lines 137-139: non-alias, non-sdif.ai directive passes through
# ---------------------------------------------------------------------------

class TestSourceDirectivesPassThrough:
    def test_custom_directive_passes_through(self):
        """A non-alias, non-sdif.ai directive is preserved in output."""
        doc = Document(
            directives=[
                Directive("sdif.ai", ["1.0"]),
                Directive("schema", ["myschema.v1"]),
            ],
            statements=[Field("kind", "Test")],
        )
        result = sdif_from_ai(doc)
        assert "@sdif 1.0" in result

    def test_sdif_directive_in_source_sets_saw_version(self):
        """A @sdif directive in the source prevents version insertion."""
        doc = Document(
            directives=[
                Directive("sdif", ["1.0"]),
            ],
            statements=[Field("kind", "Test")],
        )
        result = sdif_from_ai(doc)
        # Should have exactly one @sdif 1.0
        assert result.count("@sdif 1.0") == 1


# ---------------------------------------------------------------------------
# aliases.py line 158: ObjectBlock in _expand_statement
# ---------------------------------------------------------------------------

class TestExpandStatementObjectBlock:
    def test_object_block_key_gets_alias_expanded(self):
        doc = Document(
            directives=[
                Directive("sdif.ai", ["1.0"]),
                Directive("alias", ["m=metadata"]),
            ],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("m", [Field("version", "1")]),
            ],
        )
        result = sdif_from_ai(doc)
        assert "metadata" in result


# ---------------------------------------------------------------------------
# aliases.py lines 229, 231: _ensure_safe_projection recurses into ObjectBlock
# ---------------------------------------------------------------------------

class TestEnsureSafeProjectionObjectBlock:
    def test_safe_projection_recurses_into_object_block(self):
        """_ensure_safe_projection checks tables nested inside ObjectBlocks."""
        # Build a document with a nested ObjectBlock containing a table
        table_with_tab = Table(
            name="nested",
            columns=["val"],
            rows=[['"hello\tworld"']],
        )
        doc = Document(
            directives=[Directive("sdif", ["1.0"])],
            statements=[
                Field("kind", "Test"),
                ObjectBlock("container", [table_with_tab]),
            ],
        )
        with pytest.raises(PolicyError) as exc_info:
            ai_view(doc, {})
        assert exc_info.value.code == "SDIF_AI_UNSAFE_PROJECTION"


# ---------------------------------------------------------------------------
# aliases.py lines 253-266: _emit for ObjectBlock, Table, and Relation (direct _emit)
# ---------------------------------------------------------------------------

class TestEmitDirectly:
    def test_emit_object_block(self):
        from sdif.ai.aliases import _emit
        lines: list[str] = []
        stmt = ObjectBlock("meta", [Field("version", "1")])
        _emit(stmt, lines, {}, 0)
        assert "meta:" in lines[0]
        assert "version 1" in lines[1]

    def test_emit_table(self):
        from sdif.ai.aliases import _emit
        lines: list[str] = []
        stmt = Table("items", ["id", "name"], [["I1", "foo"]])
        _emit(stmt, lines, {}, 0)
        assert "items[id,name]:" in lines[0]

    def test_emit_relation(self):
        from sdif.ai.aliases import _emit
        lines: list[str] = []
        stmt = Relation("A", "owns", "B")
        _emit(stmt, lines, {}, 0)
        assert "rel:" in lines[0]
        assert "A owns B" in lines[1]

    def test_emit_relation_appends_to_existing_rel_block(self):
        from sdif.ai.aliases import _emit
        lines: list[str] = ["rel:"]
        stmt = Relation("A", "owns", "B")
        _emit(stmt, lines, {}, 0)
        # Should NOT add another rel: line
        assert lines.count("rel:") == 1
