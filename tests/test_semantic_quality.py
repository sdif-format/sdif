import subprocess
import sys


def test_semantic_quality_checker_passes_for_plan_example():
    run = subprocess.run(
        [sys.executable, "scripts/check_semantic_quality.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0, run.stderr
    assert "semantic quality checks OK" in run.stdout
    for axis in (
        "relational expressivity",
        "round-trip fidelity",
        "schema validation",
        "SDIF AI semantic retention",
        "canonicalization",
    ):
        assert axis in run.stdout
