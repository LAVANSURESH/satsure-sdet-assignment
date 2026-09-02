"""Task 5b — verify correct data types (boolean completed, timestamp format, ...)."""
import pytest

from tests.api.tests.schema import TEST_DATA, parse_timestamp

pytestmark = pytest.mark.api

SESSION_USER = TEST_DATA["session_user"]
EXPLICIT_IST = TEST_DATA["timestamps"]["explicit_ist"]


def test_completed_is_a_native_boolean_true(submitted):
    body = submitted()
    assert type(body["completed"]) is bool  # not the string "true"
    assert body["completed"] is True


def test_account_fields_have_the_right_types_and_values(submitted):
    body = submitted()
    assert isinstance(body["account_id"], (str, int))
    assert str(body["account_id"]).strip() != ""
    assert isinstance(body["account_email"], str)
    assert body["account_email"] == SESSION_USER["account_email"]


def test_text_and_suggestion_list_are_strings(submitted):
    body = submitted("agile methodology")
    assert isinstance(body["text"], str)
    assert isinstance(body["suggestion_list"], str)


def test_timestamps_parse_and_are_timezone_aware(submitted):
    body = submitted()
    start = parse_timestamp(body["start_date"])
    end = parse_timestamp(body["end_date"])
    assert start.tzinfo is not None
    assert end.tzinfo is not None
    assert end >= start


def test_server_preserves_an_explicit_ist_offset(api):
    body = api.submit(
        "agile methodology",
        start_date=EXPLICIT_IST["start"],
        end_date=EXPLICIT_IST["end"],
    ).json()
    assert body["start_date"].endswith("+05:30")
    assert parse_timestamp(body["start_date"]).utcoffset().total_seconds() == 5.5 * 3600
