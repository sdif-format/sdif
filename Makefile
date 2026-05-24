# -----------------------------------------------------------------------------
# Tool detection
# -----------------------------------------------------------------------------

UV := $(shell command -v uv 2>/dev/null)

ifdef UV
INSTALL_CMD := uv pip install -e ".[dev]"
RUN := uv run
RUN_DEV ?= uv run --extra dev
else
INSTALL_CMD := python3 -m pip install -e ".[dev]"
RUN :=
RUN_DEV ?=
endif


# -----------------------------------------------------------------------------
# Project configuration
# -----------------------------------------------------------------------------

PACKAGE := sdif
PYTHONPATH := src
SOURCE_DIRS := src scripts tests tools
ARCHIVE_PATH := dist/sdif.tar.gz
VERSION      := $(shell grep '^version' pyproject.toml | sed 's/version = "//;s/"//')


# -----------------------------------------------------------------------------
# Public targets
# -----------------------------------------------------------------------------

.PHONY: install test test-cov lint format typecheck release-check clean archive build release


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
	PYTHONPATH=$(PYTHONPATH) $(RUN_DEV) python scripts/check_conformance_fixtures.py
	PYTHONPATH=$(PYTHONPATH) $(RUN_DEV) python -m compileall -q $(SOURCE_DIRS)
	$(RUN_DEV) ruff check .
	$(RUN_DEV) mypy
	PYTHONPATH=$(PYTHONPATH) $(RUN_DEV) python -c "import $(PACKAGE); print('$(PACKAGE) import OK')"
	PYTHONPATH=$(PYTHONPATH) $(RUN_DEV) python -m pytest -q


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
	$(RUN_DEV) python3 -m build
	$(RUN_DEV) python3 -m twine check dist/*


release: release-check build
	$(RUN_DEV) python3 -m twine upload dist/*
	@VERSION=$$(grep '^version' pyproject.toml | sed 's/version = "//;s/"//'); \
	NOTES=$$(sed -n "/^## \[$$VERSION\]/,/^## \[/{/^## \[/d;p}" CHANGELOG.md); \
	gh release create "v$$VERSION" dist/* --title "v$$VERSION" --notes "$$NOTES"

