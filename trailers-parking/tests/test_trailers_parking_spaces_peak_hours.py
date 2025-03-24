import json
import pytest
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Import the methods we want to test
# Adjust the path as needed depending on your project layout
from src.parking_spaces.trailers_parking_spaces_peak_hours import (
    load_json,
    process_events,
    calculate_peak_hours
)


@pytest.fixture
def sample_events():
    """
    Returns a list of event dictionaries to simulate a small set of arrive/depart events.
    We’ll reuse this fixture for multiple tests.
    """
    return [
        {
            "event_id": "e1",
            "timestamp": "2024-01-01T12:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "arrived",
            "parking_space": "p1"
        },
        {
            "event_id": "e2",
            "timestamp": "2024-01-01T13:30:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "departed",
            "parking_space": "p1"
        },
        {
            "event_id": "e3",
            "timestamp": "2024-01-01T12:30:00",
            "yard_id": "y1",
            "trailer_id": "t2",
            "event_type": "arrived",
            "parking_space": "p2"
        },
        {
            "event_id": "e4",
            "timestamp": "2024-01-01T15:00:00",
            "yard_id": "y1",
            "trailer_id": "t2",
            "event_type": "departed",
            "parking_space": "p2"
        }
    ]


@pytest.fixture
def sample_json_file(tmp_path, sample_events):
    """
    Creates a temporary JSON file with sample event data for testing load_json().
    """
    test_file = tmp_path / "test_events.json"
    test_file.write_text(json.dumps(sample_events))
    return test_file


def test_load_json(sample_json_file):
    """
    Test the load_json function to ensure it properly loads JSON data from a file.
    """
    data = load_json(sample_json_file)
    assert len(data) == 4, "Should load exactly 4 events"
    assert data[0]["event_id"] == "e1", "First event should have event_id='e1'"


def test_process_events(sample_events):
    """
    Test process_events to ensure arrivals and departures are correctly recorded.
    """
    parking_utilization = process_events(sample_events)

    # We expect 2 parking spaces: 'p1' and 'p2'
    assert "p1" in parking_utilization
    assert "p2" in parking_utilization

    # Check that 'p1' has exactly 1 arrival/departure pair
    assert len(parking_utilization["p1"]) == 1
    p1_entry = parking_utilization["p1"][0]
    assert p1_entry["trailer_id"] == "t1"
    assert "arrival_time" in p1_entry
    assert "departure_time" in p1_entry

    # Check that 'p2' has exactly 1 arrival/departure pair
    assert len(parking_utilization["p2"]) == 1
    p2_entry = parking_utilization["p2"][0]
    assert p2_entry["trailer_id"] == "t2"
    assert "arrival_time" in p2_entry
    assert "departure_time" in p2_entry


def test_calculate_peak_hours(sample_events):
    """
    Test calculate_peak_hours to ensure correct peak utilization is found.
    """
    parking_utilization = process_events(sample_events)
    max_utilization, peak_hours = calculate_peak_hours(parking_utilization)

    # Based on sample data:
    #   t1 is in p1 from 12:00 -> 13:30
    #   t2 is in p2 from 12:30 -> 15:00
    # The hours from 12:00 - 13:00 have both t1 and t2
    # So max_utilization should be 2 during the 12:00 and 13:00 hours.

    assert max_utilization == 2, "Peak utilization should be 2 trailers"

    # Expect 12:00 and 13:00 hours in the peak_hours list
    # Check them in string form for clarity, or check via datetime objects:
    formatted_peak_hours = [h.strftime("%Y-%m-%d %H:%M:%S") for h in peak_hours]

    # We expect something like:
    #   2024-01-01 12:00:00
    #   2024-01-01 13:00:00
    assert any("2024-01-01 12:00:00" in ph for ph in formatted_peak_hours)
    assert any("2024-01-01 13:00:00" in ph for ph in formatted_peak_hours)

    # Optional: confirm only these two are in the peak hours
    assert len(peak_hours) == 2, "Should only have two distinct peak hours"


def test_calculate_peak_hours_no_data():
    """
    Test calculate_peak_hours when no events are provided (edge case).
    Should return a max utilization of 0 and an empty list of peak hours.
    """
    parking_utilization = {}
    max_utilization, peak_hours = calculate_peak_hours(parking_utilization)
    assert max_utilization == 0, "With no events, peak utilization should be 0"
    assert peak_hours == [], "No peak hours when there are no events"
