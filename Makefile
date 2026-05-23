# Detect if uv is installed
UV := $(shell command -v uv 2> /dev/null)

.PHONY: install test test-cov lint format typecheck release-check clean archive

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

release-check:
	PYTHONPATH=src python3 scripts/check_conformance_fixtures.py
	PYTHONPATH=src python3 -m compileall -q src scripts tests tools
	$(RUN_PREFIX) ruff check .
	$(RUN_PREFIX) mypy
	$(RUN_PREFIX) python -c "import sdif; print('sdif import OK')"
	PYTHONPATH=src python3 -m pytest -q

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info .mypy_cache .pytest_cache .ruff_cache

archive:
	mkdir -p dist
	git archive --format=tar.gz --output=dist/sdif.tar.gz HEAD
