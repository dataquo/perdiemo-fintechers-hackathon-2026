from copy import deepcopy
from conftest import example
from perdiemo_mcp.schema import validate_request


def test_official_schema_example():
    r = validate_request(example())
    assert r["ok"] is True
    assert r["payload"]["trips"][0]["itinerar"][0]["typ"] == "ODJEZD"
    assert r["payload"]["trips"][0]["bezplatna_strava"] == {"2025-06-11": ["snidane"]}


def test_missing_departure_time_does_not_guess():
    r = example()
    del r["trips"][0]["itinerar"][0]["datum"]
    checked = validate_request(r)
    assert checked["ok"] is False
    assert any("datum" in i["path"] for i in checked["error"]["issues"])


def test_matching_candidate_is_not_native_api_input():
    result = validate_request({"year": 2026, "trips": [{"candidate_trip_id": "a"}]})
    assert result["ok"] is False


def test_invalid_meal_label():
    r = example()
    r["trips"][0]["bezplatna_strava"] = {"2025-06-11": ["free_dinner"]}
    assert validate_request(r)["ok"] is False


def test_no_extra_matching_metadata_leaks_to_backend():
    r = example()
    r["trips"][0]["matched_transaction_ids"] = ["txn-1"]
    assert validate_request(r)["ok"] is False


def test_unsorted_trip_events_rejected():
    r = example()
    r["trips"][0]["itinerar"][0], r["trips"][0]["itinerar"][1] = (
        r["trips"][0]["itinerar"][1], r["trips"][0]["itinerar"][0]
    )
    assert validate_request(r)["ok"] is False


def test_duplicate_trip_ids_rejected():
    r = example()
    r["trips"].append(deepcopy(r["trips"][0]))
    assert validate_request(r)["ok"] is False


def test_invalid_date_and_negative_mileage_rejected():
    r = example()
    r["trips"][0]["itinerar"][0]["datum"] = "2025-02-30T07:00"
    r["trips"][0]["itinerar"][0]["vzdalenost_km"] = -2
    assert validate_request(r)["ok"] is False
