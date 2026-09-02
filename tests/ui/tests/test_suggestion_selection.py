"""Task 4 — Suggestion Selection: clicking a suggestion populates the input."""
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.ui


def test_clicking_a_suggestion_populates_the_input(form_page):
    form_page.type_text("agile")
    form_page.click_suggestion("agile methodology process")
    expect(form_page.input).to_have_value("agile methodology process")


def test_clicking_the_longest_suggestion_populates_the_input(form_page):
    form_page.type_text("agile")
    form_page.click_suggestion("agile methodology process testing")
    expect(form_page.input).to_have_value("agile methodology process testing")


def test_selection_then_submit_persists_the_selected_value(form_page, api):
    form_page.type_text("agile")
    form_page.click_suggestion("agile methodology")
    form_page.submit()

    expect(form_page.success_container).to_be_visible()
    status, body = api.latest()
    assert status == 200
    assert body["text"] == "agile methodology"


def test_selecting_a_suggestion_closes_the_list(form_page):
    form_page.type_text("agile")
    expect(form_page.suggestion_list).to_be_visible()

    form_page.click_suggestion("agile methodology process")
    expect(form_page.input).to_have_value("agile methodology process")
    expect(form_page.suggestion_list).to_be_hidden()  # selection closes it

    form_page.type_text("agile methodology process t")  # typing re-opens it
    assert form_page.visible_suggestions() == ["agile methodology process testing"]
