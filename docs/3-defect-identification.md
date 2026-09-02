# 3 — Defect Identification (Task 2)

## 3.1 Response under test

After completing the form by selecting **"agile methodology"** from the suggestion
list, a `GET` on the API returned:

```json
{
  "account_id": "98765",
  "account_email": "test123@gmail.com",
  "start_date": "2024-03-15T10:30:00Z",
  "end_date": "2024-03-15T10:32:00Z",
  "locale": "en",
  "text": "agile methodology",
  "suggestion_list": "agile methodology, agile methodology process, agile
methodology process testing",
  "completed": "true"
}
```

## 3.2 Discrepancy analysis vs. FR-05

| Field | FR-05 expectation | Actual | Verdict |
| --- | --- | --- | --- |
| `account_id` | ID of the account that completed the form (type not specified — see A2) | `"98765"` (string) | **OK** — FR-05 does not pin the type; treated as an opaque identifier. |
| `account_email` | Email of that account | `"test123@gmail.com"` | **OK** — matches the logged-in user. |
| `start_date` | Timestamp in the user's **local time** when they reached the form | `"2024-03-15T10:30:00Z"` (UTC) | **Discrepancy (observation).** Wire format is UTC `Z`, not local `+05:30`. Per the assignment's confirmed behavior, this is acceptable **only if** the instant converts to the correct IST wall-clock time (validated by TC-D07). Contract-clarity issue — the serialization rule for "local time" is undefined (A3). |
| `end_date` | Timestamp in the user's local time when they selected Next | `"2024-03-15T10:32:00Z"` (UTC) | Same observation as `start_date`. Ordering is fine: `end_date` > `start_date` by 2 minutes. |
| `locale` | IETF BCP 47 (e.g., `en-IN`) | `"en"` | **Discrepancy (observation).** No region subtag. `"en"` is still valid BCP 47, and `en-IN` in FR-05 is only an example, so per confirmed behavior this reflects the browser's reported language and is **not a defect** — but whether a region is *required* must be confirmed (A5). |
| `text` | Text entered/selected in the input | `"agile methodology"` | **OK** — matches the selected suggestion. |
| `suggestion_list` | Comma-separated string of suggestions matching the entered/selected value | `"agile methodology, agile methodology process, agile⏎methodology process testing"` | **DEFECT.** The string contains an embedded line break between `"agile"` and `"methodology process testing"`. The contract is a single-line, `", "`-separated string. (The *content* — all three suggestions — is acceptable here: `"agile methodology"` is a prefix of all three under FR-02.) |
| `completed` | **Boolean** | `"true"` (string) | **DEFECT.** Serialized as a JSON string, not a native boolean. Breaks schema validation and any strictly-typed or loosely-typed consumer (see TC-D02). |

## 3.3 Summary

| ID | Type | Field | Description | Severity |
| --- | --- | --- | --- | --- |
| **DEF-01** | Defect | `completed` | Returned as string `"true"` instead of JSON boolean `true` | **High** — contract/type violation; breaks schema validation and downstream boolean logic |
| **DEF-02** | Defect | `suggestion_list` | Embedded line break (`\n`) inside the comma-separated string | **Medium** — comma-split still works, but raw string comparison, CSV export, and regex matching break or emit malformed output |
| **OBS-01** | Observation / needs confirmation | `locale` | Bare `en`, no region subtag (FR-05 example is `en-IN`) | Low — valid BCP 47; confirm whether region is mandatory |
| **OBS-02** | Observation / needs confirmation | `start_date` / `end_date` | Wire format is UTC `Z`, not an explicit local `+05:30` offset | Low — acceptable if the instant converts to correct IST local time; confirm the serialization rule |

---

## 3.4 Defect-targeted test cases

Detailed test cases specifically targeting the discrepancies/defects identified between
the actual API response and FR-05.

---

### TC-D01 — API: Validate `completed` field data type is Boolean, not String

- **Preconditions**: User logged in as `test123@gmail.com`; autocomplete form accessible.
- **Test Steps**:
  1. Complete the form by typing `"agile"` and selecting `"agile methodology"` from suggestions.
  2. Click `#next-button` to submit.
  3. Capture the raw persisted API response.
  4. Inspect the `completed` field's JSON type (not just its value) using `typeof` check or schema validator.
- **Expected Results**: `completed` should be serialized as native JSON Boolean `true`, not the String `"true"`. Schema validation against FR-05 should pass for type `boolean`.
- **Test Data**: `text = "agile methodology"`; Expected: `completed: true` (Boolean). Actual (defect): `completed: "true"` (String).

---

### TC-D02 — API: Verify downstream Boolean logic does not misfire due to stringified `completed`

- **Preconditions**: A consuming service/script reads the `completed` field to gate a conditional action (e.g., mark form as done).
- **Test Steps**:
  1. Submit the form successfully.
  2. Retrieve the API response.
  3. Simulate consumption: evaluate `if (response.completed)` in a loosely-typed context (e.g., JS).
  4. Separately simulate a hypothetical `"false"` string value and re-evaluate the same conditional.
- **Expected Results**: With strict/native Boolean, the conditional should evaluate `true`/`false` correctly. Defect risk: since `completed` is a String, `"false"` (a non-empty string) would incorrectly evaluate as truthy — expose this as a real downstream risk in the report.
- **Test Data**: `completed = "true"` (actual), hypothetical `completed = "false"` (edge case to illustrate risk).

---

### TC-D03 — API: Validate `suggestion_list` is a single-line string with no embedded line breaks

- **Preconditions**: Suggestions rendered: `agile methodology`, `agile methodology process`, `agile methodology process testing`.
- **Test Steps**:
  1. Type `"agile"` into `#input-field`.
  2. Select `"agile methodology"` from the suggestion list.
  3. Click Next.
  4. Retrieve the raw `suggestion_list` string from the persisted API response (inspect raw bytes/characters, not a rendered/pretty-printed view).
  5. Search the string for `\n`, `\r`, or other control characters.
- **Expected Results**: `suggestion_list` should equal exactly `"agile methodology, agile methodology process, agile methodology process testing"` with zero embedded newline or control characters.
- **Test Data**: Input = `"agile"`; Expected string has length matching concatenation with no breaks; Actual (defect) contains `\n` between `"agile"` and `"methodology process testing"`.

---

### TC-D04 — API: Verify `suggestion_list` parses correctly when split on comma delimiter

- **Preconditions**: Same as TC-D03.
- **Test Steps**:
  1. Submit form as in TC-D03.
  2. Take the persisted `suggestion_list` value.
  3. Programmatically split the string on `", "` delimiter.
  4. Count resulting array elements and compare each to the expected 3 suggestion values.
- **Expected Results**: Split should yield exactly 3 clean elements: `["agile methodology", "agile methodology process", "agile methodology process testing"]`. Defect impact: if a newline is embedded mid-string, the split may still work correctly with commas as delimiter, but any consumer doing raw string comparison, CSV export, or regex matching without normalizing whitespace will fail or produce malformed output — verify and document actual downstream effect.
- **Test Data**: Delimiter = `", "`; Expected element count = 3.

---

### TC-D05 — API: Verify `locale` field correctly reflects configured browser/session language

- **Preconditions**: Chrome browser language set to English (India test environment, IST timezone).
- **Test Steps**:
  1. Confirm browser language setting via `navigator.language` or browser settings (expect `"en"` or `"en-US"` depending on config).
  2. Log in and load the autocomplete form.
  3. Submit the form.
  4. Inspect persisted `locale` field in API response.
- **Expected Results**: `locale` value matches whatever the browser/session actually reports — not necessarily `en-IN`. Confirm this is consistent behavior (not a defect) by cross-referencing against the browser's actual configured language string.
- **Test Data**: Browser language = `en` (per test environment); Expected `locale = "en"` (confirmed correct, non-defect).

---

### TC-D06 — API: Verify `locale` changes correctly when browser language is switched (regression/consistency check)

- **Preconditions**: Ability to change Chrome's language setting to a regional variant (e.g., `en-GB` or `hi-IN`).
- **Test Steps**:
  1. Change browser language setting to `en-GB` (or another variant).
  2. Restart session/re-login as `test123@gmail.com`.
  3. Load and submit the autocomplete form.
  4. Inspect persisted `locale` field.
- **Expected Results**: `locale` reflects the newly configured browser language (e.g., `"en-GB"`), confirming the field is dynamically sourced from session/browser config rather than hardcoded to `"en"`. If it does NOT change, this becomes a **new defect** (locale not correctly captured).
- **Test Data**: Browser language = `en-GB` (or `hi-IN`); Expected `locale` matches configured value.

---

### TC-D07 — API: Verify `start_date`/`end_date` correctly represent IST-converted instants (not just UTC suffix)

- **Preconditions**: Test machine timezone confirmed as IST (UTC+05:30); system clock synced.
- **Test Steps**:
  1. Record system wall-clock time at form load (T1, in IST).
  2. Load the form.
  3. Wait ~10 seconds, then select a valid suggestion and click Next (record T2, in IST).
  4. Retrieve `start_date` and `end_date` from the persisted API response.
  5. Convert both timestamps to IST (UTC+05:30) regardless of their wire-format suffix (`Z`/UTC).
  6. Compare converted values against T1 and T2.
- **Expected Results**: Converted `start_date` ≈ T1 and `end_date` ≈ T2 (within a few seconds' tolerance), confirming the backend performed accurate local-time conversion internally — this validates the confirmed non-defect status of the `Z` suffix.
- **Test Data**: Timezone = IST (UTC+05:30); Expected delta between `start_date` and `end_date` ≈ 10s (± tolerance).

---

### TC-D08 — UI: Verify no visible/functional impact on suggestion list rendering despite backend string defect

- **Preconditions**: Form loaded; suggestions visible in `.suggestions` list.
- **Test Steps**:
  1. Type `"agile"` into `#input-field`.
  2. Visually inspect the rendered `<li>` suggestion items in the DOM.
  3. Select `"agile methodology process testing"` (the longest suggestion, most likely affected by the line-break defect).
  4. Click Next and confirm success state.
  5. Cross-check that the UI-rendered suggestion text has no visible line break/wrapping artifact, independent of the backend string defect in TC-D03.
- **Expected Results**: UI rendering of suggestions remains clean and unaffected (line break is a backend/API-only defect); `.success-container` displays correctly; confirms defect is isolated to data persistence layer, not UI presentation layer — important for defect severity/scope classification.
- **Test Data**: Selected suggestion = `"agile methodology process testing"`.

---

### TC-D09 — API: Regression check — verify `completed` and `suggestion_list` defects persist across repeated submissions

- **Preconditions**: Ability to submit the form multiple times (fresh sessions or reset state).
- **Test Steps**:
  1. Submit the form 3 times in separate sessions, each time selecting a different suggestion (`agile methodology`, `agile methodology process`, `agile methodology process testing`).
  2. Capture the API response for each submission.
  3. Check `completed` field type in all 3 responses.
  4. Check `suggestion_list` string for embedded line breaks in all 3 responses.
- **Expected Results**: Determine whether both defects are consistent/deterministic (occur every time) or intermittent (only under specific conditions, e.g., only when the longest suggestion is selected) — this materially affects defect priority and root-cause investigation.
- **Test Data**: 3 submissions with `text` = each of the 3 available suggestions respectively.

---

## 3.5 Defect → test case traceability

| Defect / Observation | Field | Covered by |
| --- | --- | --- |
| DEF-01 — `completed` string, not boolean | `completed` | TC-D01, TC-D02, TC-D09 |
| DEF-02 — `suggestion_list` embedded line break | `suggestion_list` | TC-D03, TC-D04, TC-D08, TC-D09 |
| OBS-01 — `locale` bare `en`, no region | `locale` | TC-D05, TC-D06 |
| OBS-02 — timestamps on the wire in UTC `Z` | `start_date`, `end_date` | TC-D07 |
