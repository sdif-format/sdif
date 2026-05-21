from sdif import canonicalize
from sdif.validation import Schema
from sdif import parse_text


def test_schema_policy_orders_table_rows_relations_and_rules_when_unordered():
    schema_doc = parse_text("""
@sdif 0.1
kind Schema
tables[name,ordered,primary_key]:
  milestones\tfalse\tid
""")
    schema = Schema.from_document(schema_doc)
    source = """
@sdif 0.1
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
@sdif 0.1
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
