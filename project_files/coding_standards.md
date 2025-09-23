
# Coding Standards

## Introduction

This document details the coding standards for all development work on this project. The goal is to ensure code quality, maintainability, and consistency across Python and SQL codebases. All standards are based on modern industry best practices and assume the following baseline environments:

- **Python:** 3.9.6
- **Postgres:** 17.2
- **OS:** macOS

## Python Standards

- **Dependency Management:** Use [Poetry](https://python-poetry.org/) or [uv](https://github.com/astral-sh/uv) for dependency management and virtual environments. Do not use `pip` directly or maintain requirements.txt files.
- **Linting & Formatting:** Enforce [Ruff](https://docs.astral.sh/ruff/) for linting and [Black](https://black.readthedocs.io/en/stable/) for code formatting. Both should be run as pre-commit hooks and in CI.
- **Type Checking:** Use [mypy](https://mypy-lang.org/) in `--strict` mode. All code must have type annotations.
- **Testing:** Use [pytest](https://docs.pytest.org/) for all automated testing.
- **Documentation:** Use minimal docstrings for all public functions, classes, and methods. Avoid excessive inline comments; only comment on complex or non-obvious logic.
- **Imports:** Use absolute imports except for intra-package imports; group standard library, third-party, and local imports separately.
- **Error Handling:** Use built-in exceptions where possible. Only use custom exceptions for domain-specific errors.
- **ORM Usage:** Use an ORM (e.g., SQLAlchemy) as the primary interface to the database. Avoid raw SQL except for performance-critical or complex queries.

## SQL Standards

- **Schema Management:** All schema changes must be managed through migrations (see below).
- **Table Naming:** Use `snake_case`, plural nouns (e.g., `users`, `order_items`).
- **Primary Keys:** Name as `table_name_id` (e.g., `user_id`). Use `SERIAL` or `BIGSERIAL` for integer PKs, or UUIDs if justified.
- **Foreign Keys:** Name as `referenced_table_id` (e.g., `user_id`, `team_id`).
- **Timestamps:** Always use `TIMESTAMPTZ` for timestamps. Default to `NOW()` for created/updated columns.
- **Constraints:** Always define explicit `NOT NULL`, `UNIQUE`, and `CHECK` constraints where appropriate.
- **Indexing:** Add indexes for foreign keys and frequently queried columns.
- **ORM-First:** Prefer generating schema via ORM models and migrations, not hand-written DDL.

## Migration Standards

- **Tooling:** Use [Alembic](https://alembic.sqlalchemy.org/) for all database migrations.
- **Process:** 
  - Migrations must be generated from ORM model changes.
  - All migrations must be reviewed and tested before merging.
  - Never edit migration files after they are committed; instead, create a new migration for changes.
- **Versioning:** Use sequential, timestamped migration files.
- **Idempotency:** Migrations must be idempotent and reversible when possible.

## Style & Naming Conventions

- **Python:**
  - Use `snake_case` for variables, functions, and methods.
  - Use `CamelCase` for classes.
  - Constants in `UPPER_SNAKE_CASE`.
  - Private members prefixed with `_`.
  - Max line length: 88 (Black default).
- **SQL:**
  - Use `snake_case` for all identifiers.
  - Plural table names.
  - Primary/foreign keys as `<table>_id`.
  - All timestamps as `TIMESTAMPTZ`.
- **General:**
  - Avoid abbreviations unless industry standard.
  - Use clear, descriptive names.
  - Only comment on complex or non-obvious logic.

## Examples (Good vs Bad)

### Python

#### Good
```python
from datetime import datetime
from typing import List

class User:
    """Represents a user in the system."""
    def __init__(self, user_id: int, name: str, created_at: datetime) -> None:
        self.user_id = user_id
        self.name = name
        self.created_at = created_at

def get_active_users(users: List[User]) -> List[User]:
    """Return users created in the last 30 days."""
    cutoff = datetime.utcnow() - timedelta(days=30)
    return [u for u in users if u.created_at > cutoff]
```

#### Bad
```python
import datetime

class user:
    def __init__(self, id, n, c):
        self.id = id
        self.n = n
        self.c = c

def activeUsers(usrList):
    # get users created recently
    result = []
    for u in usrList:
        if u.c > datetime.datetime.utcnow() - datetime.timedelta(days=30):
            result.append(u)
    return result
```

### SQL

#### Good
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    amount NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### Bad
```sql
CREATE TABLE User (
    id INT PRIMARY KEY,
    Name varchar(100),
    CreatedAt timestamp
);

CREATE TABLE Order (
    id INT PRIMARY KEY,
    User INT,
    Amount float,
    CreatedAt timestamp
);
```
