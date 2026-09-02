# 2 — Test Scenarios (Task 1)

Scenarios for the Autocomplete Form, ranked highest → lowest risk.
Risk = business impact × likelihood of failure, weighted toward **persisted-data
integrity** and **truthful submission feedback** (a wrong record or a false "success"
is silent corruption that surfaces far downstream).

> The brief asks for a top 10; this list currently holds **9** agreed scenarios.
> A candidate 10th (keyboard operation — Tab order, Enter to submit, Escape to
> clear) is noted under *Beyond this list* and can be promoted if wanted.

| # | Test scenario | Risk | Reason |
| --- | --- | --- | --- |
| 1 | Verify the user data is posted to the API after clicking **Next**. | **Critical** | A UI success message can be misleading if the underlying persistence is broken or incomplete; this verifies the actual business outcome, not just the visual confirmation. |
| 2 | Verify that clicking **Next** after a proper suggestion selection returns **200 OK**. | **Critical** | Confirms the core happy path works end-to-end; if this fails, the feature is unusable for every user. |
| 3 | Verify suggestions are **not** listed when the input does not match — configuration (match anywhere) **disabled** (default prefix mode). | **High** | This is the default filtering behaviour every user experiences, so a regression here affects the whole user base, not just an edge config. |
| 4 | Verify suggestions **are** listed for a matching input. | **High** | The actual positive path — users must see the options they are meant to choose from. |
| 5 | Verify suggestions **are** listed when the input is a mismatched substring — configuration (match anywhere) **enabled**. | **High** | Exercises a distinct config-gated code path that is easy to break without noticing, since it only runs when the flag is on. |
| 6 | Verify that clicking **Next** with an invalid selection (data typed but no valid suggestion selected) throws an error. | **High** | Validates that bad submissions are blocked before reaching the backend, protecting data integrity in the persisted records. |
| 7 | Verify `suggestion_list` in the API payload reflects **only the matched suggestions**. | **High** | Divergence here is invisible in the UI and only catchable via the API. |
| 8 | Click **Next** with no selection and no input typed. | **Medium** | An undefined edge case in the spec; low-frequency in real usage but risks an unhandled crash or a silent no-op if not tested. |
| 9 | Verify the case sensitivity of the suggestions listed vs. the input typed. | **Low** | A minor UX inconsistency rather than a functional blocker, but worth a quick check since case handling is unspecified. |

**Distribution:** 2 Critical · 5 High · 1 Medium · 1 Low.

*Order note:* the scenarios are sorted highest → lowest risk as the brief requires;
within a risk band, the order reflects breadth of user impact.

## Scenario → requirement traceability

| # | Requirements exercised |
| --- | --- |
| 1 | FR-04, FR-05 (all fields) |
| 2 | FR-04 |
| 3 | FR-02 |
| 4 | FR-02 (and FR-03 when enabled) |
| 5 | FR-03 |
| 6 | FR-01, FR-04 |
| 7 | FR-05 (`suggestion_list`), FR-02 / FR-03 |
| 8 | FR-01, FR-04 |
| 9 | FR-02 |

## Beyond this list (noted, lower priority or candidate 10th)

- **Keyboard operation** — Tab reaches input → visible suggestions → Next in order;
  Enter submits; Escape clears the input and closes the list. *(Candidate 10th.)*
- FR-05 field-level correctness — `completed` boolean type, `locale` BCP 47 with
  region, `start_date`/`end_date` in local time — is covered in
  `docs/3-defect-identification.md` and `docs/4-test-cases.md`.
- Double-click / duplicate **Next** submission.
- XSS or comma/quote characters in `text`, and their effect on the comma-joined
  `suggestion_list`.
- Very long input; `start_date` captured before vs. after the auth redirect;
  success and error elements shown at the same time; network timeout on submit.
