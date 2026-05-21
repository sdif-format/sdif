import json
from pathlib import Path

from sdif import parse_text
from sdif.json import document_to_json_data, json_data_to_sdif


GOLDEN_ROOT = Path("examples/golden")
ALLOWED_GOLDEN_FILES = {"equivalent.json", "source.sdif", "canonical.sdif", "canonical.sha256"}


def test_golden_json_is_the_semantic_source_for_checked_in_sdif():
    for golden_json in sorted(GOLDEN_ROOT.glob("*/equivalent.json")):
        data = json.loads(golden_json.read_text(encoding="utf-8"))

        generated_sdif = json_data_to_sdif(data, include_header=True)
        source_sdif = golden_json.parent / "source.sdif"
        round_trip = document_to_json_data(parse_text(generated_sdif))

        if source_sdif.exists():
            checked_in_sdif = source_sdif.read_text(encoding="utf-8")
            assert generated_sdif == checked_in_sdif, golden_json
        assert round_trip == data, golden_json


def test_golden_directories_do_not_keep_stale_derived_formats():
    for document_dir in sorted(path for path in GOLDEN_ROOT.iterdir() if path.is_dir()):
        actual = {path.name for path in document_dir.iterdir()}
        assert "equivalent.json" in actual
        assert actual <= ALLOWED_GOLDEN_FILES


def test_json_to_sdif_encodes_heterogeneous_object_lists_as_lossless_block_lists():
    data = {"rows": [{"id": "A", "status": "open"}, {"id": "B", "owner": "team"}]}

    text = json_data_to_sdif(data)

    assert "rows:" in text
    assert "  __item:" in text
    assert document_to_json_data(parse_text(text)) == data


def test_json_to_sdif_preserves_ambiguous_string_scalars():
    data = {
        "numeric_string": "123",
        "decimal_string": "1.25",
        "bool_string": "true",
        "null_string": "null",
        "list_string": "[a,b]",
        "rows": [{"id": "001", "enabled": "false"}],
    }

    text = json_data_to_sdif(data)

    assert document_to_json_data(parse_text(text)) == data


def test_json_to_sdif_rejects_reserved_array_encoding_keys():
    data = {"rows": [{"__item": "not allowed"}]}

    try:
        json_data_to_sdif(data)
    except ValueError as exc:
        assert "reserved" in str(exc)
    else:  # pragma: no cover - assertion branch
        raise AssertionError("reserved JSON converter keys must be rejected explicitly")


def test_canonicalize_preserves_json_string_type_markers():
    from sdif import canonicalize

    data = {
        "numeric_string": "123",
        "rel": [{"subject": "a", "predicate": "points_to", "object": "456"}],
    }
    text = json_data_to_sdif(data, include_header=True)
    canonical = canonicalize(text)

    assert document_to_json_data(parse_text(canonical)) == data
