import os
import subprocess
import sys

from benchmarks import token_comparison


def test_benchmark_main_discovers_golden_fixtures_from_script_location(
    monkeypatch,
    tmp_path,
    capsys,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SDIF_BENCHMARK_TOON", "0")
    monkeypatch.setattr(
        token_comparison,
        "available_tokenizers",
        lambda: [token_comparison.TokenizerSpec("tiktoken", lambda text: len(text.split()))],
    )

    token_comparison.main()

    output = capsys.readouterr().out
    assert "JSON Compact" in output
    assert "JSON Pretty" in output
    assert "YAML" in output
    assert "XML" in output
    assert "CSV Bundle" in output
    assert "SDIF" in output
    assert "TOON skipped" in output


def test_benchmark_script_runs_directly_from_checkout():
    env = os.environ.copy()
    env["SDIF_BENCHMARK_TOON"] = "0"
    env.pop("PYTHONPATH", None)

    run = subprocess.run(
        [sys.executable, "benchmarks/token_comparison.py"],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0
    assert "XML" in run.stdout
    assert "CSV Bundle" in run.stdout
