# Autocomplete Form — SDET Practical Assignment

Test analysis, documentation, and automation for the Autocomplete web form described
in the assignment brief.

Because the brief's URL (`https://test.com/autocomplete-form`) is not a real target,
this repo ships a **local fixture** (`fixture/`) that implements the HTML structure and
functional requirements FR-01…FR-05 exactly as specified, plus a mock REST API. All UI
and API tests run against that fixture, so `pytest` is green end-to-end with no external
dependencies.

## Layout

```
README.md
requirements.txt            # dependency file
pytest.ini
conftest.py                 # boots the fixture server for the test session
fixture/                    # local system under test (form + mock API)
docs/
  1-requirement-analysis.md
  2-test-scenarios.md       # Task 1 — top 10 risk-ranked scenarios
  3-defect-identification.md # Task 2 — API response vs FR-05
  4-test-cases.md           # Task 3 — detailed test cases
  7-ai-reflection.md        # Task 6 — AI usage
  8-architecture-discussion.md
tests/
  ui/                       # Task 4 — Playwright, Page Object Model
    pages/                   # base_page.py, autocomplete_page.py
    tests/                   # test scripts + conftest.py
    config/                  # settings.py, loader.py
      locators.json          #   selectors, kept out of the page object
      test_data.json         #   suggestions, messages, tab order, filter datasets
  api/
    tests/                   # Task 5 — API contract + negative tests
      schema.py              #   loads the JSON below + BCP 47 / timestamp validators
      data/
        fr05_schema.json     #   the FR-05 contract as a JSON Schema file
        api_test_data.json   #   payloads, expected values, negative-case inputs
prompts/                    # prompt file(s) used for this assignment
```

### Test data

Locators and test data are externalised as JSON and loaded by thin helpers
(`tests/ui/config/loader.py`, `tests/api/tests/schema.py`):

| File | Holds |
| --- | --- |
| `tests/ui/config/locators.json` | Every selector for the form (CSS; Playwright also accepts XPath through the same `page.locator()` call) |
| `tests/ui/config/test_data.json` | Suggestion list, success/error message text, expected Tab order, prefix/match-anywhere filter datasets, stock inputs |
| `tests/api/tests/data/fr05_schema.json` | FR-05 JSON Schema (`additionalProperties:false`, all fields required) |
| `tests/api/tests/data/api_test_data.json` | Session user, `suggestion_list` prefix/anywhere cases, BCP 47 case table, timestamp fixtures, negative-case inputs |

Filtering, locale, and `suggestion_list` tests are `@pytest.mark.parametrize`d over
these datasets, so adding a case is a JSON edit — no test code changes.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

pytest                      # runs UI + API suites (fixture server auto-starts)
```

Run just one layer:

```bash
pytest -m ui                 # Task 4 — Playwright UI suite
pytest -m api                # Task 5 — API suite
```

Every run writes a self-contained **`report.html`** (pytest-html) at the repo root;
open it in a browser. Failing browser tests embed a screenshot in that report, and a
screenshot + video + Playwright trace are also saved under `test-results/`. Point the
report elsewhere with `pytest --html=path/to/report.html`.

Explore the form by hand:

```bash
python fixture/server.py     # http://127.0.0.1:5057/autocomplete-form
```

## UI suite — Task 4

Playwright driven through `pytest-playwright`, structured with the Page Object Model.

| File | Layer |
| --- | --- |
| `tests/ui/config/settings.py` | Base URL, form path, timeouts, suggestions — all env-overridable |
| `tests/ui/pages/base_page.py` | `BasePage` — navigation + focused-element helper |
| `tests/ui/pages/autocomplete_page.py` | `AutocompletePage` — every locator and action for the form |
| `tests/ui/tests/conftest.py` | `form_page`, `open_form` (factory), `api` (fixture-control) fixtures |
| `tests/ui/tests/test_tab_navigation.py` | **Tab Navigation** — Tab / Shift+Tab order across input → suggestions → Next |
| `tests/ui/tests/test_keyboard_interaction.py` | **Keyboard Interaction** — Enter submits, Escape clears input / closes list |
| `tests/ui/tests/test_suggestion_filtering.py` | **Suggestion Filtering** — list hidden until typing; prefix (FR-02) and match-anywhere (FR-03, config toggle) |
| `tests/ui/tests/test_suggestion_selection.py` | **Suggestion Selection** — click populates the input and closes the list |
| `tests/ui/tests/test_form_submission.py` | **Form Submission** — success vs. error message, empty input, required-selection mode |

Run it:

```bash
pytest -m ui                          # headless Chromium (default)
pytest -m ui --headed --slowmo 300    # watch it drive the browser
pytest -m ui --browser firefox        # also: chromium | webkit
pytest -m ui -k filtering             # a single area
```

On failure, a screenshot, video, and Playwright trace are written to `test-results/`
(open a trace with `playwright show-trace test-results/<...>/trace.zip`).

**Fixture notes:**

- The suggestion list is **hidden until the user types** a matching value, and closes
  again on selection or Escape (the brief is silent on the empty-field state — see
  `docs/1` A-12). Tab order therefore includes the suggestions only while the list is open.
- The `<li>` suggestions are given `tabindex="0"` so they are keyboard-reachable — an
  accessibility improvement over the raw HTML in the brief.
- Submission tests do a *light* read-back against `GET /api/response/latest`; full
  schema/type/negative validation is the API suite's job (Task 5).

## API suite — Task 5

Plain `requests` + `jsonschema`, no browser. Each test submits through the mock REST
API and asserts on the persisted response.

| File | Covers |
| --- | --- |
| `tests/api/tests/schema.py` | FR-05 JSON Schema (`additionalProperties: false`, all fields required) + `is_bcp47` / `bcp47_region` / `parse_timestamp` / `parse_suggestion_list` helpers |
| `tests/api/tests/conftest.py` | `api` client (`submit`, `get_latest`, `set_config`) and `submitted` fixtures |
| `tests/api/tests/test_schema_contract.py` | **(a)** response validates against the FR-05 schema — POST and GET, across several inputs; exact field set |
| `tests/api/tests/test_data_types.py` | **(b)** `completed` is a native `bool` `True`; timestamps parse, are tz-aware, ordered; explicit `+05:30` offset preserved; account fields typed |
| `tests/api/tests/test_locale_format.py` | **(c)** `locale` is well-formed BCP 47 and carries a region for this env; validator truth-table (`en-IN`, `en`, `hi-IN`, `en-Latn-IN` vs. `english`, `en_IN`, …) |
| `tests/api/tests/test_suggestion_list.py` | **(d)** `suggestion_list` is exactly the prefix matches (never the full list for a specific input); every entry is a real suggestion; no embedded newline (DEF-02); match-anywhere mode |
| `tests/api/tests/test_negative.py` | **(e)** 8 negatives: missing field, stringified `completed`, all-suggestions, region-less locale, naive timestamp, empty text (400), free text when selection required (400), empty body (400) |

```bash
pytest -m api            # ~0.5s, no browser
pytest -m api -v
```

## AI transcript

Per the brief, the prompt file(s) live in `prompts/` and the full JSON transcript of the
AI conversation is included with the submission.
