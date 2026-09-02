"""FR-05 data contract — schema/data loading and format validators.

Not a test module (no ``test_`` prefix); imported by the API test files.
The schema and test data live as JSON under ``data/``.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"


def _load_json(name: str) -> dict:
    with open(_DATA_DIR / name, encoding="utf-8") as handle:
        return json.load(handle)


# FR-05 response schema. `additionalProperties: false` + a full `required` list
# makes it strict: a missing field or an unexpected extra field both fail.
FR05_SCHEMA: dict = _load_json("fr05_schema.json")

# Payloads, expected values and negative-case inputs.
TEST_DATA: dict = _load_json("api_test_data.json")

CONTRACT_FIELDS = set(FR05_SCHEMA["required"])


# --------------------------------------------------------------------------
# IETF BCP 47
# --------------------------------------------------------------------------
# language (2-3 alpha) + optional script (4 alpha) + optional region
# (2 alpha | 3 digit) + optional variants. Covers en, en-IN, hi-IN, en-Latn-IN.
_BCP47 = re.compile(
    r"^[A-Za-z]{2,3}"
    r"(-[A-Za-z]{4})?"
    r"(-([A-Za-z]{2}|\d{3}))?"
    r"(-([A-Za-z0-9]{5,8}|\d[A-Za-z0-9]{3}))*$"
)


def is_bcp47(tag: str) -> bool:
    """True if `tag` is a well-formed BCP 47 language tag."""
    return bool(_BCP47.match(tag or ""))


def bcp47_region(tag: str) -> str | None:
    """The region subtag (upper-case) if present, else None."""
    for part in (tag or "").split("-")[1:]:
        if re.fullmatch(r"[A-Za-z]{2}|\d{3}", part):
            return part.upper()
    return None


# --------------------------------------------------------------------------
# Timestamps & suggestion_list
# --------------------------------------------------------------------------
def parse_timestamp(value: str) -> datetime:
    """Parse an ISO-8601 timestamp; raises ValueError if malformed."""
    return datetime.fromisoformat(value)


def parse_suggestion_list(value: str) -> list[str]:
    """Split the comma-separated suggestion_list into trimmed entries."""
    if not value:
        return []
    return [part.strip() for part in value.split(",")]
