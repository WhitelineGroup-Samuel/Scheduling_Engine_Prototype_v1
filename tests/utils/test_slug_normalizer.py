from __future__ import annotations

import importlib
from collections.abc import Callable

import pytest


def _load_slug_normalizer() -> Callable[[str], str]:
    """
    Find a public slug normalizer.
    Priority:
      1) app.schemas.system.organisations.OrganisationCreate.normalize_slug (if present)
      2) app.db.seed._fallback_normalize_slug
      3) app.cli.seed_data._fallback_normalize_slug
    If none are available, skip the tests.
    """
    # 1) Try DTO static/cls method
    try:
        org_mod = importlib.import_module("app.schemas.system.organisations")
        normaliser = getattr(org_mod, "OrganisationCreate", None)
        if normaliser is not None:
            func = getattr(normaliser, "normalize_slug", None)
            if callable(func):
                return func  # type: ignore[return-value]
    except Exception:
        pass

    # 2) Try seed fallback in app.db.seed
    try:
        seed_mod = importlib.import_module("app.db.seed")
        func = getattr(seed_mod, "_fallback_normalize_slug", None)
        if callable(func):
            return func  # type: ignore[return-value]
    except Exception:
        pass

    # 3) Try CLI fallback in app.cli.seed_data
    try:
        cli_mod = importlib.import_module("app.cli.seed_data")
        func = getattr(cli_mod, "_fallback_normalize_slug", None)
        if callable(func):
            return func  # type: ignore[return-value]
    except Exception:
        pass

    pytest.skip("No slug normalizer available to test.")
    raise AssertionError("unreachable")


@pytest.mark.parametrize(
    ("input_name", "expected"),
    [
        ("Demo Org", "demo-org"),
        ("  ACME   Inc  ", "acme-inc"),
        ("A--B__C", "a-b-c"),
        ("Foo   Bar!!!   Baz", "foo-bar-baz"),
        ("", "org"),  # empty → default
        ("!!!", "org"),  # only punctuation → default
    ],
)
def test_slug_normalizer_basic_cases(input_name: str, expected: str) -> None:
    normalize = _load_slug_normalizer()
    assert normalize(input_name) == expected
