# migrations/env.py
from __future__ import annotations

import os
from logging.config import fileConfig
from typing import Literal
from urllib.parse import quote_plus

from alembic import context

# Load .env/.env.test explicitly for Alembic
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.schema import SchemaItem

# Use your canonical Base and ensure all models are imported
from app.db.base import Base, import_all_models

# ---------------------------------------------------------------------------
# Alembic config & logging
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name, disable_existing_loggers=False)
    except Exception:
        # If logging sections are missing/malformed, skip configuring logging.
        pass

# Ensure metadata is populated from all model modules
import_all_models()
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Environment selection & URL resolution
# ---------------------------------------------------------------------------
def _truthy(val: str | None) -> bool:
    return (val or "").strip().lower() in {"1", "true", "yes", "on"}


def _load_env() -> None:
    """Load .env or .env.test based on -x env=... (defaults to dev)."""
    x = context.get_x_argument(as_dictionary=True)
    env_name = (x.get("env") or "dev").lower()
    dotenv_path = ".env.test" if env_name == "test" else ".env"
    load_dotenv(dotenv_path)


def _compose_url_from_parts() -> str | None:
    """Build a psycopg URL from DB_* parts if DATABASE_URL isn't provided.
    Use string defaults so types are non-Optional for static analysis.
    """
    user = os.getenv("DB_USER", "")
    pwd = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "")

    # Only compose when the required pieces are present
    if user and pwd and name:
        return f"postgresql+psycopg://{quote_plus(user)}:{quote_plus(pwd)}@{host}:{port}/{name}"
    return None


def _resolve_db_url() -> str:
    """Priority:
    1) env DATABASE_URL (or SQLALCHEMY_DATABASE_URL)
    2) compose from DB_* parts (no app import required)
    3) (optional) last-ditch fallback to app settings if available
    """
    url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")
    if url and url.strip():
        return url
    url = _compose_url_from_parts()
    if url:
        return url

    # Optional last-ditch fallback: use your app's settings if importable
    # (kept to honor your original behavior; safe to remove if you prefer decoupling)
    try:
        from app.config.settings import get_settings  # lazy import

        settings = get_settings()
        return settings.DATABASE_URL or settings.effective_database_url
    except Exception as exc:
        raise RuntimeError(
            "DATABASE_URL is not set and could not be composed from DB_*; " "also failed to import app settings as a fallback."
        ) from exc


# ---------------------------------------------------------------------------
# Autogenerate include rules (safe by default)
# ---------------------------------------------------------------------------
ALLOW_DROPS = _truthy(os.getenv("ALEMBIC_ALLOW_DROPS"))


def include_object(
    obj: SchemaItem,
    name: str | None,
    type_: Literal[
        "schema",
        "table",
        "column",
        "index",
        "unique_constraint",
        "foreign_key_constraint",
    ],
    reflected: bool,
    compare_to: SchemaItem | None,
) -> bool:
    # Never autogenerate operations for Alembic's own version table
    if type_ == "table" and name == "alembic_version":
        return False

    # Conservative safety net: if Alembic "sees" an object in the DB but it doesn't
    # exist in metadata, that's typically a DROP. Block it unless explicitly allowed.
    if reflected and compare_to is None and not ALLOW_DROPS:
        return False

    # Otherwise include it
    return True


# ---------------------------------------------------------------------------
# Offline/Online runners
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    _load_env()
    url = _resolve_db_url()
    # Make sure .ini sees our resolved URL (helps alembic output)
    config.set_main_option("sqlalchemy.url", url)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        # include_schemas=False  # set True if you use multiple schemas
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    _load_env()
    url = _resolve_db_url()
    config.set_main_option("sqlalchemy.url", url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
            # include_schemas=False
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
