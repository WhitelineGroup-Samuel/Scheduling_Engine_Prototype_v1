"""Shared DTO primitives and helpers for the Scheduling Engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, field_validator

__all__ = [
    "BaseDTO",
    "TimestampsDTO",
    "PaginationQuery",
    "PaginationMeta",
    "SortQuery",
    "HealthcheckPingDTO",
    "ErrorEnvelopeDTO",
    "ensure_utc",
    "now_utc",
    "to_json",
]


class BaseDTO(BaseModel):
    """Base class for all DTOs with project-wide configuration."""

    model_config = ConfigDict(
        frozen=False,
        extra="forbid",
        populate_by_name=False,
        str_strip_whitespace=True,
        validate_default=True,
        ser_json_timedelta="iso8601",
        ser_json_inf_nan=cast(Any, False),
    )


def now_utc() -> datetime:
    """Return the current UTC time as an aware :class:`datetime`."""

    return datetime.now(timezone.utc)


def ensure_utc(value: datetime | str) -> datetime:
    """Coerce a datetime-like value to a timezone-aware UTC datetime."""

    if isinstance(value, str):
        value = value.strip()
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:  # pragma: no cover - defensive branch
            raise ValueError("Invalid datetime string") from exc
        value = parsed

    # At this point, by type contract, `value` is a datetime
    value_dt: datetime = value
    if value_dt.tzinfo is None:
        return value_dt.replace(tzinfo=timezone.utc)
    return value_dt.astimezone(timezone.utc)


class TimestampsDTO(BaseDTO):
    """Mixin providing UTC-aware creation and update timestamps."""

    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _coerce_utc(cls, value: datetime | str) -> datetime:
        """Ensure stored timestamps are normalized to UTC."""

        return ensure_utc(value)


class PaginationQuery(BaseDTO):
    """Pagination inputs used by list-style repository queries."""

    page: int = 1
    page_size: int = 50
    sort: str | None = None
    search: str | None = None

    @field_validator("page")
    @classmethod
    def _validate_page(cls, value: int) -> int:
        """Validate that the page number is at least one."""

        if value < 1:
            raise ValueError("page must be greater than or equal to 1")
        return value

    @field_validator("page_size")
    @classmethod
    def _validate_page_size(cls, value: int) -> int:
        """Validate the configured page size is within accepted bounds."""

        if not 1 <= value <= 100:
            raise ValueError("page_size must be between 1 and 100")
        return value


class PaginationMeta(BaseDTO):
    """Metadata describing the pagination state for list responses."""

    page: int
    page_size: int
    total: int


class SortQuery(BaseDTO):
    """Sorting-only query payload used by some CLI commands."""

    sort: str | None = None


class HealthcheckPingDTO(BaseDTO):
    """Structured payload returned by the healthcheck diagnostic command."""

    ok: bool
    database: str
    server_version: str
    duration_ms: float

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HealthcheckPingDTO":
        """Build an instance from a mapping produced by adapters."""

        return cls.model_validate(payload)


class ErrorEnvelopeDTO(BaseDTO):
    """Machine-readable error contract used across CLI boundaries."""

    code: str
    message: str
    exit_code: int
    severity: Literal["INFO", "WARN", "ERROR", "CRITICAL"]
    context: dict[str, object] | None = None


def to_json(obj: BaseDTO) -> str:
    """Serialise a DTO to JSON using the configured encoding rules."""

    return obj.model_dump_json()
