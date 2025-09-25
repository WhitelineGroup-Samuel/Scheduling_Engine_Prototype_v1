"""Utility helpers for working with structured logging trace identifiers."""

from __future__ import annotations

import contextlib
import contextvars
import secrets
from typing import Any, Iterator

TRACE_ID_VAR: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "trace_id", default=None
)
"""Context variable storing the current trace identifier."""


def new_trace_id() -> str:
    """Generate a fresh 16-character hexadecimal trace identifier.

    Returns:
        str: A random lower-case hexadecimal string suitable for correlation IDs.
    """

    return secrets.token_hex(8)


def get_trace_id() -> str | None:
    """Retrieve the trace identifier currently bound to the active context.

    Returns:
        str | None: The active trace identifier, if one has been set.
    """

    return TRACE_ID_VAR.get()


def ensure_trace_id() -> str:
    """Return the active trace identifier, creating one if missing.

    Returns:
        str: The existing or newly generated trace identifier.
    """

    current = TRACE_ID_VAR.get()
    if current is not None:
        return current
    new_id = new_trace_id()
    TRACE_ID_VAR.set(new_id)
    return new_id


@contextlib.contextmanager
def with_trace_id(trace_id: str) -> Iterator[None]:
    """Temporarily bind ``trace_id`` to the context inside a ``with`` block.

    Args:
        trace_id: The identifier to bind for the duration of the context.

    Yields:
        None: Execution proceeds inside the managed context.
    """

    token = TRACE_ID_VAR.set(trace_id)
    try:
        yield
    finally:
        TRACE_ID_VAR.reset(token)


def build_log_extra(**kwargs: Any) -> dict[str, Any]:
    """Return a dictionary suitable for passing as ``extra`` to logger methods.

    Returns:
        dict[str, Any]: A shallow copy of ``kwargs`` for logging APIs.
    """

    return dict(kwargs)


__all__ = [
    "TRACE_ID_VAR",
    "new_trace_id",
    "get_trace_id",
    "ensure_trace_id",
    "with_trace_id",
    "build_log_extra",
]
