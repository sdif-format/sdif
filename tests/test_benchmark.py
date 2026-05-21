import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


def load_token_efficiency_module():
    module_path = Path("benchmarks/scripts/token_efficiency.py")
    spec = importlib.util.spec_from_file_location("token_efficiency", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["token_efficiency"] = module
    spec.loader.exec_module(module)
    return module


token_efficiency = load_token_efficiency_module()


def path_snapshot(path):
    try:
        stat = path.lstat()
    except FileNotFoundError:
        return None

    target = os.readlink(path) if path.is_symlink() else None
    return (stat.st_mode, stat.st_size, stat.st_mtime_ns, target)


def test_benchmark_main_discovers_golden_fixtures_from_script_location(
    monkeypatch,
    tmp_path,
    capsys,
):
    golden = tmp_path / "golden" / "plan"
    golden.mkdir(parents=True)
    (golden / "equivalent.json").write_text(
        '{"kind":"Plan","id":"demo","items":[{"id":"I1","status":"open"}]}',
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SDIF_ENV_OVERRIDE", "0")
    monkeypatch.setenv("SDIF_BENCHMARK_TOON", "0")
    monkeypatch.setenv("SDIF_BENCHMARK_GOLDEN_DIR", str(tmp_path / "golden"))
    monkeypatch.setenv("SDIF_BENCHMARK_OUTPUT_DIR", str(tmp_path / "benchmarks"))
    monkeypatch.setattr(
        token_efficiency,
        "available_tokenizers",
        lambda: [token_efficiency.TokenizerSpec("tiktoken", lambda text: len(text.split()))],
    )

    token_efficiency.main()

    output = capsys.readouterr().out
    assert "Semantic source:" in output
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

    formats = dict(token_efficiency.build_formats(data))

    assert len(formats["SDIF AI"].encode("utf-8")) <= len(formats["SDIF"].encode("utf-8"))


def test_benchmark_has_estimated_token_counter_when_optional_tokenizers_unavailable(monkeypatch):
    monkeypatch.setattr(token_efficiency, "tiktoken", None)
    monkeypatch.setattr(token_efficiency, "AutoTokenizer", None)
    monkeypatch.setattr(token_efficiency, "Anthropic", None)

    tokenizers = token_efficiency.available_tokenizers()
    names = [tokenizer.name for tokenizer in tokenizers]

    assert "Estimate" in names
    estimate = next(tokenizer for tokenizer in tokenizers if tokenizer.name == "Estimate")
    assert estimate.counter("abcd") == 1
    assert estimate.counter("abcde") == 2
    assert token_efficiency.select_primary_tokenizer(tokenizers, "abcd").name == "Estimate"


def test_benchmark_ratios_rankings_and_savings_use_json_compact_as_baseline():
    rows = [
        token_efficiency.FormatResult(
            name="JSON Compact",
            text="{}",
            bytes_size=100,
            tokens={"Estimate": 100},
            primary_ratio=100.0,
        ),
        token_efficiency.FormatResult(
            name="Compact Format",
            text="x",
            bytes_size=60,
            tokens={"Estimate": 60},
            primary_ratio=60.0,
        ),
        token_efficiency.FormatResult(
            name="Expanded Format",
            text="x",
            bytes_size=140,
            tokens={"Estimate": 140},
            primary_ratio=140.0,
        ),
    ]
    evidence = token_efficiency.BenchmarkEvidence(
        generated_at="2026-05-21T00:00:00Z",
        run_dir=token_efficiency.REPO_ROOT / "benchmarks" / "test",
        golden_dir=token_efficiency.REPO_ROOT / "examples" / "golden",
        primary_name="Estimate",
        tokenizers=[token_efficiency.TokenizerSpec("Estimate", lambda text: len(text))],
        results_by_document={"demo": rows},
        env_file_loaded=False,
    )

    observations = {
        observation.format_name: observation
        for observation in token_efficiency.iter_ranked_observations(evidence, "Estimate")
    }

    assert observations["Compact Format"].rank == 1
    assert observations["Compact Format"].ratio_value == 60.0
    assert observations["Compact Format"].saved_tokens == 40
    assert observations["JSON Compact"].ratio_value == 100.0
    assert observations["JSON Compact"].saved_tokens == 0
    assert observations["Expanded Format"].ratio_value == 140.0
    assert observations["Expanded Format"].saved_tokens == -40
    assert token_efficiency.wins_by_tokenizer(evidence, "Estimate") == {"Compact Format": 1}



def test_benchmark_golden_dir_can_be_overridden(monkeypatch, tmp_path):
    monkeypatch.delenv("SDIF_BENCHMARK_GOLDEN_DIR", raising=False)
    assert token_efficiency.benchmark_golden_dir() == token_efficiency.REPO_ROOT / "examples" / "golden"

    custom = tmp_path / "golden"
    monkeypatch.setenv("SDIF_BENCHMARK_GOLDEN_DIR", str(custom))

    assert token_efficiency.benchmark_golden_dir() == custom.resolve()


def test_benchmark_script_runs_directly_from_checkout(tmp_path):
    golden = tmp_path / "golden" / "plan"
    golden.mkdir(parents=True)
    (golden / "equivalent.json").write_text(
        '{"kind":"Plan","id":"demo","items":[{"id":"I1","status":"open"}]}',
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["SDIF_ENV_OVERRIDE"] = "0"
    env["SDIF_BENCHMARK_TOON"] = "0"
    env["SDIF_BENCHMARK_TOKENX"] = "0"
    env["SDIF_BENCHMARK_LLAMA"] = "0"
    env["SDIF_BENCHMARK_CLAUDE"] = "0"
    env["SDIF_BENCHMARK_GOLDEN_DIR"] = str(tmp_path / "golden")
    env["SDIF_BENCHMARK_OUTPUT_DIR"] = str(tmp_path / "benchmarks")
    env.pop("PYTHONPATH", None)

    repo_result = token_efficiency.REPO_ROOT / "benchmarks" / "results" / "token_efficiency"
    before = path_snapshot(repo_result)

    run = subprocess.run(
        [sys.executable, "benchmarks/scripts/token_efficiency.py"],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )

    assert run.returncode == 0
    assert "XML" in run.stdout
    assert "CSV Bundle" in run.stdout
    assert path_snapshot(repo_result) == before
    assert (tmp_path / "benchmarks" / "results" / "token_efficiency").exists()
    assert not (tmp_path / "benchmarks" / "tmp" / "token_efficiency").exists()


def test_benchmark_main_emits_formal_summary_artifacts(monkeypatch, tmp_path):
    golden = tmp_path / "examples" / "golden" / "plan"
    golden.mkdir(parents=True)
    (golden / "equivalent.json").write_text(
        '{"kind":"Plan","id":"demo","items":[{"id":"I1","status":"open"}]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(token_efficiency, "REPO_ROOT", tmp_path)
    monkeypatch.setenv("SDIF_BENCHMARK_TOON", "0")
    monkeypatch.setattr(
        token_efficiency,
        "available_tokenizers",
        lambda: [token_efficiency.TokenizerSpec("Estimate", token_efficiency.count_estimate)],
    )

    token_efficiency.main()

    run_dir = tmp_path / "benchmarks" / "results" / "token_efficiency"

    assert (run_dir / "summary.md").is_file()
    assert (run_dir / "summary.json").is_file()
    assert (run_dir / "summary.sdif").is_file()
    assert (run_dir / "summary.sdif.ai").is_file()


def test_benchmark_main_emits_self_contained_html_dashboard(monkeypatch, tmp_path):
    golden = tmp_path / "examples" / "golden" / "plan"
    golden.mkdir(parents=True)
    (golden / "equivalent.json").write_text(
        '{"kind":"Plan","id":"demo","items":[{"id":"I1","status":"open"}]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(token_efficiency, "REPO_ROOT", tmp_path)
    monkeypatch.setenv("SDIF_BENCHMARK_TOON", "0")
    monkeypatch.setattr(
        token_efficiency,
        "available_tokenizers",
        lambda: [token_efficiency.TokenizerSpec("Estimate", token_efficiency.count_estimate)],
    )

    token_efficiency.main()

    run_dir = tmp_path / "benchmarks" / "results" / "token_efficiency"
    dashboard = run_dir / "dashboard.html"
    report = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    html = dashboard.read_text(encoding="utf-8")

    assert dashboard.is_file()
    assert 'id="report-data" type="application/json"' in html
    assert 'id="summary-md" type="application/json"' in html
    assert 'id="comparison-md-preview" type="application/json"' in html
    assert report["generatedAt"] in html
    assert "/home/alessbarb/Descargas" not in html
    assert report["artifacts"]["dashboard"] == "benchmarks/results/token_efficiency/dashboard.html"


def test_benchmark_main_publishes_compared_corpus_files(monkeypatch, tmp_path):
    golden = tmp_path / "examples" / "golden" / "plan"
    golden.mkdir(parents=True)
    (golden / "equivalent.json").write_text(
        '{"kind":"Plan","id":"demo","items":[{"id":"I1","status":"open"}]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(token_efficiency, "REPO_ROOT", tmp_path)
    monkeypatch.setenv("SDIF_BENCHMARK_TOON", "0")
    monkeypatch.setattr(
        token_efficiency,
        "available_tokenizers",
        lambda: [token_efficiency.TokenizerSpec("Estimate", token_efficiency.count_estimate)],
    )

    token_efficiency.main()

    run_dir = tmp_path / "benchmarks" / "results" / "token_efficiency"
    corpus_dir = run_dir / "corpus" / "plan"
    report = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))

    assert (corpus_dir / "json_compact.json").read_text(encoding="utf-8").startswith(
        '{"kind":"Plan"'
    )
    assert (corpus_dir / "json_pretty.json").read_text(encoding="utf-8").startswith("{\n")
    assert (corpus_dir / "yaml.yaml").is_file()
    assert (corpus_dir / "xml.xml").is_file()
    assert (corpus_dir / "csv_bundle.csv").is_file()
    assert (corpus_dir / "sdif.sdif").is_file()
    assert (corpus_dir / "sdif_ai.sdif.ai").is_file()
    assert not (corpus_dir / "toon.toon").exists()
    assert report["artifacts"]["corpus"] == "benchmarks/results/token_efficiency/corpus"
