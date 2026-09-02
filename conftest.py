"""Shared pytest fixtures: boots the local fixture server for the whole session."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).parent
SERVER = ROOT / "fixture" / "server.py"
HOST = "127.0.0.1"
PORT = int(os.environ.get("FIXTURE_PORT", "5057"))
BASE = f"http://{HOST}:{PORT}"


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.25)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def live_server() -> str:
    """Base URL of a running fixture server.

    Reuses an already-running instance on PORT; otherwise starts one and
    tears it down at the end of the session.
    """
    started = None
    if not _port_open(HOST, PORT):
        env = {**os.environ, "HOST": HOST, "PORT": str(PORT)}
        started = subprocess.Popen(
            [sys.executable, str(SERVER)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                requests.get(f"{BASE}/api/config", timeout=0.5)
                break
            except requests.RequestException:
                time.sleep(0.2)
        else:
            started.terminate()
            raise RuntimeError("fixture server did not become ready within 15s")

    yield BASE

    if started is not None:
        started.terminate()
        try:
            started.wait(timeout=5)
        except subprocess.TimeoutExpired:
            started.kill()


@pytest.fixture(autouse=True)
def _reset_server(live_server: str):
    """Restore default config and clear stored state before every test."""
    requests.post(f"{live_server}/api/reset", timeout=2)
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Embed a screenshot in the HTML report when a browser test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page = item.funcargs.get("page")
    if page is None:
        return
    try:
        import base64

        from pytest_html import extras as html_extras

        png_b64 = base64.b64encode(page.screenshot(full_page=True)).decode("ascii")
        report.extras = getattr(report, "extras", []) + [html_extras.png(png_b64)]
    except Exception:
        pass  # never let reporting break the run
