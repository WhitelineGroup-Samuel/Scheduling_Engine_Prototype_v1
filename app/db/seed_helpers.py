# app/db/seed_helpers.py

from __future__ import annotations

import os
import re
import subprocess
import unicodedata
from collections.abc import Mapping
from typing import Any, TypeVar

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base

# Import the concrete user model so we can ensure the "created_by" user exists.
# Your models file shows the table name "users" with PK "user_account_id" and a unique "email".
from app.models.system.users import UserAccount

# ---------- Types ----------

M = TypeVar("M", bound=Base)


# ---------- Simple console echo ----------


def echo(msg: str) -> None:
    """Lightweight console output for seed steps."""
    print(f"[seed] {msg}")


# ---------- Environment guard ----------


class DevEnvironmentError(RuntimeError):
    """Raised when a seed command attempts to run outside dev without --force."""


def assert_dev_only(settings: Any, *, force: bool = False) -> None:
    """
    Refuse to run unless APP_ENV == 'dev' (unless --force is provided).

    Accept both 'APP_ENV' (your Settings field) and a lowercase fallback.
    """
    # Prefer the Settings field name exactly as defined in your model.
    env = getattr(settings, "APP_ENV", None)
    if env is None:
        # Fallbacks for safety in case of future refactors
        env = getattr(settings, "app_env", None) or os.getenv("APP_ENV")

    env_norm = (env or "").strip().lower()
    if env_norm != "dev" and not force:
        raise DevEnvironmentError(f"Refusing to seed in APP_ENV='{env}'. Set --force to override (not recommended).")


# ---------- Alembic awareness ----------


class MigrationStateError(RuntimeError):
    """Raised when the database is not at Alembic head and --migrate was not used."""


def _is_alembic_at_head() -> bool:
    """
    Return True if the current DB is at Alembic head.

    Implementation note:
      We shell out to 'alembic current --verbose' and look for '(head)' markers.
      This keeps us decoupled from Alembic's internal APIs and your env vars.
    """
    try:
        # We prefer '--verbose' so that '(head)' markers appear consistently.
        proc = subprocess.run(
            ["alembic", "current", "--verbose"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        # If alembic isn't on PATH, we conservatively say "not at head".
        return False

    out = proc.stdout or ""
    # If *any* line shows '(head)', consider it up-to-date for our purposes.
    return "(head)" in out


def ensure_migrations_applied(*, migrate: bool, env: str = "dev") -> None:
    """
    Ensure DB is at Alembic head. If 'migrate=True', run 'upgrade head' automatically.
    Otherwise, raise with a helpful message.

    Parameters
    ----------
    migrate: whether to auto-upgrade.
    env:     Alembic -x env=<env> extra var (your project uses this convention).
    """
    if _is_alembic_at_head():
        return

    if not migrate:
        raise MigrationStateError(
            "Database is not at Alembic head. Re-run with --migrate to upgrade, or run 'alembic -x env=dev upgrade head' yourself and retry."
        )

    # Perform the upgrade:
    echo("Applying Alembic migrations to head...")
    cmd = ["alembic", "-x", f"env={env}", "upgrade", "head"]
    subprocess.run(cmd, check=True)
    echo("Migrations applied.")


# ---------- Slug utility ----------

_slug_hyphen_re = re.compile(r"[^a-z0-9]+")
_slug_strip_re = re.compile(r"^-+|-+$")


def slugify(name: str) -> str:
    """
    Convert an arbitrary name to a stable, lowercased, ASCII-only slug.
    Keeps only [a-z0-9-], collapses runs of non-alphanumerics to '-'.
    """
    if not name:
        return ""
    value = unicodedata.normalize("NFKD", name)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = _slug_hyphen_re.sub("-", value)
    value = _slug_strip_re.sub("", value)
    return value


# ---------- Idempotent helpers ----------


def get_or_create[
    M
](session: Session, model: type[M], where: Mapping[str, Any], defaults: Mapping[str, Any] | None = None,) -> tuple[M, bool]:
    """
    Fetch an existing instance by unique 'where' keys, or create one with 'defaults'.

    Returns
    -------
    (instance, created)
      created == True if a new row was inserted in this call.

    Notes
    -----
    - Portable across DBs, no Postgres-specific 'ON CONFLICT'.
    - Includes a retry on IntegrityError to handle races.
    """
    stmt = sa.select(model).filter_by(**where)
    obj = session.execute(stmt).scalar_one_or_none()
    if obj is not None:
        return obj, False

    data: dict[str, Any] = dict(where)
    if defaults:
        data.update(defaults)

    vals: dict[str, Any] = dict(data)
    obj = model(**vals)
    session.add(obj)
    try:
        session.flush()  # assign PKs without committing
        return obj, True
    except IntegrityError as exc:
        session.rollback()
        # Another process/seed run may have inserted it; fetch again.
        obj = session.execute(stmt).scalar_one_or_none()
        if obj is not None:
            return obj, False
        raise exc


def get_one_by[M](session: Session, model: type[M], where: Mapping[str, Any]) -> M:
    """
    Fetch exactly one row by a unique/natural key; raise with a clear message if missing.
    """
    obj = session.execute(sa.select(model).filter_by(**where)).scalar_one_or_none()
    if obj is None:
        raise LookupError(f"{model.__name__} not found for {dict(where)}")
    return obj


# ---------- Seed admin user ----------

DEFAULT_SEED_ADMIN_EMAIL = "samuel@whitelinegroup.com.au"
DEFAULT_SEED_ADMIN_DISPLAY = "Samuel Ellis"


def ensure_seed_admin_user(
    session: Session,
    *,
    email: str = DEFAULT_SEED_ADMIN_EMAIL,
    display_name: str = DEFAULT_SEED_ADMIN_DISPLAY,
) -> UserAccount:
    """
    Ensure a 'creator' user exists and return the row (for created_by_user_id attribution).

    Your 'users' model shows:
      - PK: user_account_id (SERIAL)
      - Unique: email
    """
    where = {"email": email.lower()}
    defaults = {"display_name": display_name, "is_active": True}
    user, _ = get_or_create(session, UserAccount, where, defaults)
    return user
