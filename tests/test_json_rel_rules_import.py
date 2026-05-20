from sdif import parse_text
from sdif.json import json_data_to_sdif


def test_json_data_to_sdif_imports_relations_rules_lists_and_nested_objects():
    text = json_data_to_sdif(
        {
            "kind": "Plan",
            "id": "demo",
            "tags": ["release", "validation"],
            "owner": {"id": "team.platform", "role": "maintainer"},
            "rel": [{"subject": "R2", "predicate": "depends_on", "object": "R1"}],
            "rules": ["(deny missing(evidence))"],
        }
    )

    assert text == '''
kind Plan
id demo
tags [release,validation]
owner:
  id team.platform
  role maintainer
rel:
  R2 depends_on R1
rules:
  (deny missing(evidence))
'''.lstrip()
    doc = parse_text(text)
    assert doc.fields["tags"].value == "[release,validation]"
    assert doc.relations[0].predicate == "depends_on"
    assert doc.rules[0].source == "(deny missing(evidence))"
