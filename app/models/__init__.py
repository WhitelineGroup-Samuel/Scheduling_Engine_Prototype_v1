"""
===============================================================================
Package: app.models
Purpose:
  House all ORM model modules. Alembic visibility is achieved by dynamically
  importing these modules via `app.db.base.import_all_models()` before
  autogenerate runs.

Guidelines
----------
- DO NOT eagerly import models here (avoid side effects).
- Each model module should import Base from app.db.base and declare ORM classes.
- Optionally maintain __all__ for discoverability (not required for Alembic).

First visible entity
--------------------
- organisations (see app.models.core.Organisation)
===============================================================================
"""

# Optional export list (informational; not required for Alembic)
__all__: list[str] = [
    # "Organisation",  # uncomment if you want explicit exports later
]
