"""Task 4 — Tab Navigation: move between form elements with the Tab key.

The fixture marks each `<li>` suggestion `tabindex="0"` so suggestions are
keyboard-reachable and selectable (an accessibility improvement over the raw HTML
in the brief). Because the suggestion list is hidden until the user types, the
expected Tab order depends on whether the list is open.
"""
import pytest
from playwright.sync_api import expect

from tests.ui.config.loader import TEST_DATA

pytestmark = pytest.mark.ui

TAB_ORDER = TEST_DATA["tab_order"]
TRIGGER = TEST_DATA["inputs"]["trigger"]


def test_tab_on_empty_form_goes_from_input_to_next_button(form_page):
    # list hidden before typing -> focus skips straight to the button
    form_page.input.focus()
    expect(form_page.input).to_be_focused()
    form_page.tab()
    expect(form_page.next_button).to_be_focused()


def test_tab_visits_each_visible_suggestion_in_order(form_page):
    form_page.type_text(TRIGGER)  # opens the list with all three
    expect(form_page.suggestion_list).to_be_visible()

    form_page.input.focus()
    seen = []
    for _ in range(len(TAB_ORDER)):
        form_page.tab()
        seen.append(form_page.focused_identifier())

    assert seen == TAB_ORDER


def test_shift_tab_moves_focus_backwards_through_suggestions(form_page):
    form_page.type_text(TRIGGER)
    form_page.next_button.focus()

    form_page.shift_tab()
    expect(form_page.suggestions.nth(2)).to_be_focused()
    form_page.shift_tab()
    expect(form_page.suggestions.nth(1)).to_be_focused()
