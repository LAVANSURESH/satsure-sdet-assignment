# 8 — Architecture Discussion

## 8.1 Goals

- Runs end-to-end with a single `pytest`, no external system required.
- Clear separation between the system under test, the UI layer, and the API layer.
- Cheap to extend — a new page, a new contract, or a new environment is an additive change.
- CI-ready: fast, isolated per test, and produces failure artefacts.

## 8.2 Layered structure

```
fixture/           stand-in SUT — static form (index.html / app.js / styles.css)
                   + Flask mock API (server.py)
conftest.py        session-scoped server boot + autouse per-test reset
tests/ui/
  config/          settings.py — base URL, form path, timeouts (env-overridable)
  pages/           BasePage -> AutocompletePage (locators + actions only)
  tests/           scenario-oriented specs + suite fixtures
tests/api/
  tests/           schema.py (contract as data) + ApiClient + specs
docs/              analysis and design deliverables
```

| Choice | Why |
| --- | --- |
| **Python + pytest** | Matches the JD's Python emphasis; fixtures give clean dependency injection; one runner for UI and API. |
| **pytest-playwright** for UI | First-class auto-waiting removes most sleep-based flakiness; trace/video/screenshot on failure built in. |
| **`requests` + `jsonschema`** for API | No browser overhead (~0.5s for 39 tests); schema is plain data, easy to diff against a spec change. |
| **Local fixture as SUT** | The brief's URL is not real. A fixture that implements FR-01…FR-05 makes every test executable and doubles as an executable interpretation of the spec. |

## 8.3 Design patterns

- **Page Object Model** — every locator and interaction lives in `AutocompletePage`;
  tests hold only assertions. `BasePage` carries shared navigation so the model scales
  past one screen.
- **Fixture-based dependency injection** — `live_server`, `form_page`, `open_form`
  (a factory, so config can be set *before* the page loads), `api`, `submitted`. Tests
  declare what they need; there is no global state.
- **Contract as data** — FR-05 is a JSON Schema *file* (`data/fr05_schema.json`) plus
  small pure validators (`is_bcp47`, `bcp47_region`, `parse_timestamp`,
  `parse_suggestion_list`). Reused across POST and GET, and updated without touching code.
- **Externalised locators and test data** — selectors live in
  `ui/config/locators.json`, inputs / expected values in `ui/config/test_data.json` and
  `api/tests/data/api_test_data.json`. The filtering, locale, and `suggestion_list`
  tests are parametrised over those datasets, so a new case is a JSON edit. Keeps the
  page object free of literals and lets non-authors extend coverage.
- **Thin API client** — one `ApiClient` owns endpoint knowledge; test bodies read as
  intent, not plumbing.
- **Fault injection over response mocking** — the fixture emits deliberately broken
  payloads via `?inject=<fault>`, so negative tests exercise the real validation path
  and still pass deterministically.

## 8.4 State and isolation

- One server process per session (fast start-up cost paid once).
- `POST /api/reset` runs autouse before every test — restores default config and clears
  the stored response, so a `set_config(...)` in one test never leaks into the next.
- No shared mutable test data; each test submits its own input.
- Playwright `expect(...)` retries until the condition holds or times out — no manual waits.

## 8.5 Configuration and environments

Everything environment-specific is an env var with a sensible default:
`UI_BASE_URL`, `UI_FORM_PATH`, `UI_TIMEOUT_MS`, `FIXTURE_PORT`, `FILTER_MODE`,
`REQUIRE_SUGGESTION`.

To point the same suites at a deployed system: set `UI_BASE_URL`, skip the
`live_server` autostart (it already no-ops when the port is open), repoint
`ApiClient.base_url`, and every test runs unchanged.

## 8.6 CI/CD integration

- **Pipeline step:** `pip install -r requirements.txt && playwright install --with-deps chromium && pytest --junitxml=report.xml`.
- **Quality gate:** block the merge on a non-green run; publish the JUnit XML; upload
  `test-results/` (trace, video, screenshot — all failure-only).
- **Parallelism:** `pytest -n auto` (pytest-xdist); run the API and UI suites as
  separate jobs; expand browsers with `--browser firefox|webkit`.
- **Stage placement:** the API suite (~0.5s) belongs in the fast pre-merge gate; the UI
  suite runs pre-merge on Chromium and full cross-browser on a nightly schedule.

## 8.7 Scaling up

- **More screens:** add a `*Page(BasePage)` and a spec file; promote shared journeys to
  a `flows/` module.
- **More contracts:** one `schema.py` per resource; add consumer-driven contract tests
  (e.g. Pact) against the real provider.
- **Non-functional (per JD):** k6 or JMeter for FR-04 load and scalability, axe-core for
  accessibility, Playwright `devices` for mobile viewports, visual snapshots for the
  suggestion list.
- **Test data:** move to builders/factories as the input space grows; never depend on
  execution order.

## 8.8 Trade-offs taken for a 48-hour exercise

- **Local fixture instead of the real system** — unblocks executable tests but encodes
  my reading of the ambiguous requirements (`docs/1`). Expected values in
  `test_suggestion_list.py` and the locale/timestamp assertions may need revising
  against the real backend.
- **Flask development server, not a production WSGI stack** — fine for tests, not
  representative of production latency or error modes.
- **Chromium-only by default** — matches the stated environment (Chrome / Windows 10);
  cross-browser is one flag away but unproven here.
- **No auth layer** — login is out of scope, so `account_id` / `account_email` are
  server-fixed. A-09 (client-submitted identity is a security risk) is noted but untested.
- **Single locale / timezone** — `en-IN` and IST are hard-expected; a real matrix would
  parametrize both.

## 8.9 If this were production

- Contract tests owned by the provider's pipeline, with the schema published as a
  versioned artefact.
- `data-testid` attributes added to the app so selectors are decoupled from copy.
- Trace-on-failure surfaced in the CI run summary, plus a flake-rate dashboard.
- Accessibility and performance gates running alongside the functional suite.
- Configuration and secrets from the CI secret store rather than env-var defaults.
