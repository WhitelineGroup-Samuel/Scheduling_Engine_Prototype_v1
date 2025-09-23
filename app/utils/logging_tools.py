"""
===============================================================================
File: app/utils/logging_tools.py
Purpose:
  Helpers for structured logging: contextvars (trace_id), extra fields, JSON
  formatter support.

Responsibilities:
  - set_trace_id(), get_trace_id()
  - build_log_extra(**kwargs) -> dict usable with logger.bind/extra
  - Optional JSON formatter class

Collaborators:
  - app.config.logging_config
===============================================================================
"""