################################################################################
# Makefile = Single source of truth for local Dev/Test workflow.
#
# What this gives you:
# - One-liners for Docker DB lifecycle, Alembic migrations, testing, QA, and DX.
# - Test reports saved to timestamped files.
# - Safe reset flows with extensions/grants re-applied.
#
# Conventions / Notes:
# - DB runs in Docker (container name defaults to `scheduling_postgres`).
# - Alembic is env-aware via `-x env=dev|test` and APP_ENV is set per target.
# - Test DB is always `scheduling_test`; dev DB is `scheduling_dev`.
# - macOS: `db-logs` opens a NEW Terminal window via AppleScript when available.
#
# Edit these if your local names differ:
#   - CONTAINER := scheduling_postgres
#   - DB_SERVICE := db
################################################################################

# ---------- Variables ----------
SHELL := /bin/bash

VENV_BIN := $(CURDIR)/.venv/bin
ifneq ("$(wildcard $(VENV_BIN)/python)","")
  PY  := $(VENV_BIN)/python
  PIP := $(VENV_BIN)/pip
else
  PY  := python3
  PIP := pip3
endif

ALEMBIC := $(PY) -m alembic
PYTEST  := $(PY) -m pytest
COMPOSE := docker compose

DB_SERVICE := db
CONTAINER  := scheduling_postgres

PSQL_DEV  := psql "postgresql://scheduler_user:myschedulerpass@127.0.0.1:5432/scheduling_dev"
PSQL_TEST := psql "postgresql://scheduler_user:myschedulerpass@127.0.0.1:5432/scheduling_test"

# Paths for reports/backups
DATE_DIR   := $(shell date +%Y/%m/%d)
TIME_STAMP := $(shell date +%H-%M-%S)
REPORT_DIR := reports/$(DATE_DIR)
REPORT_FILE := $(REPORT_DIR)/$(TIME_STAMP)_test_report.txt

BACKUP_ROOT := backups/dev
BACKUP_DIR  := $(BACKUP_ROOT)/$(DATE_DIR)
BACKUP_FILE := $(BACKUP_DIR)/$(TIME_STAMP)_dev.sql

# ---------- Help ----------
.PHONY: help
help:
	@echo "Targets (grouped):"
	@echo "  Database:"
	@echo "    make db-up           - Start DB stack (docker compose up -d) and show status"
	@echo "    make db-down         - Stop & remove DB stack and volume"
	@echo "    make db-logs         - Tail Postgres logs (NEW macOS Terminal window if available)"
	@echo "    make db-status       - One-shot diagnostics: container, psql smoke, alembic head"
	@echo "    make db-backup-dev   - Dump dev DB to timestamped file under backups/dev/YYYY/MM/DD/"
	@echo "    make db-restore-dev  - Restore dev DB from latest dump or FILE=<path>"
	@echo "    make db-begin       	- Start DB, show status, optionally open logs"
	@echo
	@echo "  Migrations (Alembic):"
	@echo "    make migrate-dev     - Alembic upgrade head (dev)"
	@echo "    make migrate-test    - Alembic upgrade head (test)"
	@echo "    make migrate-all     - Upgrade both (dev & test)"
	@echo "    make migrate-new msg='...' - Create revision (autogenerate from models)"
	@echo "    make migrate-head    - Show current heads (dev & test)"
	@echo "    make migrate-down rev=<revision> - Downgrade to a specific revision (safety required)"
	@echo "    make migrate-sql     - [TODO] Render SQL (dry-run) for review"
	@echo
	@echo "  Seeding:"
	@echo "    make seed-dev            - Idempotent baseline seed (apply to DEV)"
	@echo "    make seed-dev-preview    - Plan/preview seed (no writes, pretty table)"
	@echo "    make seed-dev-dry        - Dry-run seed (execute & rollback, no pretty plan)"
	@echo "    make seed-dev-migrate    - Migrate DEV then seed (apply)"
	@echo "    make seed-test           - Seed TEST database (apply)"
	@echo "    make seed-test-preview   - Plan/preview seed for TEST (no writes)"
	@echo "    make seed-test-dry       - Dry-run seed for TEST (rollback)"
	@echo "    make seed-test-migrate   - Migrate TEST then seed (apply)"
	@echo
	@echo "  Testing:"
	@echo "    make test-all        - Full pytest suite on test DB"
	@echo "    make test-unit       - Unit tests only (verbose)"
	@echo "    make test-int        - Integration tests only (verbose)"
	@echo "    make test-smoke      - Smoke tests only"
	@echo "    make test-list       - One-line per test: PASSED/SKIPPED/ERROR/FAILED"
	@echo "    make test-report     - Save brief test list to test_reports/YYYY/MM/DD/HH-MM-SS_test_report.txt"
	@echo "    make test-report-detailed - Save full verbose run to the same folder"
	@echo
	@echo "  Code Quality & Checks:"
	@echo "    make qual-lint       - Ruff lint (auto-fix where possible)"
	@echo "    make qual-black      - Black format"
	@echo "    make qual-mypy       - Mypy type-check"
	@echo "    make qual-pylance    - Pylance via pyright CLI (if installed)"
	@echo "    make pre-commit      - Run all pre-commit hooks"
	@echo "    make pre-commit-suite- Run pre-commit + test-list"
	@echo
	@echo "  Security & Dependencies:"
	@echo "    make env-deps-audit  - pip-audit (fallback: safety)"
	@echo "    make env-deps-check  - Show outdated dependencies"
	@echo "    make env-rebuild     - Recreate .venv and reinstall (use FORCE=1)"
	@echo
	@echo "  Diagnostics & Developer UX:"
	@echo "    make env-show        - Print effective URLs, APP_ENV & versions"
	@echo "    make db-schema       - DB size & top tables (dev)"
	@echo
	@echo "  Repo Hygiene:"
	@echo "    make repo-clean      - Remove caches & build artifacts"
	@echo
	@echo "  (Placeholders [TODO] exist for: db-bootstrap, migrate-sql, seed-dev, seed-dev-preview, db-explain, docs-build, git targets)"

################################################################################
# Database
################################################################################

.PHONY: db-up db-down db-logs db-status db-backup-dev db-restore-dev db-begin

db-up:
	$(COMPOSE) up -d
	$(COMPOSE) ps

db-down:
	$(COMPOSE) down -v

# Open logs in a NEW macOS Terminal window if osascript is available; otherwise tail here.
db-logs:
	@which osascript >/dev/null 2>&1 && osascript -e 'tell application "Terminal" to do script "cd $(shell pwd) && $(COMPOSE) logs -f $(DB_SERVICE)"; activate' || (echo "Following logs in this terminal..."; $(COMPOSE) logs -f $(DB_SERVICE))

# One-shot diagnostics for both DBs (dev/test)
db-status:
	@echo "---- Docker containers ----"
	$(COMPOSE) ps
	@echo
	@echo "---- psql smoke (dev) ----"
	-$(PSQL_DEV) -c "select current_database(), current_user;"
	@echo
	@echo "---- psql smoke (test) ----"
	-$(PSQL_TEST) -c "select current_database(), current_user;"
	@echo
	@echo "---- Alembic heads ----"
	APP_ENV=dev  $(ALEMBIC) -x env=dev current
	APP_ENV=test $(ALEMBIC) -x env=test current

# Dump dev DB to timestamped SQL file (plain SQL)
db-backup-dev:
	@mkdir -p "$(BACKUP_DIR)"
	@echo "Dumping dev DB to $(BACKUP_FILE)"
	@docker exec -i $(CONTAINER) pg_dump -U postgres -d scheduling_dev --no-owner --no-privileges > "$(BACKUP_FILE)"
	@echo "Done."

# Restore dev DB from FILE=<path> or latest dump if FILE not provided
db-restore-dev:
	@[ -n "$(FILE)" ] || FILE=$$(ls -t $(BACKUP_ROOT)/*/*/*/*.sql 2>/dev/null | head -n1); \
	if [ -z "$$FILE" ]; then \
	  echo "No backup file found. Provide FILE=<path/to.sql>"; exit 1; \
	fi; \
	echo "Restoring dev DB from $$FILE"; \
	docker exec -i $(CONTAINER) psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS scheduling_dev WITH (FORCE);" ; \
	docker exec -i $(CONTAINER) psql -U postgres -d postgres -c "CREATE DATABASE scheduling_dev;" ; \
	docker exec -i $(CONTAINER) psql -U postgres -f /docker-entrypoint-initdb.d/02-extensions-and-grants.sql ; \
	cat "$$FILE" | docker exec -i $(CONTAINER) psql -U postgres -d scheduling_dev ; \
	echo "Restore complete."

# Interactive wrapper: up -> status -> optionally open logs
db-begin:
	@echo "=== Starting Postgres stack ==="
	$(MAKE) db-up
	@echo
	@echo "=== Status after start ==="
	$(MAKE) db-status
	@echo
	@read -r -p "Show Postgres logs now? [Y/N]: " ans; \
	case "$$ans" in \
	  y|Y|yes|YES) echo "Opening logs..."; $(MAKE) db-logs ;; \
	  *) echo "OK, not showing logs. Done."; ;; \
	esac

# db-bootstrap: up → migrate-all → seed-dev → db-status
.PHONY: db-bootstrap
db-bootstrap:
	@echo "=== Bootstrapping local DB ==="
	$(MAKE) db-up
	@echo
	@echo "=== Running migrations (dev & test) ==="
	$(MAKE) migrate-all
	@echo
	@echo "=== Seeding DEV database (apply) ==="
	$(MAKE) seed-dev
	@echo
	@echo "=== Status check ==="
	$(MAKE) db-status
	@echo "Bootstrap complete."


HEALTHCHECK_EXTS ?= pg_trgm

.PHONY: doctor doctor-dev doctor-test
## doctor: Run DB healthcheck for dev & test (version, extensions, alembic head)
doctor:
	APP_ENV=dev $(PY) -m app.db.healthcheck --env both --require-extensions "$(HEALTHCHECK_EXTS)"

## doctor-dev: Run DB healthcheck for dev only
doctor-dev:
	APP_ENV=dev $(PY) -m app.db.healthcheck --env dev --require-extensions "$(HEALTHCHECK_EXTS)"

## doctor-test: Run DB healthcheck for test only
doctor-test:
	APP_ENV=dev $(PY) -m app.db.healthcheck --env test --require-extensions "$(HEALTHCHECK_EXTS)"

################################################################################
# Alembic Migrations
################################################################################

.PHONY: migrate-dev migrate-test migrate-all migrate-new migrate-head migrate-down migrate-sql

migrate-dev:
	APP_ENV=dev $(ALEMBIC) -x env=dev upgrade head

migrate-test:
	APP_ENV=test $(ALEMBIC) -x env=test upgrade head

migrate-all: migrate-dev migrate-test

# Create new revision from ORM models (autogenerate). Usage: make migrate-new msg="add X to Y"
migrate-new:
ifndef msg
	$(error Usage: make migrate-new msg="your message")
endif
	APP_ENV=dev $(ALEMBIC) -x env=dev revision --autogenerate -m "$(msg)"
	@echo "Review the generated file in migrations/versions/, then run: make migrate-all"

# Show current heads (both envs)
migrate-head:
	@echo "---- Dev head ----"
	APP_ENV=dev $(ALEMBIC) -x env=dev current
	@echo "---- Test head ----"
	APP_ENV=test $(ALEMBIC) -x env=test current

# Downgrade to a specific revision (safety required). Usage: make migrate-down rev=<revision>
migrate-down:
ifndef rev
	$(error Usage: make migrate-down rev=<revision>)
endif
	@echo "Downgrading DEV to $(rev)"
	APP_ENV=dev $(ALEMBIC) -x env=dev downgrade $(rev)
	@echo "Downgrading TEST to $(rev)"
	APP_ENV=test $(ALEMBIC) -x env=test downgrade $(rev)
	@echo "Done. Consider re-running: make migrate-all"

# [TODO] Render SQL (offline/dry-run) for review
migrate-sql:
	@echo "[TODO] migrate-sql: render offline SQL for a given revision range."

################################################################################
# Seeding
################################################################################

.PHONY: seed-dev seed-dev-preview seed-dev-dry seed-dev-migrate seed-test seed-test-preview seed-test-dry seed-test-migrate

# DEV seeding variants
seed-dev: ## Apply idempotent baseline seed to DEV
	APP_ENV=dev $(PY) -m app.cli seed-data

seed-dev-preview: ## Plan/preview seed (no writes) for DEV
	APP_ENV=dev $(PY) -m app.cli seed-data --plan

seed-dev-dry: ## Execute then rollback (no pretty plan) for DEV
	APP_ENV=dev $(PY) -m app.cli seed-data --dry-run

seed-dev-migrate: ## Migrate DEV schema then seed (apply)
	$(MAKE) migrate-dev
	APP_ENV=dev $(PY) -m app.cli seed-data

# TEST seeding variants
seed-test: ## Apply idempotent baseline seed to TEST
	APP_ENV=test $(PY) -m app.cli seed-data

seed-test-preview: ## Plan/preview seed (no writes) for TEST
	APP_ENV=test $(PY) -m app.cli seed-data --plan

seed-test-dry: ## Execute then rollback (no pretty plan) for TEST
	APP_ENV=test $(PY) -m app.cli seed-data --dry-run

seed-test-migrate: ## Migrate TEST schema then seed (apply)
	$(MAKE) migrate-test
	APP_ENV=test $(PY) -m app.cli seed-data

################################################################################
# Testing
################################################################################

.PHONY: test-all test-unit test-int test-list test-report test-report-detailed test-smoke

# Full suite
test-all:
	APP_ENV=test $(PYTEST) -q

# Unit only (verbose)
test-unit:
	APP_ENV=test $(PYTEST) -vv -m unit

# Integration only (verbose)
test-int:
	APP_ENV=test $(PYTEST) -vv -m integration

# Smoke only
test-smoke:
	APP_ENV=test $(PYTEST) -vv -m smoke

# One-line per test (on-screen)
test-list:
	APP_ENV=test $(PYTEST) tests -v --tb=no --disable-warnings --no-header --no-summary

# Save brief list to timestamped file
test-report:
	@mkdir -p "$(REPORT_DIR)"
	@echo "Saving brief test report to $(REPORT_FILE)"
	@APP_ENV=test $(PYTEST) tests -v --tb=no --disable-warnings --no-header --no-summary > "$(REPORT_FILE)" 2>&1
	@echo "Done."

# Save full verbose run to timestamped file
test-report-detailed:
	@mkdir -p "$(REPORT_DIR)"
	@echo "Saving detailed test report to $(REPORT_FILE)"
	@APP_ENV=test $(PYTEST) -vv -s --tb=long > "$(REPORT_FILE)" 2>&1
	@echo "Done."

################################################################################
# Code Quality & Checks
################################################################################

.PHONY: qual-lint qual-black qual-mypy qual-pylance pre-commit pre-commit-suite

# Ruff lint (auto-fix where possible)
qual-lint:
	@ruff --version >/dev/null 2>&1 || (echo "ruff not found. Install with: pip install ruff"; exit 1)
	ruff check . --fix

# Black format
qual-black:
	@black --version >/dev/null 2>&1 || (echo "black not found. Install with: pip install black"; exit 1)
	black .

# Mypy type-check
qual-mypy:
	@mypy --version >/dev/null 2>&1 || (echo "mypy not found. Install with: pip install mypy"; exit 1)
	mypy .

# "Pylance" via the pyright CLI (closest CLI analogue)
qual-pylance:
	@pyright --version >/dev/null 2>&1 || (echo "pyright not found. Install with: npm i -g pyright  OR  pip install pyright"; exit 1)
	pyright

pre-commit:
	@pre-commit --version >/dev/null 2>&1 || (echo "pre-commit not found. Install with: pip install pre-commit"; exit 1)
	pre-commit run --all-files

pre-commit-suite: pre-commit
	$(MAKE) test-list


.PHONY: fmt lint typecheck pyright check-all

# Aliases that wrap your existing qual-* tasks
fmt:        ## Format code (ruff format + black)
	$(MAKE) qual-black

lint:       ## Lint (ruff)
	$(MAKE) qual-lint

typecheck:  ## Static typing (mypy)
	$(MAKE) qual-mypy

pyright:    ## Pylance/pyright CLI
	$(MAKE) qual-pylance

# One command to run everything quickly
check-all: fmt lint typecheck pyright
	@echo "All quality checks passed."

################################################################################
# Security & Dependencies
################################################################################

.PHONY: env-deps-audit env-deps-check env-rebuild

env-deps-audit:
	@pip-audit --version >/dev/null 2>&1 && pip-audit -r requirements.txt || \
	 (safety --version >/dev/null 2>&1 && safety check -r requirements.txt) || \
	 (echo "Neither pip-audit nor safety found. Install one: pip install pip-audit  OR  pip install safety"; exit 1)

env-deps-check:
	$(PIP) list --outdated

# Recreate local venv and reinstall deps (destructive). Usage: make env-rebuild FORCE=1
env-rebuild:
	@[ "$(FORCE)" = "1" ] || (echo "This will delete and recreate .venv. Re-run with: make env-rebuild FORCE=1"; exit 1)
	rm -rf .venv
	$(PY) -m venv .venv
	. .venv/bin/activate && python -m pip install -U pip wheel && python -m pip install -r requirements.txt
	@echo "New venv created. Activate with: source .venv/bin/activate"

################################################################################
# Diagnostics & Developer UX
################################################################################

.PHONY: env-show db-schema

# Print effective URLs, APP_ENV & versions
env-show:
	@echo "---- Files present ----"
	@ls -1 .env .env.test 2>/dev/null || true
	@echo
	@echo "---- Versions ----"
	@$(PY) --version
	@$(PIP) --version
	@psql --version || true
	@docker --version || true
	@$(ALEMBIC) --version
	@$(PYTEST) --version
	@echo
	@echo "---- Effective DB URLs (computed via app.config.settings.get_settings) ----"
	@$(PY) -c 'import os; from dotenv import load_dotenv; load_dotenv(".env"); os.environ.setdefault("APP_ENV","dev"); from app.config.settings import get_settings; s=get_settings(); print("DEV :", getattr(s,"effective_database_url", getattr(s,"DATABASE_URL", "<n/a>")))'
	@$(PY) -c 'import os; from dotenv import load_dotenv; load_dotenv(".env.test"); os.environ.setdefault("APP_ENV","test"); from app.config.settings import get_settings; s=get_settings(); print("TEST:", getattr(s,"effective_database_url", getattr(s,"DATABASE_URL", "<n/a>")))'

# Show DB size and top tables by size (dev)
db-schema:
	@echo "Database size (dev):"
	@$(PSQL_DEV) -c "select pg_size_pretty(pg_database_size(current_database())) as db_size;"
	@echo
	@echo "Top 30 tables by total size (dev):"
	@$(PSQL_DEV) -c "SELECT n.nspname AS schema, c.relname AS table, pg_size_pretty(pg_total_relation_size(c.oid)) AS total, pg_size_pretty(pg_relation_size(c.oid)) AS table_size, pg_size_pretty(pg_total_relation_size(c.oid)-pg_relation_size(c.oid)) AS indexes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND n.nspname NOT IN ('pg_catalog','information_schema') ORDER BY pg_total_relation_size(c.oid) DESC LIMIT 30;"

################################################################################
# Repo Hygiene
################################################################################

.PHONY: repo-clean
repo-clean:
	@echo "Removing caches and build artifacts..."
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info 2>/dev/null || true
	@echo "Done."

################################################################################
# Placeholders [TODO] you'll add later (descriptions only)
################################################################################

# [TODO] db-explain: Run EXPLAIN ANALYZE for a given SQL (param). Will accept q="select ..." or file.
.PHONY: db-explain
db-explain:
	@echo "[TODO] db-explain: EXPLAIN ANALYZE helper (q=... or FILE=...)."

# [TODO] docs-build: Build Sphinx/MkDocs docs locally.
.PHONY: docs-build
docs-build:
	@echo "[TODO] docs-build: build local docs (e.g., mkdocs build)."

# [TODO] Git helpers (pull / branch / PR) — left as stubs per your plan.
.PHONY: git-pull git-branch git-pr
git-pull:
	@echo "[TODO] git-pull: git checkout main && git pull --ff-only"

git-branch:
	@echo "[TODO] git-branch: git checkout main && git pull && git checkout -b <type>:<topic>"

git-pr:
	@echo "[TODO] git-pr: git push -u origin <type>:<topic> (then open PR)"
