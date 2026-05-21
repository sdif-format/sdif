import subprocess
import sys
from pathlib import Path

from sdif import parse_text


def test_conformance_manifest_is_sdif_and_lists_portable_core_agent_case():
    manifest = Path("conformance/manifest.sdif")
    doc = parse_text(manifest.read_text(encoding="utf-8"))

    assert doc.fields["kind"].value == "ConformanceManifest"
    cases = doc.tables["cases"]
    assert cases.columns == ["id", "profile", "source", "canonical", "tree", "sha256"]
    assert any(row[0] == "core-agent" for row in cases.rows)


def test_conformance_checker_passes_for_python_and_tree_sitter_shared_fixtures():
    run = subprocess.run(
        [sys.executable, "scripts/check_conformance_fixtures.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0, run.stderr
    assert "conformance fixtures OK" in run.stdout
