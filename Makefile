.PHONY: install test lint format typecheck benchmark clean

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

lint:
	$(RUN_PREFIX) ruff check .

format:
	$(RUN_PREFIX) ruff format .

typecheck:
	$(RUN_PREFIX) mypy

benchmark:
	$(RUN_PREFIX) python benchmarks/token_comparison.py

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info .mypy_cache .pytest_cache .ruff_cache
