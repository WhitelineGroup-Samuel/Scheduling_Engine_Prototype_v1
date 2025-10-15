"""
Base scaffolding for all Pydantic (v2) DTOs.

Additions:
- Strict default config on ORMBase (extra=forbid, strip strings, validate defaults)
- UTC utilities (ensure_utc, now_utc)
- UTC coercion in Read mixins (created_at/updated_at normalized to UTC)
- Pagination DTOs (PaginationQuery, PaginationMeta) and SortQuery
- Error/diagnostic envelopes (ErrorEnvelopeDTO, HealthcheckPingDTO)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------
# Core base and config
# ---------------------------


class ORMBase(BaseModel):
    """Base class for all DTOs with strict API hygiene and ORM compatibility."""

    model_config = ConfigDict(
        # Load directly from SQLAlchemy attributes
        from_attributes=True,
        populate_by_name=True,
        # Strict request payloads
        extra="forbid",  # reject unknown fields
        str_strip_whitespace=True,  # trim all incoming strings
        validate_default=True,  # validate defaults too
    )


# ---------------------------
# UTC helpers
# ---------------------------


def now_utc() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(UTC)


def ensure_utc(value: datetime | str | None) -> datetime | None:
    """
    Coerce a datetime or ISO string to timezone-aware UTC.
    Returns None if input is None.
    """
    if value is None:
        return None
    dt = datetime.fromisoformat(value) if isinstance(value, str) else value

    if dt.tzinfo is None:
        # Assume naive -> UTC
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


# ---------------------------
# Read mixins (with UTC coercion)
# ---------------------------


class IdModelMixin(ORMBase):
    """Generic id carrier if you craft helpers that rely on a standard 'id' field name."""

    id: int


class CreatedStampedReadMixin(ORMBase):
    """
    Include created_* fields in READ DTOs only.
    Maps 1:1 to CreatedStampedMixin on the models layer.
    """

    created_at: datetime | None = None
    created_by_user_id: int

    @field_validator("created_at", mode="before")
    @classmethod
    def _coerce_created_at_to_utc(cls, v: Any) -> Any:
        # Accept None/str/datetime; return tz-aware UTC or None
        return ensure_utc(v)


class UpdatedStampedReadMixin(ORMBase):
    """
    Include updated_* fields in READ DTOs only.
    Maps 1:1 to UpdatedStampedMixin on the models layer.
    """

    updated_at: datetime | None = None
    updated_by_user_id: int | None = None

    @field_validator("updated_at", mode="before")
    @classmethod
    def _coerce_updated_at_to_utc(cls, v: Any) -> Any:
        return ensure_utc(v)


# ---------------------------
# Pagination + sorting
# ---------------------------


class PaginationQuery(ORMBase):
    """
    Standard query payload for paginated endpoints.
    Apply cap/validation at the API layer as needed.
    """

    page: int = Field(1, ge=1, description="1-based page number")
    per_page: int = Field(50, ge=1, le=500, description="Page size (1..500)")

    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginationMeta(ORMBase):
    """Metadata returned with paginated lists."""

    total: int
    page: int
    per_page: int
    pages: int


class SortQuery(ORMBase):
    """
    Simple sorting descriptor.
    Extend to multi-field sorts if needed later.
    """

    order_by: str = Field(min_length=1, description="Column or field name to sort by")
    direction: Literal["asc", "desc"] = "asc"


# ---------------------------
# Error/diagnostic envelopes
# ---------------------------


class ErrorEnvelopeDTO(ORMBase):
    model_config = ConfigDict(extra="ignore")

    code: str
    message: str
    context: dict[str, Any] | None = None


class HealthcheckPingDTO(ORMBase):
    # Accept extra keys so v2 shape ({service, env, ping}) doesn't raise
    model_config = ConfigDict(extra="ignore")

    # v1 (flat) fields
    ok: bool | None = None
    duration_ms: float | None = None
    database: str | None = None
    server_version: str | None = None

    # v2 (nested) fields – accepted but not required
    service: str | None = None
    env: str | None = None
    ping: dict[str, Any] | None = None

    @model_validator(mode="after")
    def _derive_from_ping(self) -> HealthcheckPingDTO:
        """
        If the v2 shape is provided (ping contains ok/duration_ms),
        lift them into the top-level fields when those are missing.
        """
        if self.ping:
            if self.ok is None and "ok" in self.ping:
                self.ok = bool(self.ping["ok"])
            if self.duration_ms is None and "duration_ms" in self.ping:
                self.duration_ms = float(self.ping["duration_ms"])
        return self
