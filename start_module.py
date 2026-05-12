"""Entry-point script for OneVizion integration modules.

Execution flow
--------------
1. Install any missing Python dependencies listed in ``pyproject.toml``
   (via ``uv pip install``).  If new packages are installed the process exits
   immediately so that the freshly installed code is picked up on the next
   scheduled launch.
2. Load and validate ``settings.json`` against ``settings_schema.json``.
3. Load runtime parameters from ``ihub_parameters.json`` (injected by the
   OneVizion iHub platform at execution time).
4. Construct an ``IntegrationLog`` and delegate to ``Module.start()``.
5. Any unhandled exception from ``Module.start()`` is logged to the platform
   and re-raised so the iHub process exits with a non-zero return code.

Usage::

    python start_module.py
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate
from onevizion import IntegrationLog, LogLevel

from module import Module

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
# A basic StreamHandler is sufficient here; the OneVizion platform captures
# stdout/stderr.  The level can be overridden via the LOG_LEVEL env variable
# if needed.
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
SETTINGS_FILE = _HERE / "settings.json"
SETTINGS_SCHEMA_FILE = _HERE / "settings_schema.json"
IHUB_PARAMETERS_FILE = _HERE / "ihub_parameters.json"


# ---------------------------------------------------------------------------
# Dependency management
# ---------------------------------------------------------------------------


def install_dependencies() -> None:
    """Install project dependencies using ``uv pip install`` with fallback to ``pip``.

    Installs packages declared in ``pyproject.toml`` (the ``[project]
    dependencies`` table).  If any new packages are installed the process
    exits with code ``0`` so that the next scheduled run picks up the freshly
    installed libraries.

    Tries ``uv`` first (modern, faster), falls back to ``pip`` if ``uv`` is not
    available (for older iHub environments).

    Raises:
        subprocess.CalledProcessError: If the installation command returns a
            non-zero exit code (package resolution or network failure).
    """
    # Try uv first (modern, faster)
    try:
        logger.info("Checking / installing dependencies via uv...")
        result = subprocess.run(
            ["uv", "pip", "install", "-e", ".", "--quiet"],
            capture_output=True,
            text=True,
            check=True,
            cwd=_HERE,
        )
        output = result.stdout.strip()
        if output:
            logger.debug("uv output: %s", output)

        # uv emits "Installed N packages" when it actually installs something
        if "Installed" in output:
            logger.warning(
                "New packages were installed: %s. "
                "Terminating so that the next scheduled launch uses them.",
                output,
            )
            sys.exit(0)

        logger.info("All dependencies satisfied.")
        return

    except FileNotFoundError:
        # uv not available - fall back to pip
        logger.info("uv not found, falling back to pip...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"],
            capture_output=True,
            text=True,
            check=True,
            cwd=_HERE,
        )
        output = result.stdout + result.stderr
        if output:
            logger.debug("pip output: %s", output.strip())

        # pip emits "Successfully installed" when packages are installed
        if "Successfully installed" in output:
            logger.warning(
                "New packages were installed via pip. "
                "Terminating so that the next scheduled launch uses them."
            )
            sys.exit(0)

        logger.info("All dependencies satisfied.")


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------


def load_json_file(path: Path) -> Any:
    """Read and decode a JSON file.

    Args:
        path: Absolute or relative path to the JSON file.

    Returns:
        The decoded Python object (usually a ``dict``).

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    logger.debug("Loading JSON from %s", path)
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_settings(settings_data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate ``settings_data`` against a JSON Schema.

    Args:
        settings_data: The settings dictionary loaded from ``settings.json``.
        schema: The JSON Schema dictionary loaded from ``settings_schema.json``.

    Raises:
        ValueError: If validation fails, wrapping the original
            ``jsonschema.ValidationError`` with a clear message.
    """
    try:
        validate(instance=settings_data, schema=schema)
    except ValidationError as exception:
        raise ValueError(f"Incorrect value in the settings file\n{exception}") from exception


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the full module execution lifecycle.

    This function is called at module import time (i.e. when the script is
    executed directly).  It is extracted into a named function to facilitate
    unit testing of each individual step.
    """
    install_dependencies()

    logger.info("Loading settings from %s", SETTINGS_FILE)
    settings_data: dict[str, Any] = load_json_file(SETTINGS_FILE)

    logger.info("Loading settings schema from %s", SETTINGS_SCHEMA_FILE)
    data_schema: dict[str, Any] = load_json_file(SETTINGS_SCHEMA_FILE)

    validate_settings(settings_data, data_schema)
    logger.info("Settings validated successfully.")

    logger.info("Loading iHub runtime parameters from %s", IHUB_PARAMETERS_FILE)
    module_run_data: dict[str, Any] = load_json_file(IHUB_PARAMETERS_FILE)

    module_log = IntegrationLog(
        module_run_data["processId"],
        settings_data["ovUrl"],
        settings_data["ovAccessKey"],
        settings_data["ovSecretKey"],
        None,
        True,
        module_run_data["logLevel"],
    )

    module = Module(module_log, settings_data)
    logger.info("Starting module execution.")

    try:
        module.start()
    except Exception as exc:
        logger.exception("Module raised an unhandled exception")
        module_log.add(LogLevel.ERROR, str(exc))
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
