"""Fixtures for the API suite.

`live_server` and the per-test `_reset_server` autouse fixture come from the
repo-root conftest.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pytest
import requests

from tests.api.tests.schema import TEST_DATA

SUGGESTIONS = TEST_DATA["suggestions"]
DEFAULT_LOCALE = TEST_DATA["default_locale"]


def iso_local(dt: datetime | None = None) -> str:
    """ISO-8601 timestamp with the local UTC offset, seconds precision."""
    dt = (dt or datetime.now().astimezone()).replace(microsecond=0)
    return dt.isoformat()


@dataclass
class ApiClient:
    base_url: str

    # --- test-control endpoints -------------------------------------------
    def set_config(self, **kwargs) -> dict:
        resp = requests.post(f"{self.base_url}/api/config", json=kwargs, timeout=3)
        resp.raise_for_status()
        return resp.json()

    def reset(self) -> None:
        requests.post(f"{self.base_url}/api/reset", timeout=3)

    # --- the contract under test --------------------------------------
    def submit(
        self,
        text: str,
        *,
        locale: str = DEFAULT_LOCALE,
        start_date: str | None = None,
        end_date: str | None = None,
        suggestion_list: str = "",
        inject: str | None = None,
        raw_body: dict | None = None,
    ) -> requests.Response:
        body = raw_body if raw_body is not None else {
            "text": text,
            "start_date": start_date or iso_local(),
            "end_date": end_date or iso_local(),
            "locale": locale,
            # the server recomputes this authoritatively; sent only for realism
            "suggestion_list": suggestion_list,
        }
        params = {"inject": inject} if inject else None
        return requests.post(
            f"{self.base_url}/api/response", json=body, params=params, timeout=3
        )

    def get_latest(self, inject: str | None = None) -> requests.Response:
        params = {"inject": inject} if inject else None
        return requests.get(
            f"{self.base_url}/api/response/latest", params=params, timeout=3
        )


@pytest.fixture
def api(live_server: str) -> ApiClient:
    return ApiClient(live_server)


@pytest.fixture
def submitted(api: ApiClient):
    """Perform a successful submission and return the parsed response body."""

    def _do(text: str = "agile methodology", **kwargs) -> dict:
        resp = api.submit(text, **kwargs)
        assert resp.status_code == 200, resp.text
        return resp.json()

    return _do
