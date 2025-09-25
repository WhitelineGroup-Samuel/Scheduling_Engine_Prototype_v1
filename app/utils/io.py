"""Minimal JSON and YAML file IO helpers used by configuration routines."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Protocol, cast


class _YamlProtocol(Protocol):  # pragma: no cover - typing helper
    """Protocol describing the subset of PyYAML used by this module."""

    def safe_load(self, stream: str) -> Any:  # pragma: no cover - signature stub
        """Deserialize YAML from ``stream``."""

    def safe_dump(
        self, data: Any, *, default_flow_style: bool = ...
    ) -> str:  # pragma: no cover - signature stub
        """Serialize ``data`` to a YAML string."""


def ensure_dir(path: str | Path) -> Path:
    """Ensure a directory for ``path`` exists and return that directory.

    Args:
        path: Either a directory path or a file path whose parent should exist.

    Returns:
        Path: The directory that was created or already existed.
    """

    path_obj = Path(path)
    directory = path_obj if path_obj.suffix == "" else path_obj.parent
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _to_path(path: str | Path) -> Path:
    """Convert ``path`` to :class:`Path` without performing IO."""

    return Path(path)


def _load_yaml_module() -> _YamlProtocol:
    """Import and return the PyYAML module, raising :class:`ImportError` if missing."""

    try:
        module = importlib.import_module("yaml")
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency absence
        raise ImportError("PyYAML is required to work with YAML files") from exc
    return cast(_YamlProtocol, module)


def read_json(path: str | Path) -> Any:
    """Read and deserialize a UTF-8 encoded JSON file.

    Args:
        path: The JSON file to read.

    Returns:
        Any: The deserialized Python object.
    """

    file_path = _to_path(path)
    text = file_path.read_text(encoding="utf-8")
    return json.loads(text)


def write_json(path: str | Path, data: Any, *, indent: int = 2) -> Path:
    """Serialize ``data`` as JSON and write it to ``path`` using UTF-8 encoding.

    Args:
        path: The destination file path.
        data: JSON-serialisable data to write.
        indent: Indentation applied during serialisation.

    Returns:
        Path: The path written to.
    """

    file_path = _to_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, indent=indent)
    if not serialized.endswith("\n"):
        serialized += "\n"
    file_path.write_text(serialized, encoding="utf-8", newline="\n")
    return file_path


def read_yaml(path: str | Path) -> Any:
    """Read a YAML file using :func:`yaml.safe_load` if PyYAML is installed.

    Args:
        path: The YAML file to read.

    Returns:
        Any: The deserialized object.

    Raises:
        ImportError: If PyYAML is not available in the runtime environment.
    """

    file_path = _to_path(path)
    text = file_path.read_text(encoding="utf-8")
    module = _load_yaml_module()
    return module.safe_load(text)


def write_yaml(path: str | Path, data: Any) -> Path:
    """Serialize ``data`` to YAML using :func:`yaml.safe_dump` when available.

    Args:
        path: The destination YAML file path.
        data: The object to serialise.

    Returns:
        Path: The path written to.

    Raises:
        ImportError: If PyYAML is not installed.
    """

    file_path = _to_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    module = _load_yaml_module()
    serialized = module.safe_dump(data, default_flow_style=False)
    if not serialized.endswith("\n"):
        serialized += "\n"
    file_path.write_text(serialized, encoding="utf-8", newline="\n")
    return file_path


__all__ = [
    "ensure_dir",
    "read_json",
    "write_json",
    "read_yaml",
    "write_yaml",
]
