# 1 — Requirement Analysis

## 1.1 Purpose & scope

Analyse the Autocomplete Form requirements before designing tests: restate each
functional requirement, pin down data types and formats, and record every ambiguity,
contradiction, and assumption that affects test design.

**In scope:** the Autocomplete form UI (`https://test.com/autocomplete-form`), its
filtering behaviour, submission flow, and the persisted response contract (FR-05).

**Out of scope (per brief):** login / authentication, the Admin configuration UI, and
the backend datastore internals. These are treated as trusted preconditions.

## 1.2 System overview

| Element | Detail |
| --- | --- |
| Title | Static heading on the form |
| `#input-field` | Free-text input, `placeholder="Type here..."` |
| `ul.suggestions > li` | Three static suggestions: `agile methodology`, `agile methodology process`, `agile methodology process testing`. The list is hidden until the user types a matching value (see A-12). |
| `#next-button` | Submits the response via a REST call |
| `span.error-message` | `"Error: Invalid input. Please select a valid suggestion."` — hidden until an invalid submission |
| `div.success-container` | `"Success! Your response has been recorded."` — hidden until a successful submission |

## 1.3 Functional requirements — analysis

### FR-01 — Text input
Users may **type any value** *or* click/tap a suggestion to select it. Selecting a
suggestion populates `#input-field` with that suggestion's text.
*Implication:* free text that matches no suggestion is a legitimate input by default
(but see C-01 / A-01).

### FR-02 — Prefix-match filtering (default)
A suggestion stays visible only while the typed text is a **prefix** of it
(case handling unspecified — see A-06). Suggestions whose start does not match are
removed from the list. Typing text that is a prefix of nothing empties the list.
The brief does not say whether suggestions show before the user types; the adopted
position is that the list is **hidden while the field is empty** and appears once a
matching value is typed, then closes again on selection or Escape (see A-12).

### FR-03 — Match-anywhere filtering (configurable)
When enabled in backend configuration, a suggestion stays visible if the typed text
appears **anywhere** in it as a substring. Worked example from the brief: typing
`agile method` keeps all three visible.
*Implication:* the filtering mode is a backend-controlled toggle; both modes must be
regression-tested, and switching modes must not require a client redeploy.

### FR-04 — Form submission
Pressing **Next** issues a REST call to persist the response.
- HTTP **200** ⇒ success ⇒ `div.success-container` shown.
- Invalid input ⇒ `span.error-message` shown.
- Success and error states are assumed mutually exclusive (showing one clears the other).
- Which non-200 codes are returned, and whether validation is client- or server-side,
  are unspecified (A-02, A-10).

### FR-05 — Backend data contract

| Property | Description (brief) | Expected type | Expected format / rule | Notes |
| --- | --- | --- | --- | --- |
| `account_id` | ID of the account that completed the form | string *or* integer (type unspecified by FR-05) | non-empty; opaque; server-derived (A-09) | must equal the logged-in user's id |
| `account_email` | Email of that account | string | RFC 5321 email | must equal the logged-in user's email (`test123@gmail.com`) |
| `start_date` | Timestamp in the user's local time when they **reached** the form | string | ISO 8601; wire format (offset vs. `Z`) unresolved — C-02 | must resolve to the correct IST instant; capture point unclear (A-08) |
| `end_date` | Timestamp in the user's local time when they **selected Next** | string | ISO 8601 | `end_date >= start_date` |
| `locale` | User's locale | string | **IETF BCP 47**; FR-05 example is `en-IN` | region expected for this env (`en-IN`); whether a bare tag is acceptable is unresolved (A-07) |
| `text` | Text entered/selected in the input | string | verbatim value of `#input-field` at submit | value after any post-selection edit is unspecified (A-03) |
| `suggestion_list` | Comma-separated suggestions **matching** the entered/selected value | string | `", "`-joined subset of the suggestions | filtered-at-submission set vs. full list unresolved (A-04) |
| `completed` | Status of the response upload | **boolean** | `true` / `false` (not `"true"`) | persisted record ⇒ expected `true` |

## 1.4 Contradictions & ambiguities

Open questions raised during the requirement review. Each needs product-owner
confirmation before the FR-05 contract and acceptance criteria can be considered final.

### Contradictions

| ID | Description |
| --- | --- |
| **C-01** | FR-01 allows free typing, but the error message demands "a valid suggestion" — conflicting acceptance criteria. |
| **C-02** | FR-05 says "local time" but timestamps are conventionally UTC — unclear if the wire format needs an offset or just the correct underlying instant. |
| **C-03** | FR-02/FR-03 imply dynamic/configurable filtering, but the HTML shows a static hardcoded suggestion list — unclear how the filtering mode is actually delivered. |

### Ambiguities

| ID | Description |
| --- | --- |
| **A-01** | Unclear if Next requires an exact suggestion match, allows any free text, or a hybrid. |
| **A-02** | Unclear if validation is client-side (blocks the API call) or server-side (API call fires, error rendered from the response). |
| **A-03** | Unclear what `text` holds if the user edits the input after selecting a suggestion. |
| **A-04** | Unclear if `suggestion_list` is the filtered-at-submission set or the full static list. |
| **A-05** | No defined mechanism for how the client learns the active filter mode (prefix vs. match-anywhere). |
| **A-06** | No spec for minimum characters, case sensitivity, or whitespace handling in filtering. |
| **A-07** | Unclear if `locale` comes from server-side headers or client-side JS. |
| **A-08** | Unclear if `start_date` is captured at page-load (server or client) or at session start. |
| **A-09** | Unclear if `account_id` / `account_email` are server-derived or client-submitted (security risk if the latter). |
| **A-10** | No defined non-200 status codes or their triggers. |
| **A-11** | No defined double-submit / idempotency protection. |
| **A-12** | No defined behavior for the suggestion list / state when the input is cleared after a selection. |
| **A-13** | No stated behavior for filter-mode switching mid-session. |

### 1.4.1 Interim positions used for test design

Where a test or the local `fixture/` must commit to a behavior before confirmation,
the following positions are used (and are revisited if the product owner rules otherwise):

- **C-01 / A-01** — empty or whitespace-only input is always invalid; free text that
  matches no suggestion is accepted by default, gated by an optional
  `require_suggestion_selection` flag (default off, honouring FR-01).
- **C-02 / A-08** — timestamps are treated as correct if the underlying instant maps to
  the right IST wall-clock time, regardless of `Z` vs. `+05:30` on the wire
  (see `docs/3` OBS-02).
- **A-02** — both paths are exercised: the suite asserts on the rendered UI state and,
  independently, on the API status/response.
- **A-04** — `suggestion_list` is expected to be the set matching the submitted value
  under the active filter mode.
- **A-05 / A-13** — the client reads the mode from backend config on load; mid-session
  switching is out of scope until specified.
- **A-06** — filtering is assumed case-insensitive with the input trimmed before matching.
- **A-07** — `locale` is expected to carry a region for this environment (`en-IN`);
  whether a bare language tag is acceptable is unresolved (see `docs/3` OBS-01).
- **A-12** — the suggestion list is hidden on load and stays hidden until the user
  types a matching value; selecting a suggestion or pressing Escape closes it again.
  (Focus alone, without typing, does not open it.)

## 1.5 Assumptions

1. The three suggestions are static content, not backend-driven, for the duration of a session.
2. The form is reached only after a successful login; `account_id` / `account_email` are already established server-side.
3. A single environment is under test (Chrome / Windows 10 / English / IST); no cross-browser or multi-locale matrix is required.
4. The REST API is same-origin with the form.
5. Network is reliable; offline/timeout handling is out of scope unless explicitly raised.

## 1.6 Test environment

| Item | Value |
| --- | --- |
| Browser / OS | Chrome on Windows 10, UI language English |
| Logged-in user | `test123@gmail.com` |
| User location / timezone | India, IST (UTC+05:30) |
| Expected `locale` | `en-IN` |
| Production URL (brief) | `https://test.com/autocomplete-form` |
| Local stand-in (this repo) | `http://127.0.0.1:5057/autocomplete-form` — `fixture/` implements FR-01…FR-05 and the mock REST API so the suites run without the real system |

## 1.7 Key risk areas (feed into `docs/2-test-scenarios.md`)

- **Data integrity of the persisted FR-05 payload** — wrong types (`completed`), malformed `locale`, wrong timezone, over-broad `suggestion_list`. This is where the sample response in Task 2 actually breaks.
- **Submission feedback** — user must get a truthful success/error signal.
- **Filtering correctness** in both modes, including the empty-list edge.
- **The FR-01 / error-message contradiction (C-01)** — risk of either over-blocking valid users or accepting invalid data.
- **Client/server validation split (A-02) and undefined non-200 codes (A-10)** — affects where and how errors surface.
- **Keyboard & accessibility** — Tab order, Enter to submit, custom Escape-to-clear handler.
