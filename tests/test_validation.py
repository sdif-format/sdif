from sdif import parse_text
import pytest

from sdif.validation import Schema, SchemaError, validate_document


SCHEMA = """
@sdif 0.1
kind Schema
id example.plan.v1
for_kind Plan
fields[name,type,required,default]:
  kind\tIdentifier\ttrue\tnull
  id\tIdentifier\ttrue\tnull
  title\tString\ttrue\tnull
  status\tEnum(open,closed)\tfalse\topen
columns[table,name,type,required]:
  milestones\tid\tIdentifier\ttrue
  milestones\tstatus\tEnum(done,pending)\ttrue
"""


def test_schema_parser_extracts_required_fields_and_table_columns():
    schema = Schema.from_document(parse_text(SCHEMA))

    assert schema.required_fields == {"kind", "id", "title"}
    assert schema.required_table_columns["milestones"] == {"id", "status"}


def test_validator_reports_missing_required_fields_and_table_columns():
    schema = Schema.from_document(parse_text(SCHEMA))
    doc = parse_text("""
@sdif 0.1
kind Plan
id demo
milestones[id]:
  R1
""")

    diagnostics = validate_document(doc, schema)

    assert [(d.code, d.path) for d in diagnostics] == [
        ("SDIF_REQUIRED_FIELD", "title"),
        ("SDIF_REQUIRED_COLUMN", "milestones.status"),
    ]
    assert all(d.severity == "error" for d in diagnostics)


def test_schema_parser_extracts_relation_policies():
    schema = Schema.from_document(
        parse_text("""
@sdif 0.1
kind Schema
relations[predicate,subject_type,object_type,required]:
  depends_on	Identifier	Identifier	true
  describes	Identifier	String	false
""")
    )

    assert set(schema.relation_policies) == {"depends_on", "describes"}
    assert schema.relation_policies["depends_on"].required is True
    assert schema.relation_policies["describes"].object_type == "String"


def test_validator_reports_unknown_relation_predicate_and_missing_required_relation():
    schema = Schema.from_document(
        parse_text("""
@sdif 0.1
kind Schema
relations[predicate,subject_type,object_type,required]:
  depends_on	Identifier	Identifier	true
  emits	Identifier	Path	false
""")
    )
    doc = parse_text("""
@sdif 0.1
kind Plan
rel:
  release.v2 unknown_predicate target
  release.v2 emits "not a path with spaces"
""")

    diagnostics = validate_document(doc, schema)

    assert [(d.code, d.path) for d in diagnostics] == [
        ("SDIF_REQUIRED_RELATION", "rel.depends_on"),
        ("SDIF_REL_PREDICATE", "rel[0].predicate"),
        ("SDIF_TYPE", "rel[1].object"),
    ]


def test_validator_reports_duplicate_fields_duplicate_tables_and_unknown_tables():
    schema = Schema.from_document(
        parse_text("""
@sdif 0.1
kind Schema
tables[name,ordered,primary_key]:
  milestones	true	id
""")
    )
    doc = parse_text("""
@sdif 0.1
kind Plan
kind Plan
milestones[id]:
  R1
milestones[id]:
  R2
extra[id]:
  E1
""")

    diagnostics = validate_document(doc, schema)

    assert [(d.code, d.path) for d in diagnostics] == [
        ("SDIF_DUPLICATE_FIELD", "kind"),
        ("SDIF_DUPLICATE_TABLE", "milestones"),
        ("SDIF_TABLE_UNKNOWN", "extra"),
    ]


def test_schema_parser_rejects_non_schema_documents():
    with pytest.raises(SchemaError, match="expected schema document"):
        Schema.from_document(
            parse_text("""
@sdif 0.1
kind Plan
id not.a.schema
""")
        )
