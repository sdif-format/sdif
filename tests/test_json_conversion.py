from sdif import parse_text
from sdif.json import document_to_json_data, json_data_to_sdif


def test_document_to_json_maps_fields_tables_relations_and_rules():
    doc = parse_text("""
@sdif 0.1
kind Plan
id demo
milestones[id,status]:
  R1\tdone
rel:
  R1 depends_on R0
rules:
  (deny missing(evidence))
""")

    data = document_to_json_data(doc)

    assert data["kind"] == "Plan"
    assert data["milestones"] == [{"id": "R1", "status": "done"}]
    assert data["rel"] == [{"subject": "R1", "predicate": "depends_on", "object": "R0"}]
    assert data["rules"] == ["(deny missing(evidence))"]


def test_json_data_to_sdif_emits_scalars_and_uniform_tables():
    text = json_data_to_sdif(
        {
            "kind": "Plan",
            "id": "demo",
            "milestones": [
                {"id": "R1", "status": "done"},
                {"id": "R2", "status": "pending"},
            ],
        }
    )

    assert text == "kind Plan\nid demo\nmilestones[id,status]:\n  R1\tdone\n  R2\tpending\n"
    assert parse_text(text).tables["milestones"].rows[1] == ["R2", "pending"]


def test_ai_string_column_marker_preserves_scalar_like_strings_without_repeated_quotes():
    doc = parse_text("""
@sdif.ai 0.1
items[id,value$]:
I1	null
I2	42
I3	true
""")

    assert document_to_json_data(doc)["items"] == [
        {"id": "I1", "value": "null"},
        {"id": "I2", "value": "42"},
        {"id": "I3", "value": "true"},
    ]
