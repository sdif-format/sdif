.PHONY: install test test-cov lint format typecheck benchmark benchmark-token benchmark-quality benchmark-corpus benchmark-large-corpus clean

# Detect if uv is installed
UV := $(shell command -v uv 2> /dev/null)

ifdef UV
	INSTALL_CMD := uv pip install -e ".[dev]"
	RUN_PREFIX := uv run
else
	INSTALL_CMD := python -m pip install -e ".[dev]"
	RUN_PREFIX :=
endif

install:
	$(INSTALL_CMD)

test:
	$(RUN_PREFIX) pytest

test-cov:
	$(RUN_PREFIX) pytest --cov=sdif --cov-report=term-missing

lint:
	$(RUN_PREFIX) ruff check .

format:
	$(RUN_PREFIX) ruff format .

typecheck:
	$(RUN_PREFIX) mypy

benchmark: benchmark-token

benchmark-token:
	$(RUN_PREFIX) python scripts/token_comparison.py

benchmark-quality:
	$(RUN_PREFIX) python scripts/check_semantic_quality.py

benchmark-corpus:
	$(RUN_PREFIX) python scripts/generate_benchmark_golden.py

benchmark-large-corpus:
	$(RUN_PREFIX) python scripts/generate_large_golden.py

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info .mypy_cache .pytest_cache .ruff_cache

archive:
	mkdir -p dist
	git archive --format=tar.gz --output=dist/sdif.tar.gz HEAD