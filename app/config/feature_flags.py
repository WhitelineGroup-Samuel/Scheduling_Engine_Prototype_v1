"""
===============================================================================
File: app/config/feature_flags.py
Purpose:
  Toggle experimental features via env/YAML. Simple gate checks used by CLI
  and (later) scheduling modules.

Responsibilities:
  - read_flags(settings) -> Dict[str, bool]
  - is_enabled(name: str) -> bool

Collaborators:
  - app.config.settings
  - app.utils.io (YAML/JSON helpers for optional overrides)

Testing:
  - Confirm precedence: env > file > defaults.
===============================================================================
"""
