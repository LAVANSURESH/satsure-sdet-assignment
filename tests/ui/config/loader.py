"""Load externalised locators and test data (JSON) for the UI suite."""
from __future__ import annotations

import json
from pathlib import Path

_CONFIG_DIR = Path(__file__).parent


def read_json(filename: str) -> dict:
    with open(_CONFIG_DIR / filename, encoding="utf-8") as handle:
        return json.load(handle)


LOCATORS: dict = read_json("locators.json")
TEST_DATA: dict = read_json("test_data.json")
