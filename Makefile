# -----------------------------------------------------------------------------
# Tool detection
# -----------------------------------------------------------------------------

UV := $(shell command -v uv 2>/dev/null)

ifdef UV
INSTALL_CMD := uv pip install -e ".[dev]"
RUN := uv run
else
INSTALL_CMD := python3 -m pip install -e ".[dev]"
RUN :=
endif


# -----------------------------------------------------------------------------
# Project configuration
# -----------------------------------------------------------------------------

PACKAGE := sdif
PYTHONPATH := src
SOURCE_DIRS := src scripts tests tools
ARCHIVE_PATH := dist/sdif.tar.gz


# -----------------------------------------------------------------------------
# Public targets
# -----------------------------------------------------------------------------

.PHONY: install test test-cov lint format typecheck release-check clean archive build


install:
	$(INSTALL_CMD)


test:
	$(RUN) pytest


test-cov:
	$(RUN) pytest --cov=$(PACKAGE) --cov-report=term-missing


lint:
	$(RUN) ruff check .


format:
	$(RUN) ruff format .


typecheck:
	$(RUN) mypy


release-check:
	PYTHONPATH=$(PYTHONPATH) $(RUN) python scripts/check_conformance_fixtures.py
	PYTHONPATH=$(PYTHONPATH) $(RUN) python -m compileall -q $(SOURCE_DIRS)
	$(RUN) ruff check .
	$(RUN) mypy
	PYTHONPATH=$(PYTHONPATH) $(RUN) python -c "import $(PACKAGE); print('$(PACKAGE) import OK')"
	PYTHONPATH=$(PYTHONPATH) $(RUN) python -m pytest -q


clean:
	rm -rf \
		build/ \
		dist/ \
		*.egg-info \
		src/*.egg-info \
		.mypy_cache/ \
		.pytest_cache/ \
		.ruff_cache/


archive:
	mkdir -p dist
	git archive --format=tar.gz --output=$(ARCHIVE_PATH) HEAD


build: clean
	$(RUN) python3 -m build
	$(RUN) python3 -m twine check dist/*

