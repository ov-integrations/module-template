"""Tests for the helper functions defined in :py:mod:`start_module`.

These tests exercise each function in isolation using ``unittest.mock`` to
avoid actual filesystem I/O (where possible) or actual subprocess invocations.

Integration tests that write real files to a ``tmp_path`` directory are
marked with ``@pytest.mark.integration``.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

import start_module
from start_module import install_dependencies, load_json_file, validate_settings

# ---------------------------------------------------------------------------
# load_json_file
# ---------------------------------------------------------------------------


class TestLoadJsonFile:
    """Tests for :py:func:`start_module.load_json_file`."""

    @pytest.mark.integration()
    def test_loads_valid_json(self, tmp_path: Path) -> None:
        """Should return the decoded Python object for a valid JSON file."""
        data = {"key": "value", "number": 42}
        json_file = tmp_path / "data.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")

        result = load_json_file(json_file)
        assert result == data

    @pytest.mark.integration()
    def test_raises_file_not_found(self, tmp_path: Path) -> None:
        """Missing file should raise ``FileNotFoundError``."""
        missing = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            load_json_file(missing)

    @pytest.mark.integration()
    def test_raises_on_invalid_json(self, tmp_path: Path) -> None:
        """Corrupt JSON content should raise ``json.JSONDecodeError``."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ not valid json }", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_json_file(bad_file)

    @pytest.mark.integration()
    def test_handles_nested_objects(self, tmp_path: Path) -> None:
        """Deep JSON structures should be decoded faithfully."""
        data = {"outer": {"inner": [1, 2, 3]}}
        json_file = tmp_path / "nested.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")
        assert load_json_file(json_file) == data

    @pytest.mark.integration()
    def test_handles_utf8_content(self, tmp_path: Path) -> None:
        """Files with multi-byte UTF-8 characters should be read correctly."""
        data = {"name": "cafe\u0301"}  # 'café' with combining accent
        json_file = tmp_path / "utf8.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        assert load_json_file(json_file)["name"] == "cafe\u0301"


# ---------------------------------------------------------------------------
# validate_settings
# ---------------------------------------------------------------------------


class TestValidateSettings:
    """Tests for :py:func:`start_module.validate_settings`."""

    @pytest.mark.unit()
    def test_valid_settings_passes(
        self,
        valid_settings: dict[str, Any],
        valid_schema: dict[str, Any],
    ) -> None:
        """Fully valid settings must not raise any exception."""
        validate_settings(valid_settings, valid_schema)  # no exception

    @pytest.mark.unit()
    def test_missing_required_field_raises(self, valid_schema: dict[str, Any]) -> None:
        """Omitting a required field should raise ``ValueError``."""
        bad_settings: dict[str, Any] = {
            "ovUrl": "https://example.onevizion.com",
            # ovAccessKey missing
            "ovSecretKey": "S" * 70,
        }
        with pytest.raises(ValueError, match="Incorrect value in the settings file"):
            validate_settings(bad_settings, valid_schema)

    @pytest.mark.unit()
    def test_wrong_url_pattern_raises(self, valid_schema: dict[str, Any]) -> None:
        """A URL not starting with 'https://' must fail validation."""
        bad_settings: dict[str, Any] = {
            "ovUrl": "http://example.onevizion.com",  # http, not https
            "ovAccessKey": "A" * 20,
            "ovSecretKey": "S" * 70,
        }
        with pytest.raises(ValueError, match="Incorrect value in the settings file"):
            validate_settings(bad_settings, valid_schema)

    @pytest.mark.unit()
    def test_access_key_too_short_raises(self, valid_schema: dict[str, Any]) -> None:
        """An access key shorter than 20 characters must fail."""
        bad_settings: dict[str, Any] = {
            "ovUrl": "https://example.onevizion.com",
            "ovAccessKey": "SHORT",
            "ovSecretKey": "S" * 70,
        }
        with pytest.raises(ValueError, match="Incorrect value in the settings file"):
            validate_settings(bad_settings, valid_schema)

    @pytest.mark.unit()
    def test_access_key_too_long_raises(self, valid_schema: dict[str, Any]) -> None:
        """An access key longer than 20 characters must fail."""
        bad_settings: dict[str, Any] = {
            "ovUrl": "https://example.onevizion.com",
            "ovAccessKey": "A" * 21,
            "ovSecretKey": "S" * 70,
        }
        with pytest.raises(ValueError, match="Incorrect value in the settings file"):
            validate_settings(bad_settings, valid_schema)

    @pytest.mark.unit()
    def test_secret_key_wrong_length_raises(self, valid_schema: dict[str, Any]) -> None:
        """A secret key of incorrect length must fail."""
        bad_settings: dict[str, Any] = {
            "ovUrl": "https://example.onevizion.com",
            "ovAccessKey": "A" * 20,
            "ovSecretKey": "S" * 69,  # one char too short
        }
        with pytest.raises(ValueError, match="Incorrect value in the settings file"):
            validate_settings(bad_settings, valid_schema)

    @pytest.mark.unit()
    def test_empty_settings_raises(self, valid_schema: dict[str, Any]) -> None:
        """An empty dict must fail because all three fields are required."""
        with pytest.raises(ValueError, match="Incorrect value in the settings file"):
            validate_settings({}, valid_schema)

    @pytest.mark.unit()
    def test_error_message_contains_original_reason(self, valid_schema: dict[str, Any]) -> None:
        """The ValueError message must embed enough context to diagnose the problem."""
        bad_settings: dict[str, Any] = {
            "ovUrl": "https://example.onevizion.com",
            "ovAccessKey": "A" * 20,
            # ovSecretKey missing
        }
        with pytest.raises(ValueError) as exc_info:
            validate_settings(bad_settings, valid_schema)
        # The original ValidationError detail should appear somewhere in the message
        assert "ovSecretKey" in str(exc_info.value) or "required" in str(exc_info.value).lower()

    @pytest.mark.unit()
    def test_raises_value_error_not_validation_error(self, valid_schema: dict[str, Any]) -> None:
        """The raised exception must be ``ValueError``, not a raw ``ValidationError``."""
        with pytest.raises(ValueError):  # not jsonschema.ValidationError
            validate_settings({}, valid_schema)


# ---------------------------------------------------------------------------
# install_dependencies
# ---------------------------------------------------------------------------


class TestInstallDependencies:
    """Tests for :py:func:`start_module.install_dependencies`."""

    @pytest.mark.unit()
    def test_no_new_packages_does_not_exit(self) -> None:
        """When uv reports nothing was installed, the process must continue."""
        completed = MagicMock()
        completed.stdout = ""
        completed.returncode = 0
        with patch("start_module.subprocess.run", return_value=completed) as mock_run:
            install_dependencies()  # should NOT raise SystemExit
            mock_run.assert_called_once()

    @pytest.mark.unit()
    def test_new_packages_trigger_sys_exit(self) -> None:
        """When uv installs new packages, ``sys.exit(0)`` must be raised."""
        completed = MagicMock()
        completed.stdout = "Installed 3 packages in 200ms"
        completed.returncode = 0
        with patch("start_module.subprocess.run", return_value=completed):
            with pytest.raises(SystemExit) as exc_info:
                install_dependencies()
            assert exc_info.value.code == 0

    @pytest.mark.unit()
    def test_subprocess_failure_propagates(self) -> None:
        """A non-zero exit code from uv should propagate as ``CalledProcessError``."""
        with patch(
            "start_module.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "uv"),
        ):
            with pytest.raises(subprocess.CalledProcessError):
                install_dependencies()

    @pytest.mark.unit()
    def test_uv_not_found_raises_file_not_found(self) -> None:
        """Missing ``uv`` binary should raise ``FileNotFoundError``."""
        with patch(
            "start_module.subprocess.run",
            side_effect=FileNotFoundError("uv not found"),
        ):
            with pytest.raises(FileNotFoundError):
                install_dependencies()

    @pytest.mark.unit()
    def test_calls_uv_pip_install(self) -> None:
        """The subprocess call must use ``uv pip install``."""
        completed = MagicMock()
        completed.stdout = ""
        completed.returncode = 0
        with patch("start_module.subprocess.run", return_value=completed) as mock_run:
            install_dependencies()
            args = mock_run.call_args.args[0]
            assert args[0] == "uv"
            assert "pip" in args
            assert "install" in args


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------


class TestMain:
    """End-to-end tests for :py:func:`start_module.main`.

    These tests patch external I/O boundaries (subprocess, IntegrationLog,
    Module) to exercise the orchestration logic without real network or
    filesystem calls beyond the JSON files written in the fixture.
    """

    def _patch_everything(
        self,
        tmp_settings_dir: Path,
        *,
        uv_stdout: str = "",
    ) -> dict[str, Any]:
        """Return a dictionary of context-manager patches for ``main()``."""
        completed = MagicMock()
        completed.stdout = uv_stdout
        completed.returncode = 0

        return {
            "subprocess_run": patch("start_module.subprocess.run", return_value=completed),
            "integration_log_cls": patch("start_module.IntegrationLog"),
            "module_cls": patch("start_module.Module"),
            # Re-point path constants to the tmp directory
            "settings_file": patch.object(
                start_module, "SETTINGS_FILE", tmp_settings_dir / "settings.json"
            ),
            "schema_file": patch.object(
                start_module,
                "SETTINGS_SCHEMA_FILE",
                tmp_settings_dir / "settings_schema.json",
            ),
            "ihub_file": patch.object(
                start_module,
                "IHUB_PARAMETERS_FILE",
                tmp_settings_dir / "ihub_parameters.json",
            ),
        }

    @pytest.mark.integration()
    def test_happy_path_calls_module_start(self, tmp_settings_dir: Path) -> None:
        """On the happy path, ``Module.start()`` must be called exactly once."""
        patches = self._patch_everything(tmp_settings_dir)
        with (
            patches["subprocess_run"],
            patches["settings_file"],
            patches["schema_file"],
            patches["ihub_file"],
            patches["integration_log_cls"] as mock_log_cls,
            patches["module_cls"] as mock_module_cls,
        ):
            mock_module_instance = MagicMock()
            mock_module_cls.return_value = mock_module_instance

            start_module.main()

            mock_module_instance.start.assert_called_once()
            mock_log_cls.assert_called_once()

    @pytest.mark.integration()
    def test_module_start_exception_logs_and_reraises(self, tmp_settings_dir: Path) -> None:
        """An exception from ``Module.start()`` must be logged then re-raised."""
        patches = self._patch_everything(tmp_settings_dir)
        with (
            patches["subprocess_run"],
            patches["settings_file"],
            patches["schema_file"],
            patches["ihub_file"],
            patches["integration_log_cls"] as mock_log_cls,
            patches["module_cls"] as mock_module_cls,
        ):
            mock_log_instance = MagicMock()
            mock_log_cls.return_value = mock_log_instance
            mock_module_instance = MagicMock()
            mock_module_instance.start.side_effect = RuntimeError("boom")
            mock_module_cls.return_value = mock_module_instance

            with pytest.raises(RuntimeError, match="boom"):
                start_module.main()

            # The error must have been sent to IntegrationLog
            mock_log_instance.add.assert_called()

    @pytest.mark.integration()
    def test_missing_settings_file_raises(self, tmp_path: Path) -> None:
        """A missing ``settings.json`` should raise ``FileNotFoundError``."""
        # Provide schema and ihub params but omit settings.json
        schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        (tmp_path / "settings_schema.json").write_text(json.dumps(schema), encoding="utf-8")
        (tmp_path / "ihub_parameters.json").write_text(
            json.dumps({"processId": 1, "logLevel": "INFO"}), encoding="utf-8"
        )

        completed = MagicMock()
        completed.stdout = ""
        completed.returncode = 0

        with (
            patch("start_module.subprocess.run", return_value=completed),
            patch.object(start_module, "SETTINGS_FILE", tmp_path / "settings.json"),
            patch.object(start_module, "SETTINGS_SCHEMA_FILE", tmp_path / "settings_schema.json"),
            patch.object(start_module, "IHUB_PARAMETERS_FILE", tmp_path / "ihub_parameters.json"),
        ):
            with pytest.raises(FileNotFoundError):
                start_module.main()

    @pytest.mark.integration()
    def test_invalid_settings_raises_value_error(self, tmp_path: Path) -> None:
        """Invalid ``settings.json`` data must surface as a ``ValueError``."""
        bad_settings: dict[str, Any] = {"ovUrl": "http://not-https.com"}
        schema: dict[str, Any] = {
            "type": "object",
            "properties": {"ovUrl": {"type": "string", "pattern": "^https://.*"}},
            "required": ["ovUrl"],
        }
        (tmp_path / "settings.json").write_text(json.dumps(bad_settings), encoding="utf-8")
        (tmp_path / "settings_schema.json").write_text(json.dumps(schema), encoding="utf-8")
        (tmp_path / "ihub_parameters.json").write_text(
            json.dumps({"processId": 1, "logLevel": "INFO"}), encoding="utf-8"
        )

        completed = MagicMock()
        completed.stdout = ""
        completed.returncode = 0

        with (
            patch("start_module.subprocess.run", return_value=completed),
            patch.object(start_module, "SETTINGS_FILE", tmp_path / "settings.json"),
            patch.object(start_module, "SETTINGS_SCHEMA_FILE", tmp_path / "settings_schema.json"),
            patch.object(start_module, "IHUB_PARAMETERS_FILE", tmp_path / "ihub_parameters.json"),
        ):
            with pytest.raises(ValueError, match="Incorrect value in the settings file"):
                start_module.main()
