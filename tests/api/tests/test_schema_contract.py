"""Task 5a — validate the response schema matches the FR-05 data contract."""
import jsonschema
import pytest

from tests.api.tests.schema import CONTRACT_FIELDS, FR05_SCHEMA, TEST_DATA

pytestmark = pytest.mark.api

SCHEMA_INPUTS = TEST_DATA["schema_inputs"]


def test_post_response_matches_fr05_schema(submitted):
    jsonschema.validate(submitted(), FR05_SCHEMA)  # raises on any mismatch


def test_get_latest_matches_fr05_schema(api, submitted):
    submitted()
    resp = api.get_latest()
    assert resp.status_code == 200
    jsonschema.validate(resp.json(), FR05_SCHEMA)


def test_response_has_exactly_the_contract_fields(submitted):
    assert set(submitted()) == CONTRACT_FIELDS


@pytest.mark.parametrize("text", SCHEMA_INPUTS)
def test_schema_holds_across_a_range_of_inputs(submitted, text):
    jsonschema.validate(submitted(text), FR05_SCHEMA)
