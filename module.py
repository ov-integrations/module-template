"""Core module logic for OneVizion integration modules.

This file contains the ``Module`` class that encapsulates all business logic
for an integration module.  ``start_module.py`` instantiates this class and
delegates execution to :py:meth:`Module.start`.

When building a real integration, replace the placeholder ``start`` body with
your own implementation.  The constructor signature must remain compatible with
the call in ``start_module.py``::

    module = Module(module_log, settings_data)
    module.start()
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from onevizion import LogLevel

if TYPE_CHECKING:
    from onevizion import IntegrationLog

logger = logging.getLogger(__name__)


class Module:
    """Encapsulates all business logic for a OneVizion integration module.

    Args:
        ov_module_log: The ``IntegrationLog`` instance used to write log entries
            back to the OneVizion platform.
        settings_data: A dictionary of validated settings loaded from
            ``settings.json``.  The schema is enforced in ``start_module.py``
            before this class is constructed.

    Example:
        >>> from unittest.mock import MagicMock
        >>> log = MagicMock()
        >>> module = Module(log, {"ovUrl": "https://example.onevizion.com", ...})
        >>> module.start()
    """

    def __init__(self, ov_module_log: IntegrationLog, settings_data: dict[str, Any]) -> None:
        self._module_log = ov_module_log
        self._settings = settings_data
        logger.debug("Module initialised with settings keys: %s", list(settings_data.keys()))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Execute the module's main integration logic.

        This method is the single entry-point called by ``start_module.py``.
        Any unhandled exception raised here will be caught by the caller,
        logged to the OneVizion platform, and re-raised to terminate the
        process with a non-zero exit code.

        Replace the body of this method with the actual integration logic
        when implementing a concrete module.
        """
        logger.info("Module start() called")
        self._module_log.add(LogLevel.INFO, "Module is started")
