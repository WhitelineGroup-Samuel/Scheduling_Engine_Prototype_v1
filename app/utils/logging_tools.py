"""
===============================================================================
File: app/utils/logging_tools.py
Purpose
-------
Provide small, focused helpers for logging context and IDs:
- A contextvar-backed `trace_id` with helpers to create, set, and read it.
- A context manager to bind a trace id around an operation.
- Optional LoggerAdapter or `build_log_extra()` to attach structured extras.

What Codex must implement
-------------------------
Trace ID API:
- TRACE_ID_VAR: contextvars.ContextVar[str | None]
- new_trace_id() -> str
    * Return a random 16–32 hex string (e.g., 16 hex chars). Stable length is good.
- get_trace_id() -> str | None
    * Return the current trace id from context (or None).
- ensure_trace_id() -> str
    * Return current if present else generate+set a new id (also return it).
- with_trace_id(trace_id: str) -> context manager
    * Set the provided id for the duration of the context, then restore previous.

Optional helpers:
- build_log_extra(**kwargs) -> dict
    * Return a dict that can be passed as `extra=` to logger calls to include structured fields.
- (Optional) ContextLoggerAdapter(logging.LoggerAdapter)
    * Injects default context fields (component, job_id, etc.) into each log.

Contract with logging_config
----------------------------
- TraceIdFilter in logging_config will call `get_trace_id()` and/or `ensure_trace_id()`.
- No dependency back from this module to settings; keep it pure/standalone.
- Keep functions tiny and fast; no randomness beyond trace id generation.

Testing ideas (later)
---------------------
- With `with_trace_id()`, nested contexts restore prior values correctly.
- `new_trace_id()` returns fixed-length hex; multiple calls are unique.

Non-goals
---------
- No OpenTelemetry wiring in v1 (can be added later).
- No external correlation propagation (HTTP headers) in v1.

===============================================================================
"""
