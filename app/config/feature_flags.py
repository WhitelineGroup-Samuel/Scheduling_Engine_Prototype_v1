"""
===============================================================================
File: app/config/feature_flags.py
Purpose:
  Toggle experimental features via env/YAML. Simple gate checks used by CLI
  and (later) scheduling modules.
===============================================================================
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

from .paths import REPO_ROOT

io_helpers: ModuleType | None
try:  # pragma: no cover - optional dependency fallback
    from app.utils import io as io_helpers
except ImportError:  # pragma: no cover - optional fallback
    io_helpers = None

if io_helpers is not None:  # pragma: no cover - helper discovery
    _read_json_helper = getattr(io_helpers, "read_json", None)
    _read_yaml_helper = getattr(io_helpers, "read_yaml", None)
else:  # pragma: no cover - helper discovery fallback
    _read_json_helper = None
    _read_yaml_helper = None

if TYPE_CHECKING:  # pragma: no cover
    from .settings import Settings

_TRUTHY_VALUES: set[str] = {"1", "true", "yes", "on"}
_FALSY_VALUES: set[str] = {"0", "false", "no", "off"}

_FEATURE_ENV_PREFIX = "FEATURE_"
_FLAG_FILE_YAML: Path = REPO_ROOT / "feature_flags.yml"
_FLAG_FILE_JSON: Path = REPO_ROOT / "feature_flags.json"

DEFAULT_FLAGS: dict[str, bool] = {}
_FLAGS_CACHE: dict[str, bool] | None = None


def _normalise_name(name: str) -> str:
    """Normalise a feature flag name for consistent lookups."""

    return name.strip().lower()


def _coerce_bool(value: Any) -> bool:
    """Coerce arbitrary inputs into booleans using relaxed parsing rules."""

    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in _TRUTHY_VALUES:
            return True
        if lowered in _FALSY_VALUES:
            return False
    return bool(value)


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Load YAML content if support is available."""

    if _read_yaml_helper is not None:
        try:
            data = _read_yaml_helper(path)
        except FileNotFoundError:
            return None
        return data if isinstance(data, dict) else None

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:  # pragma: no cover - optional dependency
        return None

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else None


def _load_json(path: Path) -> dict[str, Any] | None:
    """Load JSON content using helper or built-in support."""

    if _read_json_helper is not None:
        try:
            data = _read_json_helper(path)
        except FileNotFoundError:
            return None
        return data if isinstance(data, dict) else None

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return None
    return data if isinstance(data, dict) else None


def _load_file_flags() -> dict[str, bool]:
    """Load feature flags from YAML or JSON definitions."""

    raw: dict[str, Any] | None = None
    if _FLAG_FILE_YAML.exists():
        raw = _load_yaml(_FLAG_FILE_YAML)
    elif _FLAG_FILE_JSON.exists():
        raw = _load_json(_FLAG_FILE_JSON)

    if not isinstance(raw, dict):
        return {}

    return {
        _normalise_name(str(key)): _coerce_bool(value) for key, value in raw.items()
    }


def _load_env_flags() -> dict[str, bool]:
    """Load feature flags from the process environment."""

    env_flags: dict[str, bool] = {}
    for key, value in os.environ.items():
        if not key.startswith(_FEATURE_ENV_PREFIX):
            continue
        name = _normalise_name(key[len(_FEATURE_ENV_PREFIX) :])
        env_flags[name] = _coerce_bool(value)
    return env_flags


def read_flags(settings: "Settings") -> dict[str, bool]:
    """Return the merged feature flags for the provided settings."""

    _ = settings.APP_ENV  # Access eagerly to assert presence and avoid lints.

    defaults = {_normalise_name(key): bool(val) for key, val in DEFAULT_FLAGS.items()}
    file_flags = _load_file_flags()
    env_flags = _load_env_flags()

    merged: dict[str, bool] = {**defaults, **file_flags, **env_flags}

    global _FLAGS_CACHE
    _FLAGS_CACHE = dict(merged)
    return dict(merged)


def is_enabled(name: str, *, flags: dict[str, bool] | None = None) -> bool:
    """Return whether a flag is enabled, consulting cached values when available."""

    candidate_flags = flags
    if candidate_flags is None:
        global _FLAGS_CACHE
        if _FLAGS_CACHE is None:
            from . import get_settings

            candidate_flags = read_flags(get_settings())
        else:
            candidate_flags = _FLAGS_CACHE

    return candidate_flags.get(_normalise_name(name), False)


__all__ = ["DEFAULT_FLAGS", "read_flags", "is_enabled"]
