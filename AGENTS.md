# Scheduling Engine Project Guide for OpenAI Codex

This `AGENTS.md` file provides a comprehensive guide for OpenAI Codex and other AI agents working on the Scheduling Engine project. It consolidates the conventions, workflows, and policies established across all development phases to ensure consistent, high-quality contributions.

---

## Purpose of the Scheduling Engine and Codex’s Role

The Scheduling Engine is a backend system designed to manage complex scheduling workflows, optimize resource allocation, and provide reliable, deterministic scheduling outcomes. OpenAI Codex plays a critical role in generating, maintaining, and enhancing the codebase by adhering to established project standards, ensuring maintainability, testability, and operational robustness.

---

## Project Structure

The project is organized to support clear separation of concerns and ease of navigation:

- `app/`
  Core application code including business logic, models, services, and API endpoints.

- `tests/`
  All test suites, organized by unit, integration, and smoke tests. Uses pytest with markers for test types.

- `migrations/`
  Alembic migration scripts for database schema changes. All DB migrations must be handled here.

- `docs/`
  Project documentation, including design documents, API specs, and this guide.

- `scripts/`
  Utility scripts for setup, deployment, and maintenance tasks.

- `configs/`
  Configuration files and environment templates (`.env`, `.env.test`, etc.).

---

## Coding Conventions

- **Language & Versions**
  Use Python 3.12 with full support for modern language features.

- **Typing and Validation**
  Use Pydantic v2 for data validation and settings management. All public functions and methods must include precise type hints.

- **ORM & Database**
  Use SQLAlchemy 2.x with the new 2.0 style API. Define clear boundaries between Data Transfer Objects (DTOs) and repository layers to avoid leakage of ORM models outside data access layers.

- **Logging and Exceptions**
  Use the standard `logging` module with structured logs. Avoid logging sensitive information or secrets. Handle exceptions explicitly and raise custom exceptions where appropriate.

- **Code Style**
  Follow Black formatting strictly. Use `ruff` for linting and enforce PEP8 and project-specific rules.

- **Docstrings**
  Every module, class, and function must have clear docstrings describing purpose, parameters, return types, and exceptions raised.

- **No Side Effects in `__init__.py`**
  Initialization files should only set up package imports and not execute code with side effects.

---

## Testing Conventions

- **Framework**
  Use `pytest` exclusively.

- **Test Types & Markers**
  Use pytest markers to differentiate test types:
  - `@pytest.mark.unit` for unit tests
  - `@pytest.mark.integration` for integration tests
  - `@pytest.mark.smoke` for critical smoke tests

- **Fixtures**
  Use fixtures for setup and teardown. Fixtures should be deterministic and reusable.

- **Deterministic Environment**
  Tests must run reliably and deterministically. Avoid reliance on external state or timing.

- **Coverage**
  Ensure comprehensive coverage of critical business logic and edge cases.

- **Test Data**
  Use idempotent seed data and mocks to isolate tests.

---

## Environment Handling

- Use `.env` for default environment variables and `.env.test` for test-specific overrides.
- The application must be aware of `APP_ENV` to switch configurations dynamically.
- Secrets and sensitive data must **never** be logged or exposed in error messages.
- Environment variables should be accessed via Pydantic settings models.

---

## Commit & Branching Conventions

- Follow **Conventional Commits** strictly to enable automated changelog generation and CI workflows.
- Use short-lived feature branches named descriptively (e.g., `feature/scheduling-algorithm`).
- Pull Requests must:
  - Have a clear, concise description of changes
  - Reference related issues or tickets
  - Pass all tests and checks
  - Include screenshots or logs if UI or output changes are involved
  - Be focused on a single concern to ease review

---

## Pre-commit and CI Checks

- Pre-commit hooks must include:
  - `ruff` for linting
  - `black` for formatting
  - `mypy` for static typing checks
  - `sqlfluff` for SQL linting in migrations and queries
  - `pytest` for running tests
  - Alembic migration validation

- CI pipelines must enforce all above checks and fail fast on errors.

---

## Operational Rules

- No side effects or heavy logic in `__init__.py` files.
- Seed data scripts must be idempotent to allow safe re-execution.
- All database schema changes must be handled exclusively via Alembic migrations.
- Avoid coupling business logic tightly with infrastructure or environment.

---

## How Codex Should Generate Code

- Generate **one file per run** to maintain atomic, reviewable changes.
- Follow detailed description blocks and interface contracts strictly.
- Respect existing interfaces and abstract classes; do not break contracts.
- Always add comprehensive docstrings to all new code.
- Use idiomatic Python and project conventions consistently.
- Add comments for complex or non-obvious logic to aid maintainability.
- Avoid generating code that introduces side effects or breaks deterministic behavior.

---

## Mental Checklist Before Outputting Code

Before finalizing any code generation, Codex must mentally verify:

- [ ] Code uses Python 3.12 features and syntax correctly.
- [ ] All functions and classes have proper type hints.
- [ ] Pydantic v2 models and validation are used where appropriate.
- [ ] SQLAlchemy 2.x ORM usage follows the 2.0 style API.
- [ ] Logging is structured, meaningful, and free of secrets.
- [ ] No side effects exist in `__init__.py` or unexpected places.
- [ ] Docstrings are comprehensive and clear.
- [ ] Code is formatted with Black and passes Ruff linting.
- [ ] Tests include relevant markers and fixtures, and are deterministic.
- [ ] Environment variables are accessed via Pydantic settings and secrets are not logged.
- [ ] Commit messages and branch names follow conventions if applicable.
- [ ] Alembic migrations are used for all DB schema changes.
- [ ] Code respects interfaces and contracts without breaking existing functionality.
- [ ] Generated output is limited to one file per run.
- [ ] Comments are added for any complex logic or business rules.

---

Following this guide ensures that all contributions by OpenAI Codex maintain the high standards required for the Scheduling Engine project’s success.
