"""
===============================================================================
File: app/utils/time.py
Purpose:
  Timezone-safe datetime helpers (AUS Eastern aware), monotonic timers,
  and formatting utilities.

Responsibilities:
  - now_tz(tz_name) -> aware datetime
  - measure_duration(callable) or context timer
  - format_dt/duration helpers

Collaborators:
  - app.config.settings.TIMEZONE
===============================================================================
"""