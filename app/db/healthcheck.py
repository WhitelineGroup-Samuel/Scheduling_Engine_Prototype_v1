"""
===============================================================================
File: app/db/healthcheck.py
Purpose
-------
Provide a fast, read-only Postgres healthcheck helper.
===============================================================================
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import re
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Final, cast

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.errors.exceptions import DBConnectionError

__all__ = ["ping"]

_VERSION_REGEX: Final[re.Pattern[str]] = re.compile(r"(\d+(?:\.\d+)*)")

_operational_errors: tuple[type[BaseException], ...] = ()

try:  # pragma: no cover
    from sqlalchemy.exc import OperationalError as _SAOperationalError
except Exception:  # pragma: no cover
    pass
else:  # pragma: no cover
    _operational_errors = _operational_errors + (_SAOperationalError,)

_psycopg_errors_mod: ModuleType | None = None
try:  # pragma: no cover
    _psycopg_errors_mod = importlib.import_module("psycopg.errors")
except Exception:  # pragma: no cover
    _psycopg_errors_mod = None
else:  # pragma: no cover
    # Build tuple only from attributes that exist and are exception classes
    ops: list[type[BaseException]] = []
    for name in ("OperationalError", "InvalidCatalogName"):
        err_cls = getattr(_psycopg_errors_mod, name, None)
        if isinstance(err_cls, type) and issubclass(err_cls, BaseException):
            ex: type[BaseException] = err_cls
            ops.append(ex)
    if ops:
        _operational_errors = _operational_errors + tuple(ops)


def _elapsed_ms(start: float) -> float:
    """Return elapsed milliseconds since ``start`` (monotonic timestamp)."""

    return (time.monotonic() - start) * 1000.0


def _assert_within_timeout(start: float, timeout_seconds: float, context: Mapping[str, Any]) -> None:
    """Raise :class:`DBConnectionError` if the allotted timeout has elapsed."""

    if (time.monotonic() - start) > timeout_seconds:
        raise DBConnectionError(
            message="Database healthcheck failed",
            context={**context, "timeout_s": timeout_seconds},
        )


def _build_context(database: str | None, timeout_seconds: float, driver: str | None) -> dict[str, Any]:
    context: dict[str, Any] = {
        "database": database,
        "timeout_s": timeout_seconds,
        "op": "healthcheck.ping",
    }
    if driver:
        context["driver"] = driver
    return context


def ping(engine_or_session: Engine | Session, *, timeout_seconds: float = 5.0) -> dict[str, Any]:
    """Perform a read-only healthcheck against Postgres.

    Parameters
    ----------
    engine_or_session:
        Either a SQLAlchemy ``Engine`` or an active ``Session``. When an
        engine is provided a new connection is opened and explicitly closed at
        the end of the check. Sessions reuse their existing connection.
    timeout_seconds:
        Overall time budget for the healthcheck. Exceeding the limit raises a
        :class:`DBConnectionError`.

    Returns
    -------
    dict[str, Any]
        Structured payload describing the target database, server version, and
        the elapsed time in milliseconds.

    Raises
    ------
    DBConnectionError
        When any of the read-only statements fail or the timeout is exceeded.
    """

    start = time.monotonic()
    database_name: str | None = None
    driver_name: str | None = None

    if isinstance(engine_or_session, Engine):
        connection = engine_or_session.connect()
        should_close = True
        driver_name = engine_or_session.dialect.driver
    else:
        connection = engine_or_session.connection()
        should_close = False
        with contextlib.suppress(Exception):
            bind = engine_or_session.get_bind()
            driver_name = bind.dialect.driver

    context = _build_context(database_name, timeout_seconds, driver_name)
    server_version_full: str | None = None

    try:
        _assert_within_timeout(start, timeout_seconds, context)
        connection.execute(text("SELECT 1"))
        _assert_within_timeout(start, timeout_seconds, context)

        try:
            server_version_full_result = connection.execute(text("SHOW server_version"))
            server_version_full = str(server_version_full_result.scalar_one())
            server_version = server_version_full
        except _operational_errors:
            version_row = connection.execute(text("SELECT version()"))
            server_version_full = str(version_row.scalar_one())
            match = _VERSION_REGEX.search(server_version_full)
            if not match:
                raise DBConnectionError(
                    message="Database healthcheck failed",
                    context=context,
                ) from None
            server_version = match.group(1)

        _assert_within_timeout(start, timeout_seconds, context)

        database_result = connection.execute(text("SELECT current_database()"))
        database_name = str(database_result.scalar_one())
        context = _build_context(database_name, timeout_seconds, driver_name)
        _assert_within_timeout(start, timeout_seconds, context)

        result: dict[str, Any] = {
            "ok": True,
            "database": database_name,
            "server_version": server_version,
            "server_version_full": server_version_full,
            "duration_ms": _elapsed_ms(start),
        }
        return result
    except _operational_errors as exc:
        raise DBConnectionError(
            message="Database healthcheck failed",
            context=_build_context(database_name, timeout_seconds, driver_name),
        ) from exc
    except Exception as exc:
        raise DBConnectionError(
            message="Database healthcheck failed",
            context=_build_context(database_name, timeout_seconds, driver_name),
        ) from exc
    finally:
        if should_close:
            connection.close()


GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"


@dataclass
class CheckResult:
    env: str
    ok: bool
    messages: list[str]


# Adjust when you upgrade the container image
PG_EXPECTED = "17.2"


def _alembic_head_revision() -> str:
    """Read the repository HEAD revision (no DB access)."""
    cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(cfg)
    return cast(str, script.get_current_head())


def _extensions_ok(engine: Engine, required: Iterable[str]) -> tuple[bool, str]:
    req = {x.strip() for x in required if x and x.strip()}
    if not req:
        return True, "no required extensions specified"

    # SQLAlchemy 2.0 style: open a connection and execute on the connection
    with engine.connect() as conn:
        rows = cast(list[str], conn.execute(text("select extname from pg_extension")).scalars().all())

    present = set(rows)
    missing = sorted(req - present)
    if not missing:
        return True, f"extensions present: {', '.join(sorted(req))}"
    return False, f"missing extensions: {', '.join(missing)} (present: {', '.join(sorted(present))})"


def _alembic_current(engine: Engine) -> str | None:
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        return cast(str | None, ctx.get_current_revision())


def _pg_version_ok(server_version: str) -> tuple[bool, str]:
    # Your ping() has already normalized version to "major.minor" where possible
    if server_version.startswith(PG_EXPECTED):
        return True, f"PostgreSQL {server_version}"
    return False, f"Expected {PG_EXPECTED}, got {server_version}"


def check_env(env: str, required_extensions: Iterable[str]) -> CheckResult:
    msgs: list[str] = []
    ok = True

    # Resolve URL from your project settings (respects .env/.env.test)
    s = get_settings(env=env)
    url = s.effective_database_url

    # Use SQLAlchemy engine and your existing ping() for base connectivity+version
    engine = create_engine(url, future=True, pool_pre_ping=True)
    try:
        ping_result = ping(engine)  # reuse your helper
        msgs.append(f"{GREEN}connect: ok → {url}{RESET}")

        good, ver_msg = _pg_version_ok(str(ping_result.get("server_version")))
        msgs.append((GREEN if good else YELLOW) + f"version: {ver_msg}" + RESET)
        ok &= good

        good, ext_msg = _extensions_ok(engine, required_extensions)
        msgs.append((GREEN if good else YELLOW) + f"extensions: {ext_msg}" + RESET)
        ok &= good

        head = _alembic_head_revision()
        current = _alembic_current(engine)
        if current is None:
            msgs.append(f"{YELLOW}alembic: database is not stamped (current=None), repo head={head}{RESET}")
            ok = False
        elif current == head:
            msgs.append(f"{GREEN}alembic: at head ({head}){RESET}")
        else:
            msgs.append(f"{YELLOW}alembic: behind → db={current}, head={head}{RESET}")
            ok = False
    except Exception as e:
        msgs.append(f"{RED}connect/check failed: {e}{RESET}")
        ok = False
    finally:
        with contextlib.suppress(Exception):
            engine.dispose()

    return CheckResult(env, ok, msgs)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Whiteline DB healthcheck")
    p.add_argument("--env", choices=["dev", "test", "both"], default="both", help="Which environment to check")
    p.add_argument(
        "--require-extensions",
        default="pg_trgm",
        help="Comma-separated list of required extensions (default: pg_trgm). " "Use empty string to disable extension check.",
    )
    args = p.parse_args(argv)

    required = [x.strip() for x in (args.require_extensions or "").split(",")] if args.require_extensions is not None else []

    envs = ["dev", "test"] if args.env == "both" else [args.env]

    print(f"{BOLD}=== DB Healthcheck ({', '.join(envs)}) ==={RESET}")
    overall_ok = True
    for e in envs:
        print(f"\n{BOLD}[{e}]{RESET}")
        res = check_env(e, required)
        for m in res.messages:
            print(" -", m)
        overall_ok &= res.ok

    print()
    if overall_ok:
        print(f"{GREEN}OK: all checks passed{RESET}")
        return 0
    else:
        print(f"{RED}FAIL: one or more checks failed{RESET}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
