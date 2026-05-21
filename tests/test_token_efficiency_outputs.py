import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path("benchmarks/scripts/token_efficiency.py")


def load_token_efficiency_module():
    spec = importlib.util.spec_from_file_location("token_efficiency", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["token_efficiency"] = module
    spec.loader.exec_module(module)
    return module


def test_token_efficiency_writes_to_tmp_then_moves_to_named_results(monkeypatch, tmp_path):
    module = load_token_efficiency_module()
    output_root = tmp_path / "benchmarks"
    monkeypatch.setenv("SDIF_BENCHMARK_OUTPUT_DIR", str(output_root))

    run_dir = module.create_benchmark_run_dir()

    assert run_dir == output_root / "tmp" / "token_efficiency"
    assert run_dir.is_dir()

    final_dir = output_root / "results" / "token_efficiency"
    final_dir.mkdir(parents=True)
    (final_dir / "stale.txt").write_text("old", encoding="utf-8")
    (run_dir / "summary.md").write_text("new", encoding="utf-8")

    published = module.publish_benchmark_result(run_dir)

    assert published == final_dir
    assert not run_dir.exists()
    assert not (published / "stale.txt").exists()
    assert (published / "summary.md").read_text(encoding="utf-8") == "new"
