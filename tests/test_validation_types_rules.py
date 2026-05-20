from sdif import parse_text
from sdif.validation import Schema, validate_document


SCHEMA = '''
@sdif 0.1
kind Schema
id example.plan.v1
fields[name,type,required,default]:
  kind\tIdentifier\ttrue\tnull
  id\tIdentifier\ttrue\tnull
  active\tBoolean\tfalse\ttrue
  count\tInteger\tfalse\tnull
  due\tDate\tfalse\tnull
  status\tEnum(open,closed)\tfalse\topen
columns[table,name,type,required]:
  milestones\tid\tIdentifier\ttrue
  milestones\tstatus\tEnum(done,pending)\ttrue
  milestones\tcount\tInteger\tfalse
rule_functions[name,min_args,max_args]:
  deny\t1\t1
  warn\t1\t1
  missing\t1\t1
  eq\t2\t2
'''


def test_validator_checks_field_types_table_types_and_rule_functions():
    schema = Schema.from_document(parse_text(SCHEMA))
    doc = parse_text('''
@sdif 0.1
kind Plan
id demo
active yes
count many
due 2026-99-99
status blocked
milestones[id,status,count]:
  R1\tunknown\tnan
rules:
  (allow missing(evidence))
  (deny missing(evidence) eq(status,open))
''')

    diagnostics = validate_document(doc, schema)

    assert [(d.code, d.path) for d in diagnostics] == [
        ("SDIF_TYPE", "active"),
        ("SDIF_TYPE", "count"),
        ("SDIF_TYPE", "due"),
        ("SDIF_ENUM", "status"),
        ("SDIF_ENUM", "milestones[0].status"),
        ("SDIF_TYPE", "milestones[0].count"),
        ("SDIF_RULE_FUNCTION", "rules[0]"),
        ("SDIF_RULE_ARITY", "rules[1]"),
    ]
