# Prompts used with Claude Code

Detailed, chronological log of every instruction, clarification, and debugging
exchange in the session. The complete JSON transcript is submitted alongside this file.

- **Tool:** Claude Code (Anthropic CLI, Claude Sonnet), run in the terminal.
- **Starting point:** working directory contained only `Job Description.pdf` and
  `_Practical Assignment_SDET.pdf`. No git repo, no code.
- **Working method:** after an initial attempt to work autonomously, the user redirected
  to **step-by-step with a review checkpoint after each deliverable**. Every doc and test
  module below was reviewed (and often revised) before moving on.

---

## 1. `explore`

- Read both PDFs.
- Summarised the JD (SDET role; Playwright / Selenium / Cucumber; Python / Java; API,
  data-pipeline and performance testing; CI/CD) and the assignment: the Autocomplete
  form, FR-01…FR-05, the six tasks, and the mandated submission layout (git repo with
  `docs/`, `tests/ui`, `tests/api`, dependency file, **plus the prompt file(s) and the
  full JSON transcript**).
- Flagged that `https://test.com/autocomplete-form` is not a real target, so the
  automation tasks need a local stand-in to be executable.


## 2. `yes` — Step 1: environment + repo skeleton + local fixture

- Created `.venv`; installed `pytest`, `playwright`, `pytest-playwright`, `flask`,
  `requests`, `jsonschema`; ran `playwright install chromium`; verified Chromium launches.
- Built:
  - `.gitignore`, `requirements.txt`, `pytest.ini`, root `conftest.py`
    (session-scoped fixture that boots `fixture/server.py`, autouse per-test reset).
  - `fixture/index.html` — the assignment's HTML verbatim plus an `<h1>` title;
    ids/classes unchanged.
  - `fixture/app.js` — FR-01…FR-05 behaviour: prefix / match-anywhere filtering,
    local-time ISO timestamps, BCP 47 locale, `Next` → `POST /api/response`.
  - `fixture/server.py` — Flask: serves the form + a mock REST API
    (`/api/config`, `/api/reset`, `POST /api/response`, `GET /api/response/latest`),
    with a `?inject=<fault>` hook that returns deliberately broken payloads for
    negative testing.
  - Empty `docs/`, `tests/ui/{pages,tests,config}`, `tests/api/tests`, `prompts/`.
  - `README.md` stub.
- Smoke-tested with `curl` and a headless Playwright script: filtering, Escape-to-clear,
  click-to-select, submit → success, Tab order, `400` on empty submit, `?inject=` all
  confirmed.

## 3. `yes` — Step 2: `docs/1` and `docs/2` (first drafts)

- `docs/1-requirement-analysis.md` — FR-by-FR analysis, the FR-05 field table with
  expected types/formats, an ambiguity list (with proposed resolutions), assumptions,
  test environment, risk areas.
- `docs/2-test-scenarios.md` — a first top-10 risk-ranked list (later replaced — see 5).

## 4. Supplied 9 test scenarios (table) — "change in the doc"

- The user pasted their own **9 scenarios** (Test Scenario | Risk Level | Reason).
- Claude replaced its draft in `docs/2` with the 9 **verbatim**, only:
  - re-ordered them highest → lowest risk (the brief requires that ranking),
  - fixed spelling in the titles (`selction`, `confguration`, `sensitivityof`),
  - rebuilt the scenario → requirement traceability table.
- Flagged: the brief asks for 10; a candidate 10th (keyboard operation) is noted under
  *Beyond this list*.

## 5. Supplied test cases TC-01…TC-10 — `add to doc exactly`

- Written **verbatim** into `docs/4-test-cases.md` (ID / Title / Preconditions /
  numbered Steps / Expected Results / Test Data).
- Claude added only a traceability table and flagged, without changing the text:
  - TC-01 says "all 7 properties" then lists 8;
  - TC-08 expects free text to be rejected — that is the `require_suggestion_selection`
    path, not the FR-01 default;
  - TC-01 / TC-05 describe "known deviations" that belong to the Task 2 sample, not the
    fixture's normal output.

## 6. Supplied defect test cases TC-D01…TC-D09 — `add to doc defect identification exactly`

- Written **verbatim** into `docs/3-defect-identification.md` §3.4.
- Claude authored the rest of the doc around them:
  - §3.1 the response under test (line break in `suggestion_list` preserved, not flattened);
  - §3.2 a field-by-field comparison against FR-05;
  - §3.3 the summary — **DEF-01** `completed` is string `"true"` (High); **DEF-02**
    `suggestion_list` contains an embedded line break (Medium); **OBS-01** bare `locale`
    and **OBS-02** UTC `Z` timestamps as *observations, needs-confirmation*, per the
    user's stated ground truth;
  - §3.5 defect → test-case traceability.

## 7. Supplied contradictions C-01…C-03 and ambiguities A-01…A-13 — `add these to requirement analysis`

- Formatted into clean Contradictions / Ambiguities tables in `docs/1` §1.4, wording unchanged.
- Added §1.4.1 *Interim positions used for test design* (clearly separated) mapping the
  load-bearing IDs to what the fixture/tests assume.
- Reconciled every stale cross-reference elsewhere in `docs/1` (FR-01, FR-02, FR-04, the
  FR-05 table, §1.7) from the old A1–A12 numbering to the new C-/A- IDs; softened the
  `locale` and timestamp notes so they agree with `docs/3`.

## 8. Task 4 requirements (pasted from the brief) + `lets work on it ask the questions before starting`

- **Clarifying questions asked and answers:**

  | Question | Chosen |
  | --- | --- |
  | How to trigger the error-message path | **Both** — an empty-input test *and* a `require_suggestion_selection = ON` test (TC-08) |
  | Should UI submission tests cross-check the API | **Light read-back** only (`GET /api/response/latest`); deep validation stays in Task 5 |
  | Which filter modes to cover in the UI | **Both** prefix (FR-02) and match-anywhere (FR-03) |

- Built the Page Object Model suite:
  - `tests/ui/config/settings.py`, `tests/ui/pages/base_page.py`,
    `tests/ui/pages/autocomplete_page.py`, `tests/ui/tests/conftest.py`
    (`form_page`, `open_form` factory, `api` fixture-control).
  - `test_tab_navigation.py`, `test_keyboard_interaction.py`,
    `test_suggestion_filtering.py`, `test_suggestion_selection.py`,
    `test_form_submission.py`.
  - `pytest.ini` gains screenshot / video / trace on failure.
- Result: **24 UI tests green**. README got a Task 4 section.


## 9. `yes go for B`

- Switched the fixture to **hidden-until-typing**: added a `listSuppressed` flag in
  `app.js` (set on load / Escape / selection, cleared on the first keystroke;
  `applyFilter()` hides the list while it's set or the field is empty).
- Rewrote `test_tab_navigation.py` (tab order now depends on whether the list is open)
  and `test_suggestion_filtering.py`; edited `test_suggestion_selection.py`
  (selecting a suggestion closes the list).
- Updated `docs/1` (system overview, FR-02, new **A-12** note) and the README.
- Result: **25 UI tests green**.

## 10. Task 5 requirements (pasted from the brief) + `lets do next one`

- Built the API suite (no browser — `requests` + `jsonschema`):
  - `tests/api/tests/schema.py` — the FR-05 JSON Schema (strict: all fields required,
    `additionalProperties:false`, `completed` must be boolean) + `is_bcp47`,
    `bcp47_region`, `parse_timestamp`, `parse_suggestion_list`.
  - `conftest.py` — `ApiClient` (`submit`, `get_latest`, `set_config`) and `submitted`.
  - `test_schema_contract.py` (a), `test_data_types.py` (b), `test_locale_format.py` (c),
    `test_suggestion_list.py` (d), `test_negative.py` (e — 8 negatives: missing field,
    stringified `completed`, all-suggestions, region-less locale, naive timestamp,
    empty text, free text when a selection is required, empty body).
- Result: **39 API tests green; 64 total**. README got a Task 5 section.

## 11. `go ahead` — remaining docs

- `docs/7-ai-reflection.md` (Task 6), `docs/8-architecture-discussion.md`, and the first
  version of this prompt log. `.gitkeep` files removed. 64 green.

## 12. `setup the pytest-html`

- Installed `pytest-html==4.2.0`; added it to `requirements.txt`; added
  `--html=report.html --self-contained-html` to `pytest.ini`.
- Added a `pytest_runtest_makereport` hook in the root `conftest.py` that embeds a
  screenshot into the HTML report when a browser test fails (wrapped so it can never
  break a run).
- Ignored `report.html` / `assets/`; documented in the README.
- Verified by forcing a UI failure and confirming the screenshot embedded; 64 green.

## 13. `make the data like api data, xpath as a separate json files for data handling`

- Externalised locators and test data to JSON:
  - `tests/ui/config/locators.json`, `tests/ui/config/test_data.json`,
    `tests/ui/config/loader.py`;
  - `tests/api/tests/data/fr05_schema.json`, `tests/api/tests/data/api_test_data.json`.
- Updated `settings.py`, `autocomplete_page.py` (locators from JSON), three UI test
  modules and four API test modules to read from the data files; parametrised the
  filtering, locale and `suggestion_list` tests over the JSON datasets.
- Result: **66 tests green** (25 UI + 41 API). README + `docs/8` updated.

## 14. Supplied a redrafted Task 6 reflection

- `docs/7-ai-reflection.md` replaced with the user's draft (a/b/c/d), with one wording
  edit so the "structure recommendation" clause matches the JSON data layer actually in
  the repo. Claude flagged which claims in the draft are not evidenced by this session's
  transcript so the user can reconcile them against the full set of transcripts.

## 15. `update with detailed prompt ...`

- This file expanded to the detailed log above.

---


## Clarifying questions Claude asked (all of them)

- Stack → **Python**; test target → **local fixture**; working mode → build-all
  (later overridden to step-by-step).
- Task 4 error path → **both** empty-input and required-selection; API cross-check →
  **light**; filter modes → **both**.
- Design of the empty-field suggestion list → **B (hidden until typing)**.

## Debugging / operational questions handled

- Playwright setup from scratch and in the pre-built `.venv`.
- Initial suggestion-list visibility (led to Design B).
- Running the fixture app with different filter / validation config.
- Setting up `pytest-html` and embedding failure screenshots.
