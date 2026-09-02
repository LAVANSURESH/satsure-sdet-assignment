"""Base page object — behaviour shared by every page in the suite."""
from __future__ import annotations

from playwright.sync_api import Page

from tests.ui.config import settings


class BasePage:
    #: path relative to the base URL; overridden by concrete pages
    path: str = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.page.set_default_timeout(settings.DEFAULT_TIMEOUT_MS)

    def open(self) -> "BasePage":
        self.page.goto(f"{self.base_url}{self.path}")
        return self

    def focused_identifier(self) -> str | None:
        """The focused element's id, or its trimmed text when it has no id."""
        return self.page.evaluate(
            """() => {
                const el = document.activeElement;
                if (!el || el === document.body) return null;
                return el.id || el.textContent.trim();
            }"""
        )
