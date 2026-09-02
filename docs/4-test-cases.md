# 4 — Detailed Test Cases (Task 3)

Detailed test cases covering both UI and API behaviour for the Autocomplete Form.
Each case lists Test Case ID, Title, Preconditions, numbered Test Steps, Expected
Results, and Test Data.

---

## TC-01 — API: Validate presence and data types of all FR-05 response properties

**Preconditions:** User `test123@gmail.com` logged in; autocomplete form submitted successfully via Next.

**Test Steps:**
1. Trigger form submission via UI (or replay via API client) with a valid suggestion selected.
2. Capture the persisted API response payload.
3. Verify all 7 properties (`account_id`, `account_email`, `start_date`, `end_date`, `locale`, `text`, `suggestion_list`, `completed`) are present.
4. Check data type of each field against FR-05 (string, string, timestamp, timestamp, string, string, string, Boolean).

**Expected Results:** All properties present; all types match FR-05 except `completed`, which is logged as a known deviation (returned as string `"true"` instead of Boolean) — flag as contract mismatch, not a blocking failure per confirmed behavior.

**Test Data:** `account_email` = `test123@gmail.com`, `text` = `"agile methodology"`.

---

## TC-02 — API: Verify account_id and account_email map to the logged-in session

**Preconditions:** User logged in as `test123@gmail.com`.

**Test Steps:**
1. Log in with `test123@gmail.com`.
2. Complete and submit the autocomplete form.
3. Inspect persisted response's `account_id` and `account_email`.

**Expected Results:** `account_email` exactly equals `"test123@gmail.com"`; `account_id` matches the backend-assigned ID for that account (cross-check against user/account service if accessible).

**Test Data:** `account_id` = `98765` (expected reference), `account_email` = `test123@gmail.com`.

---

## TC-03 — API: Verify start_date/end_date reflect correct IST (UTC+05:30) local-time conversion

**Preconditions:** Test environment timezone set to IST; system clock verified accurate.

**Test Steps:**
1. Note the local system time at the moment the form loads.
2. Load the autocomplete form and record wall-clock time (T1).
3. Complete the field and click Next; record wall-clock time (T2).
4. Retrieve persisted `start_date` and `end_date` from the API response.
5. Convert both persisted values to IST and compare against T1/T2 (allow small tolerance, e.g., ±5s for network/processing latency).

**Expected Results:** Converted `start_date` ≈ T1 and `end_date` ≈ T2 in IST, confirming backend correctly applied the +05:30 offset — regardless of whether the wire format uses Z/UTC or an explicit +05:30 offset, the underlying instant must match true local time when converted.

**Test Data:** Timezone = IST (UTC+05:30); expected offset = +05:30.

---

## TC-04 — API: Verify end_date is always ≥ start_date

**Preconditions:** Valid session; form accessible.

**Test Steps:**
1. Load the form (start timer).
2. Wait ~10–15 seconds before entering text, to create a measurable gap.
3. Enter valid text, select suggestion, click Next.
4. Retrieve `start_date` and `end_date` from response.

**Expected Results:** `end_date` is strictly later than `start_date`, and the delta approximates the actual time spent on the form (±tolerance).

**Test Data:** Deliberate delay ≈ 10–15s between form load and Next click.

---

## TC-05 — API: Validate suggestion_list format and content integrity

**Preconditions:** Suggestions list on UI contains: `agile methodology`, `agile methodology process`, `agile methodology process testing`.

**Test Steps:**
1. Enter `"agile"` into the input field to trigger suggestions.
2. Confirm all 3 `<li>` suggestions render in the UI.
3. Select a suggestion and submit via Next.
4. Inspect the persisted `suggestion_list` value in the API response.
5. Check for unexpected line breaks, extra whitespace, or truncation within the comma-separated string.

**Expected Results:** `suggestion_list` should read as a single continuous string: `"agile methodology, agile methodology process, agile methodology process testing"` with no embedded newline/whitespace break — flag as a defect if a line break is present in the raw payload (confirmed real, not a paste artifact).

**Test Data:** Input = `"agile"`; expected suggestions = 3 items listed above.

---

## TC-06 — API: Verify text and suggestion_list consistency when user selects a suggestion

**Preconditions:** Suggestions visible after typing partial text.

**Test Steps:**
1. Type `"agile methodology process"` into the input field.
2. From the rendered suggestion list, click/select `"agile methodology process"`.
3. Click Next.
4. Inspect persisted `text` value.

**Expected Results:** `text` exactly equals the selected suggestion (`"agile methodology process"`), not partial/raw keystrokes; `suggestion_list` still contains the full candidate set shown at time of selection.

**Test Data:** Input = `"agile methodology process"`.

---

## TC-07 — UI: Verify autocomplete suggestions filter/display correctly on partial input

**Preconditions:** Autocomplete form loaded at `https://test.com/autocomplete-form`; admin-configured suggestion set includes the 3 sample values.

**Test Steps:**
1. Click into `#input-field`.
2. Type `"ag"`.
3. Observe the `.suggestions` list rendering.
4. Continue typing to `"agile methodology p"`.
5. Observe list update.

**Expected Results:** Suggestion list narrows/updates dynamically to show only matching entries as input becomes more specific; list is visible only when there's a partial/full match, hidden otherwise.

**Test Data:** Progressive input: `"ag"` → `"agile methodology p"`.

---

## TC-08 — UI: Verify Next button rejects free text not matching any suggestion

**Preconditions:** Form loaded; no suggestion selected.

**Test Steps:**
1. Type an arbitrary string not present in the suggestions, e.g. `"random text xyz"`.
2. Click the `#next-button`.
3. Observe form behavior.

**Expected Results:** `.error-message` (`"Error: Invalid input. Please select a valid suggestion."`) is displayed; form does not proceed to `.success-container`; no API call is made to persist the response (or, if made, it's rejected server-side — confirm which per actual implementation).

**Test Data:** Input = `"random text xyz"`.

---

## TC-09 — UI: Verify successful submission flow with valid suggestion selection

**Preconditions:** Form loaded; logged in as `test123@gmail.com`.

**Test Steps:**
1. Type `"agile"` to trigger suggestions.
2. Click on `"agile methodology"` from the suggestion list.
3. Click `#next-button`.
4. Observe UI state.

**Expected Results:** `.error-message` remains hidden; `.success-container` becomes visible with text `"Success! Your response has been recorded."`; corresponding API call fires with `text` = `"agile methodology"` and correct `suggestion_list`.

**Test Data:** Input/selection = `"agile methodology"`.

---

## TC-10 — UI: Verify input field behavior on empty submission

**Preconditions:** Form loaded; input field empty.

**Test Steps:**
1. Leave `#input-field` empty.
2. Click `#next-button` directly without typing.
3. Observe form response.

**Expected Results:** Error message displays (or a distinct "required field" validation, if implemented separately); form does not proceed to success state; no premature API persistence occurs.

**Test Data:** Input = `""` (empty).

---

## Traceability — test case → scenario (`docs/2`) / requirement

| Test case | Scenario(s) | Requirement(s) |
| --- | --- | --- |
| TC-01 | 1, 7 | FR-05 (all fields, types) |
| TC-02 | 1 | FR-05 (`account_id`, `account_email`) |
| TC-03 | 1 | FR-05 (`start_date`, `end_date`) |
| TC-04 | 1 | FR-05 (`start_date`, `end_date`) |
| TC-05 | 7 | FR-05 (`suggestion_list`) |
| TC-06 | 4, 7 | FR-01, FR-02, FR-05 (`text`, `suggestion_list`) |
| TC-07 | 3, 4 | FR-02 |
| TC-08 | 6 | FR-01, FR-04 |
| TC-09 | 1, 2 | FR-01, FR-04, FR-05 |
| TC-10 | 8 | FR-01, FR-04 |
