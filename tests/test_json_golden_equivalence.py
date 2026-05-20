import json
from pathlib import Path

from sdif import parse_text
from sdif.json import document_to_json_data, json_data_to_sdif


GOLDEN_ROOT = Path("examples/golden")
EXPECTED_GOLDEN_FILES = {"equivalent.json", "source.sdif"}


def test_golden_json_is_the_semantic_source_for_checked_in_sdif():
    for golden_json in sorted(GOLDEN_ROOT.glob("*/equivalent.json")):
        data = json.loads(golden_json.read_text(encoding="utf-8"))

        generated_sdif = json_data_to_sdif(data, include_header=True)
        checked_in_sdif = (golden_json.parent / "source.sdif").read_text(encoding="utf-8")
        round_trip = document_to_json_data(parse_text(generated_sdif))

        assert generated_sdif == checked_in_sdif, golden_json
        assert round_trip == data, golden_json


def test_golden_directories_do_not_keep_stale_derived_formats():
    for document_dir in sorted(path for path in GOLDEN_ROOT.iterdir() if path.is_dir()):
        assert {path.name for path in document_dir.iterdir()} == EXPECTED_GOLDEN_FILES


def test_json_to_sdif_rejects_heterogeneous_object_tables():
    data = {"rows": [{"id": "A", "status": "open"}, {"id": "B", "owner": "team"}]}

    try:
        json_data_to_sdif(data)
    except ValueError as exc:
        assert "not uniform" in str(exc)
    else:  # pragma: no cover - assertion branch
        raise AssertionError("heterogeneous JSON arrays must not be silently encoded as SDIF tables")
