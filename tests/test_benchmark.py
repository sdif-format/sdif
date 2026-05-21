import os
import subprocess
import sys

from scripts import token_comparison


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
    assert "SDIF AI" in output
    assert "TOON skipped" in output


def test_benchmark_sdif_ai_projection_is_not_larger_than_canonical_sdif(monkeypatch):
    monkeypatch.setenv("SDIF_BENCHMARK_TOON", "0")
    data = {
        "kind": "Plan",
        "id": "demo",
        "items": [
            {"id": "I1", "status": "open"},
            {"id": "I2", "status": "done"},
        ],
    }

    formats = dict(token_comparison.build_formats(data))

    assert len(formats["SDIF AI"].encode("utf-8")) <= len(formats["SDIF"].encode("utf-8"))


def test_benchmark_has_estimated_token_counter_when_optional_tokenizers_unavailable(monkeypatch):
    monkeypatch.setattr(token_comparison, "tiktoken", None)
    monkeypatch.setattr(token_comparison, "AutoTokenizer", None)
    monkeypatch.setattr(token_comparison, "Anthropic", None)

    tokenizers = token_comparison.available_tokenizers()
    names = [tokenizer.name for tokenizer in tokenizers]

    assert "Estimate" in names
    estimate = next(tokenizer for tokenizer in tokenizers if tokenizer.name == "Estimate")
    assert estimate.counter("abcd") == 1
    assert estimate.counter("abcde") == 2
    assert token_comparison.select_primary_tokenizer(tokenizers, "abcd").name == "Estimate"


def test_benchmark_script_runs_directly_from_checkout():
    env = os.environ.copy()
    env["SDIF_BENCHMARK_TOON"] = "0"
    env.pop("PYTHONPATH", None)

    run = subprocess.run(
        [sys.executable, "scripts/token_comparison.py"],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert run.returncode == 0
    assert "XML" in run.stdout
    assert "CSV Bundle" in run.stdout
