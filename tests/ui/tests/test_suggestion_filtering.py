"""Task 4 — Suggestion Filtering: suggestions appear / disappear as text is typed.

Filter cases are data-driven from config/test_data.json.
"""
import pytest
from playwright.sync_api import expect

from tests.ui.config.loader import TEST_DATA

pytestmark = pytest.mark.ui

ALL = TEST_DATA["suggestions"]
TRIGGER = TEST_DATA["inputs"]["trigger"]
PREFIX_CASES = TEST_DATA["filtering"]["prefix"]
ANYWHERE_CASES = TEST_DATA["filtering"]["anywhere"]


def test_suggestion_list_hidden_before_typing(form_page):
    expect(form_page.suggestion_list).to_be_hidden()
    assert form_page.visible_suggestions() == []


def test_typing_a_matching_prefix_opens_the_list(form_page):
    form_page.type_text(TRIGGER)
    expect(form_page.suggestion_list).to_be_visible()
    assert form_page.visible_suggestions() == ALL


def test_clearing_the_text_hides_the_list_again(form_page):
    form_page.type_text(TRIGGER)
    expect(form_page.suggestion_list).to_be_visible()

    form_page.enter_text("")
    expect(form_page.suggestion_list).to_be_hidden()

    form_page.type_text(TRIGGER)  # typing re-opens it
    assert form_page.visible_suggestions() == ALL


# --- Prefix match — FR-02 (default) ---------------------------------------
@pytest.mark.parametrize("case", PREFIX_CASES, ids=[c["input"] for c in PREFIX_CASES])
def test_prefix_filtering(form_page, case):
    form_page.type_text(case["input"])
    assert form_page.visible_suggestions() == case["visible"]
    if not case["visible"]:
        expect(form_page.suggestion_list).to_be_hidden()


# --- Match anywhere — FR-03 (enabled via backend configuration) ----------
@pytest.mark.parametrize("case", ANYWHERE_CASES, ids=[c["input"] for c in ANYWHERE_CASES])
def test_match_anywhere_filtering(api, open_form, case):
    api.set_config(filter_mode="anywhere")
    form = open_form()
    form.type_text(case["input"])
    assert form.visible_suggestions() == case["visible"]
