"""Task 5e — negative test cases (missing fields, invalid data, bad requests).

Response-shape corruptions (missing field, stringified boolean, full suggestion
list) are produced with the fixture's `?inject=` hook; request-level failures are
produced by sending bad input directly. Inputs come from data/api_test_data.json.
"""
import jsonschema
import pytest

from tests.api.tests.schema import (
    FR05_SCHEMA,
    TEST_DATA,
    bcp47_region,
    is_bcp47,
    parse_suggestion_list,
    parse_timestamp,
)

pytestmark = pytest.mark.api

SUGGESTIONS = TEST_DATA["suggestions"]
NAIVE_TS = TEST_DATA["timestamps"]["naive"]
REJECT = TEST_DATA["negative"]["reject_inputs"]
SCHEMA_BREAKING = TEST_DATA["negative"]["schema_breaking_injects"]


# --- 1 & 2. response-shape corruptions that must fail schema validation ---
@pytest.mark.parametrize("fault", SCHEMA_BREAKING)
def test_corrupted_response_fails_schema_validation(api, submitted, fault):
    submitted()
    body = api.get_latest(inject=fault).json()
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(body, FR05_SCHEMA)


def test_stringified_completed_is_not_a_boolean(api, submitted):
    submitted()
    body = api.get_latest(inject="string_completed").json()
    assert body["completed"] == "true"
    assert type(body["completed"]) is not bool


def test_missing_field_is_actually_absent(api, submitted):
    submitted()
    body = api.get_latest(inject="missing_field").json()
    assert "end_date" not in body


# --- 3. invalid data: suggestion_list returns everything --------------
def test_all_suggestions_inject_violates_the_only_matching_rule(api, submitted):
    submitted("agile methodology process testing")  # only one genuine match
    body = api.get_latest(inject="all_suggestions").json()
    got = parse_suggestion_list(body["suggestion_list"])
    assert got == SUGGESTIONS  # bug reproduced
    assert got != ["agile methodology process testing"]  # what it should have been


# --- 4. invalid data: locale without a region (for this environment) --
def test_locale_without_region_is_flagged_for_this_environment(api):
    body = api.submit("agile methodology", locale="en").json()
    assert is_bcp47(body["locale"])            # 'en' is still well-formed BCP 47 ...
    assert bcp47_region(body["locale"]) is None  # ... but carries no region -> flagged


# --- 5. invalid data: naive timestamp with no timezone --------------
def test_timestamp_without_timezone_is_detected(api):
    body = api.submit(
        "agile methodology",
        start_date=NAIVE_TS["start"],
        end_date=NAIVE_TS["end"],
    ).json()
    assert parse_timestamp(body["start_date"]).tzinfo is None  # not acceptable per FR-05


# --- 6. bad request: empty text ----------------------------------
def test_empty_text_submission_is_rejected(api):
    resp = api.submit(REJECT["empty_text"])
    assert resp.status_code == 400
    assert "valid suggestion" in resp.json()["error"].lower()


# --- 7. bad request: free text while a selection is required ------
def test_free_text_rejected_when_selection_required(api):
    api.set_config(require_suggestion_selection=True)
    resp = api.submit(REJECT["free_text_when_selection_required"])
    assert resp.status_code == 400


# --- 8. bad request: no JSON body at all ------------------------
def test_request_with_no_body_is_rejected(api):
    resp = api.submit("", raw_body={})
    assert resp.status_code == 400
