# 7 — AI Usage Reflection (Task 6)

## a. Tools Used

**Claude (Anthropic)** — used throughout this assignment for requirement analysis, test
design, defect analysis, sample application development, and automation framework review.

## b. Usage Areas

1. **Requirement vs. actual-response discrepancy analysis** — comparing the given API
   response JSON against the FR-05 data contract to identify type mismatches and
   formatting issues.
2. **Test case design** — generating structured UI and API test cases (ID, title,
   preconditions, steps, expected results, test data) for both the general FR-05
   contract and the specific discrepancies found.
3. **Defect identification and reporting** — formalising the discrepancies into a defect
   log with severity and status.
4. **Requirement & architecture gap analysis** — surfacing contradictions and
   ambiguities across FR-01 through FR-05 (e.g. free-text vs. exact-match conflict,
   filter-mode delivery mechanism, timestamp "local time" interpretation) that weren't
   explicit in the original spec.
5. **Sample application + automation scaffold** — building a working Flask app
   implementing the requirement (with two defects intentionally seeded) plus a
   Playwright/pytest suite, as a practice target for automation.
6. **Automation framework review** — reviewing an existing (separately authored)
   Playwright/pytest suite against best practices, structure, and scalability.

## c. Modifications Made (my corrections / additions to the AI output)

**Example 1 — Redirecting the AI's approach from assumption to clarification.**
In the defect-analysis phase, Claude's first pass listed several discrepancies (locale
format, timestamp suffix, `completed` type, `suggestion_list` formatting) but treated
some as settled defects without confirming they weren't artifacts of my paste or
reasonable interpretations of an ambiguous spec. I explicitly corrected this ("don't
jump to conclusions, ask me clarifications") and then supplied the ground truth myself —
e.g. confirming the boolean-as-string was actual/expected API behaviour (not a paste
error), and that the timestamps represent a genuine backend locale-based conversion
rather than a raw UTC passthrough. This changed which items got logged as confirmed
defects (`completed` type mismatch, `suggestion_list` line break) versus dismissed as
non-issues (locale format, timestamp suffix) — Claude's own first pass had these less
clearly separated.

**Example 2 — Elevating a buried finding into a proper structural recommendation.**
When Claude reviewed the automation framework, it flagged `SUGGESTIONS` list duplication
as one minor bullet point among several other gaps, without naming the underlying
pattern. I identified that this was really a missing architectural layer — no
centralised test-data management at all (locators were fine, but suggestions, expected
messages, locale values, and the test account were all scattered as inline literals
across multiple files). I asked Claude to treat this as its own discrepancy, which
produced a proper externalised-data layer: JSON files for locators
(`ui/config/locators.json`) and for suggestions / messages / expected datasets
(`ui/config/test_data.json`, `api/tests/data/api_test_data.json`), loaded by thin
helpers, with the filtering, locale, and contract tests parametrised over them — a
meaningfully more useful output than the original one-line duplication note.

## d. AI Limitations

**Example 1 — Under-weighted the test-data gap on first pass.**
As above: Claude's initial framework review correctly *noticed* the `SUGGESTIONS`
duplication but classified it as a minor DRY violation rather than recognising it as a
missing best-practice layer (centralised test-data management, parallel to how locators
are centralised in Page Objects). It took my explicit prompt to reframe and properly
scope this — the AI didn't independently identify the pattern's full significance.

**Example 2 — Missed the embedded line break in `suggestion_list` on the first pass.**
In the Task 2 response JSON the `suggestion_list` value wraps across two physical lines —
a literal newline inside the string. Claude's first discrepancy pass did not catch it;
it flagged only the stringified `completed`, the bare `locale`, and the UTC timestamps.
I identified the line break as the second genuine defect (DEF-02), and it became the
target of TC-D03 / TC-D04.

**Example 3 — No ability to actually execute and verify a suite from an artifact alone.**
When reasoning about an uploaded automation project, Claude can only statically read the
code and a bundled `report.html`. It correctly caught that such a report contained only
UI test results with no API tests represented — meaning a claim that "everything is
working" couldn't be verified from the artifact, since the API suite's real pass/fail
status was never demonstrated. This is a hard limitation rather than an error: without
the root-level `conftest.py`, the fixture app, and a live environment to run `pytest`,
the AI can reason about code correctness in principle but not confirm runtime behaviour.

## AI transcript

The prompts given to Claude Code are recorded in `prompts/prompts.md`. The complete JSON
transcript(s) of the session(s) are included with the submission.
