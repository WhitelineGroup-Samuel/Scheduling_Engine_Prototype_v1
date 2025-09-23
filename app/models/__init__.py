"""
===============================================================================
Package: app.models
Purpose:
  Centralize model imports so Base.metadata includes all tables.

Responsibilities:
  - from .core import *   # and future domain models

Notes:
  - Keep imports side-effectful only for metadata population.
===============================================================================
"""