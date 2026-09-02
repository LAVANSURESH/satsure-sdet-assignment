"""Browser / environment configuration for the UI suite.

All values can be overridden with environment variables so the same scripts can
run against the local fixture (default) or a deployed instance.
"""
from __future__ import annotations

import os

from tests.ui.config.loader import LOCATORS, TEST_DATA

# Path of the Autocomplete form relative to the server root.
FORM_PATH = os.environ.get("UI_FORM_PATH", "/autocomplete-form")

# Optional explicit base URL. When unset, tests use the `live_server` fixture,
# which boots the bundled fixture server (fixture/server.py).
BASE_URL: str | None = os.environ.get("UI_BASE_URL")

# Default per-action timeout in milliseconds.
DEFAULT_TIMEOUT_MS = int(os.environ.get("UI_TIMEOUT_MS", "5000"))

# Externalised data (see config/locators.json, config/test_data.json).
FORM_LOCATORS = LOCATORS["autocomplete_form"]
SUGGESTIONS = TEST_DATA["suggestions"]
