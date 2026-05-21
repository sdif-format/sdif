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
    assert "SDIF" in output
    assert "TOON skipped" in output
