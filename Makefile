# =============================================================================
# File: Makefile
# Purpose:
#   Developer shortcuts for common tasks.
#
# Targets (examples):
#   setup, dev, lint, typecheck, test, migrate, seed, diag
#
# Usage:
#   make setup
# =============================================================================

.PHONY: fmt lint type test hooks

.PHONY: all
all: fmt lint type test hooks

fmt:
	black .

lint:
	ruff check .

type:
	mypy .

test:
	pytest -q

hooks:
	pre-commit run --all-files
