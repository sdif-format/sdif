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
    monkeypatch.setenv("SDIF_ENV_OVERRIDE", "0")
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


def test_benchmark_ratios_rankings_and_savings_use_json_compact_as_baseline():
    rows = [
        token_comparison.FormatResult(
            name="JSON Compact",
            text="{}",
            bytes_size=100,
            tokens={"Estimate": 100},
            primary_ratio=100.0,
        ),
        token_comparison.FormatResult(
            name="Compact Format",
            text="x",
            bytes_size=60,
            tokens={"Estimate": 60},
            primary_ratio=60.0,
        ),
        token_comparison.FormatResult(
            name="Expanded Format",
            text="x",
            bytes_size=140,
            tokens={"Estimate": 140},
            primary_ratio=140.0,
        ),
    ]
    evidence = token_comparison.BenchmarkEvidence(
        generated_at="2026-05-21T00:00:00Z",
        run_dir=token_comparison.REPO_ROOT / "benchmarks" / "test",
        golden_dir=token_comparison.REPO_ROOT / "examples" / "golden",
        primary_name="Estimate",
        tokenizers=[token_comparison.TokenizerSpec("Estimate", lambda text: len(text))],
        results_by_document={"demo": rows},
        env_file_loaded=False,
    )

    observations = {
        observation.format_name: observation
        for observation in token_comparison.iter_ranked_observations(evidence, "Estimate")
    }

    assert observations["Compact Format"].rank == 1
    assert observations["Compact Format"].ratio_value == 60.0
    assert observations["Compact Format"].saved_tokens == 40
    assert observations["JSON Compact"].ratio_value == 100.0
    assert observations["JSON Compact"].saved_tokens == 0
    assert observations["Expanded Format"].ratio_value == 140.0
    assert observations["Expanded Format"].saved_tokens == -40
    assert token_comparison.wins_by_tokenizer(evidence, "Estimate") == {"Compact Format": 1}


def test_benchmark_script_runs_directly_from_checkout():
    env = os.environ.copy()
    env["SDIF_ENV_OVERRIDE"] = "0"
    env["SDIF_BENCHMARK_TOON"] = "0"
    env["SDIF_BENCHMARK_TOKENX"] = "0"
    env["SDIF_BENCHMARK_LLAMA"] = "0"
    env["SDIF_BENCHMARK_CLAUDE"] = "0"
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


def test_benchmark_main_emits_formal_summary_artifacts(monkeypatch, tmp_path):
    golden = tmp_path / "examples" / "golden" / "plan"
    golden.mkdir(parents=True)
    (golden / "equivalent.json").write_text(
        '{"kind":"Plan","id":"demo","items":[{"id":"I1","status":"open"}]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(token_comparison, "REPO_ROOT", tmp_path)
    monkeypatch.setenv("SDIF_BENCHMARK_TOON", "0")
    monkeypatch.setattr(
        token_comparison,
        "available_tokenizers",
        lambda: [token_comparison.TokenizerSpec("Estimate", token_comparison.count_estimate)],
    )

    token_comparison.main()

    latest = tmp_path / "benchmarks" / "latest"
    run_dir = latest.resolve()

    assert (run_dir / "summary.md").is_file()
    assert (run_dir / "summary.json").is_file()
    assert (run_dir / "summary.sdif").is_file()
    assert (run_dir / "summary.sdif.ai").is_file()
