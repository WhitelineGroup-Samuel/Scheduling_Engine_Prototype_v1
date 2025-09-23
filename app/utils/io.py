"""
===============================================================================
File: app/utils/io.py
Purpose:
  Safe, minimal file I/O helpers for JSON/YAML/TOML read/write (used by flags).

Responsibilities:
  - read_json(path) / write_json(path, data)
  - read_yaml(path) / write_yaml(path, data)
  - ensure_dir(path)

Dependencies:
  - pyyaml (optional), json, pathlib
===============================================================================
"""
