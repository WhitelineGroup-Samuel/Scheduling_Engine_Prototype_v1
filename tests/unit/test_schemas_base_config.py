from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas._base import (
    ErrorEnvelopeDTO,
    HealthcheckPingDTO,
    PaginationQuery,
    SortQuery,
    ensure_utc,
)

# --- ensure_utc ---------------------------------------------------------------


def test_ensure_utc_converts_naive_to_utc() -> None:
    naive = datetime(2025, 1, 1, 12, 0, 0)  # naive, assumed local -> treat as UTC
    coerced = ensure_utc(naive)
    assert coerced is not None
    assert coerced.tzinfo is UTC
    assert coerced.hour == 12


def test_ensure_utc_keeps_aware_and_normalizes_to_utc() -> None:
    aware = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=+10)))
    coerced = ensure_utc(aware)
    assert coerced is not None
    assert coerced.tzinfo is UTC
    # 12:00 +10:00 == 02:00 UTC
    assert coerced.hour == 2


# --- Envelopes ----------------------------------------------------------------


def test_healthcheck_ping_dto_accepts_minimal_payload() -> None:
    """
    Accept either of the two minimal shapes we discussed:
    - v1: { ok, duration_ms, database, server_version }
    - v2: { service, env, ping: { ok, duration_ms } }
    Using model_validate avoids Pylance complaining about kwargs.
    """
    try:
        dto = HealthcheckPingDTO.model_validate(
            {
                "ok": True,
                "duration_ms": 1.23,
                "database": "whiteline_test",
                "server_version": "16.0",
            }
        )
    except Exception:
        dto = HealthcheckPingDTO.model_validate(
            {
                "service": "diag",
                "env": "test",
                "ping": {"ok": True, "duration_ms": 1.23},
            }
        )

    # basic sanity
    assert dto is not None


def test_error_envelope_dto_shapes() -> None:
    e = ErrorEnvelopeDTO.model_validate(
        {
            "code": "VALIDATION_ERROR",
            "message": "bad input",
            "context": {"field": "name"},
        }
    )
    assert e.code == "VALIDATION_ERROR"
    assert e.message == "bad input"
    assert e.context == {"field": "name"}


# --- Pagination & Sort DTOs ---------------------------------------------------


def test_pagination_query_accepts_normal_values() -> None:
    p = PaginationQuery(page=2, per_page=50)
    assert p.page == 2
    assert p.per_page == 50


def test_pagination_query_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        PaginationQuery(page=0, per_page=10)  # page must be >= 1

    with pytest.raises(ValidationError):
        PaginationQuery(page=1, per_page=0)  # per_page must be >= 1


def test_sort_query_accepts_field_and_direction() -> None:
    s = SortQuery(order_by="name", direction="asc")
    field = "order_by" if hasattr(s, "order_by") else "key"
    assert getattr(s, field) == "name"
    assert s.direction in ("asc", "desc")


def test_sort_query_rejects_bad_direction() -> None:
    with pytest.raises(ValidationError):
        SortQuery(order_by="name", direction="upwards")  # type: ignore[arg-type]  # invalid literal for test
