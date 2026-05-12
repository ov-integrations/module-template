"""Entry-point script for OneVizion integration modules.

Execution flow
--------------
1. Sync dependencies using ``uv sync`` (creates .venv and installs packages)
2. Load and validate ``settings.json`` against ``settings_schema.json``
3. Load runtime parameters from ``ihub_parameters.json``
4. Construct an ``IntegrationLog`` and delegate to ``Module.start()``
5. Any unhandled exception is logged and re-raised

Usage::

    # First time setup:
    uv sync

    # Then run:
    .venv/bin/python start_module.py
    # OR
    source .venv/bin/activate && python start_module.py
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# Note: jsonschema, onevizion, and module imports are inside functions
# to avoid ImportError before dependencies are installed

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
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
# Virtual environment bootstrap
# ---------------------------------------------------------------------------


def ensure_venv() -> None:
    """Ensure we're running in a venv, creating and re-execing if needed."""
    import os
    import shutil

    # Check if already in a venv
    in_venv = sys.prefix != sys.base_prefix

    if in_venv:
        logger.debug("Running in virtual environment: %s", sys.prefix)
        return  # Already in venv, continue

    # Not in venv - check if .venv exists, create if needed, then re-exec
    venv_dir = _HERE / ".venv"
    venv_python = venv_dir / "bin" / "python"

    if not venv_python.exists():
        logger.info("Creating virtual environment at %s", venv_dir)

        # Create venv using uv if available
        if shutil.which("uv"):
            logger.info("Creating venv with uv...")
            subprocess.run(
                ["uv", "venv", str(venv_dir)],
                check=True,
                capture_output=True,
            )
        else:
            logger.info("Creating venv with python -m venv...")
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)],
                check=True,
            )

        logger.info("✅ Created virtual environment")

    # Re-exec using venv's Python
    logger.info("Re-executing with venv Python...")
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)


# ---------------------------------------------------------------------------
# Dependency management
# ---------------------------------------------------------------------------


def install_dependencies() -> None:
    """Sync dependencies using ``uv sync`` or fallback to ``pip``.

    Uses ``uv sync`` to ensure the virtual environment and all dependencies
    are up to date. If new packages are installed, exits with code ``0`` so
    the next scheduled run picks up the fresh libraries.

    Falls back to ``pip install`` if ``uv`` is unavailable.

    Raises:
        subprocess.CalledProcessError: If dependency sync/install fails.
    """
    import shutil

    # Try uv sync (handles venv + dependencies)
    if shutil.which("uv"):
        logger.info("Syncing dependencies with uv...")
        try:
            result = subprocess.run(
                ["uv", "sync"],
                capture_output=True,
                text=True,
                check=True,
                cwd=_HERE,
            )
            output = result.stdout + result.stderr

            # Check if anything was installed/updated
            if "Installed" in output or "Updated" in output:
                logger.warning(
                    "Dependencies were updated. "
                    "Terminating so the next scheduled launch uses them."
                )
                sys.exit(0)

            logger.info("All dependencies up to date.")
            return

        except subprocess.CalledProcessError as e:
            logger.warning(f"uv sync failed: {e.stderr}")
            logger.info("Falling back to pip...")

    # Fallback to pip
    logger.info("Using pip for dependency installation...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        capture_output=True,
        text=True,
        check=True,
        cwd=_HERE,
    )
    output = result.stdout + result.stderr

    if "Successfully installed" in output:
        logger.warning(
            "New packages were installed via pip. "
            "Terminating so the next scheduled launch uses them."
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
        The decoded JSON content as a Python dict, list, or scalar.
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
    from jsonschema import ValidationError, validate

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
    # Ensure we're in a venv (creates and re-execs if needed)
    ensure_venv()

    # Install/sync dependencies (now running in venv)
    install_dependencies()

    # Import after dependencies are installed
    from module import Module
    from onevizion import IntegrationLog, LogLevel

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
