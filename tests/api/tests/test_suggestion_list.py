"""Task 5d — suggestion_list contains only matching suggestions, not all of them.

Match cases are data-driven from data/api_test_data.json.
"""
import pytest

from tests.api.tests.schema import TEST_DATA, parse_suggestion_list

pytestmark = pytest.mark.api

SUGGESTIONS = TEST_DATA["suggestions"]
PREFIX_CASES = TEST_DATA["suggestion_list"]["prefix"]
ANYWHERE_CASES = TEST_DATA["suggestion_list"]["anywhere"]


@pytest.mark.parametrize("case", PREFIX_CASES, ids=[c["text"] for c in PREFIX_CASES])
def test_suggestion_list_is_exactly_the_prefix_matches(submitted, case):
    body = submitted(case["text"])
    assert parse_suggestion_list(body["suggestion_list"]) == case["expected"]


def test_specific_input_does_not_return_the_full_list(submitted):
    got = parse_suggestion_list(submitted("agile methodology process testing")["suggestion_list"])
    assert got == ["agile methodology process testing"]
    assert len(got) < len(SUGGESTIONS)


def test_every_returned_entry_is_a_real_suggestion(submitted):
    for entry in parse_suggestion_list(submitted("agile methodology p")["suggestion_list"]):
        assert entry in SUGGESTIONS


def test_suggestion_list_has_no_embedded_control_characters(submitted):
    raw = submitted("agile methodology")["suggestion_list"]
    assert "\n" not in raw and "\r" not in raw  # guards against the DEF-02 defect


@pytest.mark.parametrize("case", ANYWHERE_CASES, ids=[c["text"] for c in ANYWHERE_CASES])
def test_match_anywhere_mode_returns_only_substring_matches(api, submitted, case):
    api.set_config(filter_mode="anywhere")
    got = parse_suggestion_list(submitted(case["text"])["suggestion_list"])
    assert got == case["expected"]
