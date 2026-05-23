from sdif import parse_text
from sdif.ai import expand_ai_doc
from sdif.canonical.canonicalizer import canonicalize
from sdif.json import document_to_json_data, json_data_to_sdif


def test_document_to_json_maps_fields_tables_relations_and_rules():
    doc = parse_text("""
@sdif 1.0
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

    assert text == "@sdif 1.0\nkind Plan\nid demo\nmilestones[id,status]:\n  R1\tdone\n  R2\tpending\n"
    assert parse_text(text).tables["milestones"].rows[1] == ["R2", "pending"]


def test_ai_string_column_marker_preserves_scalar_like_strings_without_repeated_quotes():
    doc = parse_text("""
@sdif.ai 1.0
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


# Regression: scalar-ambiguous strings must survive JSON→SDIF→JSON round-trip.
# Strings that look like typed SDIF literals must be quoted on emission and
# decoded back to strings, not typed values.
_AMBIGUOUS_SCALARS = ["200", "404", "0", "-1", "1.0", "3.14", "true", "false", "null", "[1,2]", ""]


def test_scalar_ambiguous_strings_survive_json_sdif_json_field_round_trip():
    for value in _AMBIGUOUS_SCALARS:
        data = {"code": value}
        sdif_text = json_data_to_sdif(data)
        doc = parse_text(sdif_text)
        result = document_to_json_data(doc)
        assert result["code"] == value, f"field round-trip lost {value!r}: got {result['code']!r}"
        assert isinstance(result["code"], str), f"field round-trip changed type of {value!r}"


def test_scalar_ambiguous_strings_survive_json_sdif_json_table_round_trip():
    for value in _AMBIGUOUS_SCALARS:
        data = {"rows": [{"id": "r1", "code": value}]}
        sdif_text = json_data_to_sdif(data)
        doc = parse_text(sdif_text)
        result = document_to_json_data(doc)
        cell = result["rows"][0]["code"]
        assert cell == value, f"table round-trip lost {value!r}: got {cell!r}"
        assert isinstance(cell, str), f"table round-trip changed type of {value!r}"


def test_scalar_ambiguous_strings_survive_sdif_ai_expand_table_round_trip():
    # Encode JSON→SDIF, project to SDIF AI text, expand back, decode.
    # The $-suffixed column must preserve the string type through expand_ai_doc.
    for value in _AMBIGUOUS_SCALARS:
        data = {"rows": [{"id": "r1", "code": value}]}
        sdif_text = json_data_to_sdif(data)
        doc = parse_text(sdif_text)
        rows = doc.tables.get("rows")
        if rows is None:
            # empty-string or other value may be encoded as a block list — skip table path
            continue
        # Build a .sdif.ai snippet with code$ marker to simulate what the AI projection emits
        ai_text = "@sdif.ai 1.0\nrows[id,code$]:\n"
        for row in rows.rows:
            ai_text += "\t".join(row) + "\n"
        expanded_doc = expand_ai_doc(parse_text(ai_text))
        result = document_to_json_data(expanded_doc)
        cell = result["rows"][0]["code"]
        assert cell == value, (
            f"SDIF AI expand round-trip lost {value!r}: got {cell!r}"
        )
        assert isinstance(cell, str), f"SDIF AI expand round-trip changed type of {value!r}"


def test_canonicalize_preserves_list_literals_without_inner_quotes():
    # Regression: canonicalize must not convert bare list literals into quoted strings.
    # [a,b] and [1,2,3] must remain list literals, not become "[a,b]" (a string).
    sdif_text = "@sdif 1.0\ntags [a,b,c]\nids [1,2,3]\n"
    canonical = canonicalize(sdif_text)
    doc = parse_text(canonical)
    data = document_to_json_data(doc)
    assert data["tags"] == ["a", "b", "c"], f"list literal became {data['tags']!r}"
    assert data["ids"] == [1, 2, 3], f"list literal became {data['ids']!r}"
