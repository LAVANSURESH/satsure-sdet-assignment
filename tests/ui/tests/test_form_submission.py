"""Task 4 — Form Submission: success and error message display."""
import pytest
from playwright.sync_api import expect

from tests.ui.config.loader import TEST_DATA

pytestmark = pytest.mark.ui

MSG = TEST_DATA["messages"]
FREE_TEXT = TEST_DATA["inputs"]["free_text"]
NO_MATCH_TEXT = TEST_DATA["inputs"]["no_match_free_text"]
TRIGGER = TEST_DATA["inputs"]["trigger"]
FIRST_SUGGESTION = TEST_DATA["suggestions"][0]


def test_valid_submission_shows_success_message(form_page, api):
    form_page.type_text(FIRST_SUGGESTION)
    form_page.submit()

    expect(form_page.success_container).to_be_visible()
    expect(form_page.success_container).to_contain_text(MSG["success"])
    expect(form_page.error_message).to_be_hidden()

    # Light cross-check only; deep schema/type validation lives in the API suite.
    status, body = api.latest()
    assert status == 200
    assert body["text"] == FIRST_SUGGESTION
    assert body["suggestion_list"]  # matches were recorded


def test_empty_submission_shows_error_and_persists_nothing(form_page, api):
    form_page.submit()  # nothing typed

    expect(form_page.error_message).to_be_visible()
    expect(form_page.error_message).to_contain_text(MSG["error"])
    expect(form_page.success_container).to_be_hidden()

    status, _ = api.latest()
    assert status == 404  # invalid input never reached persistence


def test_free_text_is_accepted_by_default(form_page, api):
    """FR-01 / C-01 default position: any non-empty text is a valid response."""
    form_page.type_text(FREE_TEXT)
    form_page.submit()

    expect(form_page.success_container).to_be_visible()
    status, body = api.latest()
    assert status == 200
    assert body["text"] == FREE_TEXT


def test_error_when_selection_required_and_text_matches_no_suggestion(api, open_form):
    """TC-08: with require_suggestion_selection ON, non-matching free text is rejected."""
    api.set_config(require_suggestion_selection=True)
    form = open_form()

    form.type_text(NO_MATCH_TEXT)
    form.submit()

    expect(form.error_message).to_be_visible()
    expect(form.success_container).to_be_hidden()
    status, _ = api.latest()
    assert status == 404


def test_valid_selection_succeeds_when_selection_required(api, open_form):
    api.set_config(require_suggestion_selection=True)
    form = open_form()

    form.type_text(TRIGGER)
    form.click_suggestion(FIRST_SUGGESTION)
    form.submit()

    expect(form.success_container).to_be_visible()
    status, body = api.latest()
    assert status == 200
    assert body["text"] == FIRST_SUGGESTION
