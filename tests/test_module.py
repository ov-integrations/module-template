"""Unit tests for :py:mod:`module`.

Tests cover:
- Module initialisation and state storage
- ``Module.start()`` emitting the expected log entry
- Robustness when settings contain extra keys
- Correct delegation to the OneVizion ``LogLevel.INFO`` log level
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call

import pytest
from onevizion import LogLevel

from module import Module

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_module(
    mock_log: MagicMock,
    settings: dict[str, Any] | None = None,
) -> Module:
    """Construct a :py:class:`Module` with the given log mock and settings.

    Args:
        mock_log: A mock standing in for ``IntegrationLog``.
        settings: Optional settings dict; defaults to a minimal valid set.

    Returns:
        A freshly constructed :py:class:`Module` instance.
    """
    if settings is None:
        settings = {
            "ovUrl": "https://example.onevizion.com",
            "ovAccessKey": "A" * 20,
            "ovSecretKey": "S" * 70,
        }
    return Module(mock_log, settings)


# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------


class TestModuleInit:
    """Tests for Module.__init__."""

    def test_stores_log_reference(self, mock_integration_log: MagicMock) -> None:
        """The log object should be accessible via the private attribute."""
        module = make_module(mock_integration_log)
        assert module._module_log is mock_integration_log

    def test_stores_settings_reference(self, mock_integration_log: MagicMock) -> None:
        """Settings should be stored and retrievable."""
        settings: dict[str, Any] = {"key": "value"}
        module = Module(mock_integration_log, settings)
        assert module._settings is settings

    def test_accepts_empty_settings(self, mock_integration_log: MagicMock) -> None:
        """Module must accept an empty settings dict without raising."""
        module = Module(mock_integration_log, {})
        assert module._settings == {}

    def test_accepts_extra_settings_keys(self, mock_integration_log: MagicMock) -> None:
        """Extra keys in settings must not cause an error at construction time."""
        settings: dict[str, Any] = {
            "ovUrl": "https://example.onevizion.com",
            "custom_key": "custom_value",
            "numeric": 42,
        }
        module = make_module(mock_integration_log, settings)
        assert module._settings["custom_key"] == "custom_value"


# ---------------------------------------------------------------------------
# start() tests
# ---------------------------------------------------------------------------


class TestModuleStart:
    """Tests for Module.start()."""

    @pytest.mark.unit()
    def test_start_logs_info_message(self, mock_integration_log: MagicMock) -> None:
        """``start()`` must call ``add(LogLevel.INFO, 'Module is started')``."""
        module = make_module(mock_integration_log)
        module.start()
        mock_integration_log.add.assert_called_once_with(LogLevel.INFO, "Module is started")

    @pytest.mark.unit()
    def test_start_returns_none(self, mock_integration_log: MagicMock) -> None:
        """``start()`` should return ``None`` (implicit)."""
        module = make_module(mock_integration_log)
        result = module.start()
        assert result is None

    @pytest.mark.unit()
    def test_start_can_be_called_multiple_times(self, mock_integration_log: MagicMock) -> None:
        """``start()`` may be called more than once without error."""
        module = make_module(mock_integration_log)
        module.start()
        module.start()
        assert mock_integration_log.add.call_count == 2
        expected = call(LogLevel.INFO, "Module is started")
        mock_integration_log.add.assert_has_calls([expected, expected])

    @pytest.mark.unit()
    def test_start_does_not_call_log_error(self, mock_integration_log: MagicMock) -> None:
        """``start()`` must not log any ERROR-level messages on the happy path."""
        module = make_module(mock_integration_log)
        module.start()
        for call_args in mock_integration_log.add.call_args_list:
            level = call_args.args[0] if call_args.args else call_args.kwargs.get("log_level")
            assert level != LogLevel.ERROR, "Unexpected ERROR log in start()"

    @pytest.mark.unit()
    def test_start_does_not_mutate_settings(self, mock_integration_log: MagicMock) -> None:
        """``start()`` must not modify the settings dictionary."""
        settings: dict[str, Any] = {
            "ovUrl": "https://example.onevizion.com",
            "ovAccessKey": "A" * 20,
            "ovSecretKey": "S" * 70,
        }
        original_settings = dict(settings)
        module = Module(mock_integration_log, settings)
        module.start()
        assert module._settings == original_settings
