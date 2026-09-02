"""Page Object for the Autocomplete form (fixture/index.html)."""
from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from tests.ui.config import settings
from tests.ui.pages.base_page import BasePage


class AutocompletePage(BasePage):
    path = settings.FORM_PATH

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        # --- locators (externalised in config/locators.json) ---------------
        loc = settings.FORM_LOCATORS
        self.title = page.locator(loc["title"])
        self.input = page.locator(loc["input"])
        self.suggestion_list = page.locator(loc["suggestion_list"])
        self.suggestions = page.locator(loc["suggestion_items"])
        self.next_button = page.locator(loc["next_button"])
        self.error_message = page.locator(loc["error_message"])
        self.success_container = page.locator(loc["success_container"])

    # --- navigation -----------------------------------------------------
    def open(self) -> "AutocompletePage":
        super().open()
        expect(self.input).to_be_visible()
        return self

    # --- input --------------------------------------------------------
    def enter_text(self, text: str) -> "AutocompletePage":
        """Set the field value in one shot (fires a single input event)."""
        self.input.fill(text)
        return self

    def type_text(self, text: str) -> "AutocompletePage":
        """Type key-by-key, as a user would (one input event per character)."""
        self.input.click()
        self.input.fill("")
        self.input.press_sequentially(text, delay=10)
        return self

    def press_key(self, key: str) -> "AutocompletePage":
        self.input.press(key)
        return self

    def press_escape(self) -> "AutocompletePage":
        self.input.press("Escape")
        return self

    # --- suggestions ------------------------------------------------
    def suggestion(self, text: str) -> Locator:
        return self.suggestions.get_by_text(text, exact=True)

    def click_suggestion(self, text: str) -> "AutocompletePage":
        self.suggestion(text).click()
        return self

    def focus_suggestion(self, index: int) -> "AutocompletePage":
        self.suggestions.nth(index).focus()
        return self

    def visible_suggestions(self) -> list[str]:
        return [
            self.suggestions.nth(i).inner_text().strip()
            for i in range(self.suggestions.count())
            if self.suggestions.nth(i).is_visible()
        ]

    # --- submission ------------------------------------------------
    def submit(self) -> "AutocompletePage":
        self.next_button.click()
        return self

    def submit_with_enter(self) -> "AutocompletePage":
        self.input.press("Enter")
        return self

    # --- reads --------------------------------------------------
    def value(self) -> str:
        return self.input.input_value()

    def tab(self, times: int = 1) -> None:
        for _ in range(times):
            self.page.keyboard.press("Tab")

    def shift_tab(self, times: int = 1) -> None:
        for _ in range(times):
            self.page.keyboard.press("Shift+Tab")
