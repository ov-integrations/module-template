"""Pytest fixtures and shared test configuration.

All fixtures defined here are automatically available to every test in the
``tests/`` package without needing explicit imports.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo_root() -> Path:
    """Return the repository root directory (parent of ``tests/``)."""
    return Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Settings fixtures
# ---------------------------------------------------------------------------

VALID_SETTINGS: dict[str, Any] = {
    "ovUrl": "https://example.onevizion.com",
    "ovAccessKey": "A" * 20,
    "ovSecretKey": "S" * 70,
}

VALID_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "ovUrl": {
            "type": "string",
            "pattern": "^https://.*",
        },
        "ovAccessKey": {
            "type": "string",
            "minLength": 20,
            "maxLength": 20,
        },
        "ovSecretKey": {
            "type": "string",
            "minLength": 70,
            "maxLength": 70,
        },
    },
    "required": ["ovUrl", "ovAccessKey", "ovSecretKey"],
}

VALID_IHUB_PARAMS: dict[str, Any] = {
    "processId": 42,
    "logLevel": "INFO",
}


@pytest.fixture()
def valid_settings() -> dict[str, Any]:
    """Return a copy of valid ``settings.json`` data."""
    return dict(VALID_SETTINGS)


@pytest.fixture()
def valid_schema() -> dict[str, Any]:
    """Return a copy of the valid JSON Schema used to validate settings."""
    return dict(VALID_SCHEMA)


@pytest.fixture()
def valid_ihub_params() -> dict[str, Any]:
    """Return a copy of valid ``ihub_parameters.json`` data."""
    return dict(VALID_IHUB_PARAMS)


# ---------------------------------------------------------------------------
# Filesystem fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_settings_dir(
    tmp_path: Path,
    valid_settings: dict[str, Any],
    valid_schema: dict[str, Any],
    valid_ihub_params: dict[str, Any],
) -> Path:
    """Create a temporary directory pre-populated with all required JSON files.

    Returns:
        The temporary directory path containing ``settings.json``,
        ``settings_schema.json``, and ``ihub_parameters.json``.
    """
    (tmp_path / "settings.json").write_text(json.dumps(valid_settings), encoding="utf-8")
    (tmp_path / "settings_schema.json").write_text(json.dumps(valid_schema), encoding="utf-8")
    (tmp_path / "ihub_parameters.json").write_text(json.dumps(valid_ihub_params), encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# OneVizion mock fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_integration_log() -> MagicMock:
    """Return a ``MagicMock`` that stands in for ``IntegrationLog``.

    The mock accepts any attribute access and records all calls, which lets
    tests assert that specific log entries were written without requiring a
    live OneVizion instance.
    """
    return MagicMock(name="IntegrationLog")
