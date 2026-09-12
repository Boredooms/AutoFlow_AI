"""Shared pytest configuration and fixtures."""

from __future__ import annotations

import warnings

import pytest

from autoflow_ai import samples


@pytest.fixture
def registry():
    """One valid instance of every contract, keyed by class name."""

    return samples.build_sample_registry()


@pytest.fixture(autouse=True)
def _fail_on_pydantic_shadow_warning():
    """Turn Pydantic field-shadow warnings into errors during tests.

    A field shadowing a base attribute is a design bug; fail loudly.
    """

    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        yield
