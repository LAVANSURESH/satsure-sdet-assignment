"""Fixtures for the UI suite.

`live_server` and the per-test `_reset_server` autouse fixture come from the
repo-root conftest.py.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest
import requests

from tests.ui.pages.autocomplete_page import AutocompletePage


@dataclass
class ApiClient:
    """Thin helper for the fixture's test-control and read-back endpoints."""

    base_url: str

    def set_config(self, **kwargs) -> dict:
        resp = requests.post(f"{self.base_url}/api/config", json=kwargs, timeout=3)
        resp.raise_for_status()
        return resp.json()

    def latest(self) -> tuple[int, dict | None]:
        resp = requests.get(f"{self.base_url}/api/response/latest", timeout=3)
        return resp.status_code, (resp.json() if resp.content else None)


@pytest.fixture
def api(live_server: str) -> ApiClient:
    return ApiClient(live_server)


@pytest.fixture
def open_form(page, live_server: str):
    """Factory that opens the form. Call it *after* any `api.set_config(...)`,
    because the client reads its filter mode when the page loads."""

    def _open() -> AutocompletePage:
        return AutocompletePage(page, live_server).open()

    return _open


@pytest.fixture
def form_page(open_form) -> AutocompletePage:
    """The form opened with default configuration (prefix filtering, free text)."""
    return open_form()
