"""
===============================================================================
File: app/config/settings.py
Purpose
-------
Single source of truth for configuration (Pydantic BaseSettings). Consumed by
logging, DB engine/session creation, CLI, and run.py.
===============================================================================
"""

from __future__ import annotations

import os
from functools import lru_cache
from importlib import metadata
from typing import Any, ClassVar, Literal, cast
from urllib.parse import quote_plus

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .constants import DB_SCHEME, DEFAULT_TZ

try:
    from dotenv import dotenv_values, load_dotenv
except Exception:

    def load_dotenv(*_: Any, **__: Any) -> None:  # underscores silence ARG001
        return None

    def dotenv_values(*_: Any, **__: Any) -> dict[str, str]:
        return {}


def _env_file_for(target_env: str) -> str:
    """Map 'dev'/'test' to the appropriate .env file name."""
    e = (target_env or "dev").lower()
    return ".env.test" if e == "test" else ".env"


def _load_file_vars_for_env(target_env: str) -> dict[str, Any]:
    """Read key/values directly from the env file for the requested env.

    Does not mutate os.environ; lets us construct Settings deterministically.
    """
    try:
        file_vars = dotenv_values(_env_file_for(target_env))
        # strip None values (dotenv returns None for missing)
        return {k: v for k, v in file_vars.items() if v is not None}
    except Exception:
        return {}


# Load the appropriate env file once on import (dev/test only).
_env = os.getenv("APP_ENV", "dev").lower()
_env_file = ".env.test" if _env == "test" else ".env"
if load_dotenv is not None:
    # override=False so real environment variables still win in CI/Prod
    load_dotenv(_env_file, override=False)


class BaseSettings(BaseModel):
    """Lightweight settings base class that hydrates values from the environment."""

    model_config = ConfigDict(extra="ignore")
    ENV_PREFIX: ClassVar[str] = ""

    def __init__(self, **data: Any) -> None:  # noqa: D107 - documented in class docstring
        merged = {**self._load_environment_values(), **data}
        super().__init__(**merged)

    @classmethod
    def _load_environment_values(cls) -> dict[str, Any]:
        """Return environment-driven values respecting the configured prefix."""

        prefix = cls.ENV_PREFIX
        values: dict[str, Any] = {}
        for field_name in cls.model_fields:
            env_key = f"{prefix}{field_name}"
            env_value = os.getenv(env_key)
            if env_value is not None:
                values[field_name] = env_value
        return values


_TRUTHY_VALUES: set[str] = {"1", "true", "yes", "on"}
_FALSY_VALUES: set[str] = {"0", "false", "no", "off"}


def _default_app_version() -> str:
    """Return the package version if available, otherwise the declared default."""

    try:
        return metadata.version("scheduling-engine")
    except metadata.PackageNotFoundError:
        return "0.1.0"
    except Exception:
        # Any unexpected issue should not stop the application from starting.
        return "0.1.0"


class Settings(BaseSettings):
    """Centralised configuration model for the scheduling engine."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)
    ENV_PREFIX: ClassVar[str] = ""

    APP_NAME: str = "scheduling-engine"
    APP_VERSION: str = Field(default_factory=_default_app_version)
    APP_ENV: Literal["dev", "test", "prod"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_JSON: bool = False
    TIMEZONE: str = DEFAULT_TZ

    DATABASE_URL: str | None = Field(default=None, repr=False)
    DB_HOST: str | None = "localhost"
    DB_PORT: int | None = 5432
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = Field(default=None, repr=False)

    @field_validator("LOG_JSON", mode="before")
    @classmethod
    def _coerce_bool(cls, value: Any) -> bool:
        """Coerce common truthy/falsey values to boolean."""

        if isinstance(value, bool) or value is None:
            return bool(value)
        if isinstance(value, int | float):
            return bool(value)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in _TRUTHY_VALUES:
                return True
            if lowered in _FALSY_VALUES:
                return False
        return bool(value)

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def _validate_database_url(cls, value: str | None) -> str | None:
        """Ensure explicit database URLs are non-empty when provided."""

        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("DATABASE_URL cannot be blank")
        return stripped

    @model_validator(mode="after")
    def _validate_database_parts(self) -> Settings:
        """Validate that database configuration is complete when composing URLs."""

        if self.DATABASE_URL:
            return self

        missing_parts = [
            name
            for name, value in (
                ("DB_USER", self.DB_USER),
                ("DB_PASSWORD", self.DB_PASSWORD),
                ("DB_HOST", self.DB_HOST),
                ("DB_PORT", self.DB_PORT),
                ("DB_NAME", self.DB_NAME),
            )
            if value in {None, ""}
        ]
        if missing_parts:
            missing = ", ".join(missing_parts)
            raise ValueError(f"database configuration incomplete: {missing}")
        return self

    @property
    def effective_database_url(self) -> str:
        """Return the effective SQLAlchemy database URL with psycopg scheme."""

        if self.DATABASE_URL:
            return self.DATABASE_URL

        if not all((self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_NAME)):
            raise ValueError("database configuration incomplete for URL composition")

        user = quote_plus(cast(str, self.DB_USER))
        password = quote_plus(cast(str, self.DB_PASSWORD))
        host = cast(str, self.DB_HOST)
        port = cast(int, self.DB_PORT)
        name = cast(str, self.DB_NAME)
        return f"{DB_SCHEME}://{user}:{password}@{host}:{port}/{name}"


@lru_cache(maxsize=3)
def get_settings(env: str | None = None) -> Settings:
    """Return Settings for the requested environment ('dev'|'test'|'prod').

    - If env is provided, read that file directly (.env or .env.test) so we don't
      rely on whatever was loaded at import time.
    - If env is None, fall back to current process environment (which your import-
      time load_dotenv() already initialized).
    """
    selected_env: str = env if env is not None else (os.getenv("APP_ENV") or "dev")
    selected = selected_env.lower()

    # read the right .env file into a dict (does not touch os.environ)
    file_vars = _load_file_vars_for_env(selected)

    # ensure APP_ENV is set consistently
    file_vars["APP_ENV"] = selected

    # Build Settings; BaseSettings merges os.environ values first, then **data**.
    # Because we pass file_vars as **data**, those values win over os.environ.
    return Settings(**file_vars)


__all__ = ["Settings", "get_settings"]
