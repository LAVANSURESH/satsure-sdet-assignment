"""Task 5c — validate the IETF BCP 47 locale format.

Locale cases are data-driven from data/api_test_data.json.
"""
import pytest

from tests.api.tests.schema import TEST_DATA, bcp47_region, is_bcp47

pytestmark = pytest.mark.api

DEFAULT_LOCALE = TEST_DATA["default_locale"]
LOCALE_CASES = TEST_DATA["locale_cases"]


def test_locale_is_well_formed_bcp47(submitted):
    assert is_bcp47(submitted()["locale"])


def test_locale_carries_a_region_for_this_environment(submitted):
    # Test environment is English + India -> a region subtag is expected (en-IN).
    assert bcp47_region(submitted(locale=DEFAULT_LOCALE)["locale"]) == "IN"


@pytest.mark.parametrize(
    "case",
    LOCALE_CASES,
    ids=[c["tag"] or "<empty>" for c in LOCALE_CASES],
)
def test_bcp47_validator_behaviour(case):
    assert is_bcp47(case["tag"]) is case["well_formed"]
