"""Task 4 — Keyboard Interaction: Enter submits, Escape clears/closes."""
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.ui


def test_enter_key_submits_the_form(form_page, api):
    form_page.type_text("agile methodology")
    form_page.submit_with_enter()

    expect(form_page.success_container).to_be_visible()
    expect(form_page.error_message).to_be_hidden()

    status, body = api.latest()
    assert status == 200
    assert body["text"] == "agile methodology"


def test_escape_clears_the_input(form_page):
    form_page.type_text("agile methodology process")
    expect(form_page.input).to_have_value("agile methodology process")

    form_page.press_escape()
    expect(form_page.input).to_have_value("")


def test_escape_closes_the_suggestion_list(form_page):
    form_page.type_text("agile")
    expect(form_page.suggestion_list).to_be_visible()

    form_page.press_escape()
    expect(form_page.suggestion_list).to_be_hidden()


def test_enter_on_a_focused_suggestion_selects_it(form_page):
    form_page.type_text("agile")
    form_page.focus_suggestion(1)
    form_page.page.keyboard.press("Enter")

    expect(form_page.input).to_have_value("agile methodology process")
