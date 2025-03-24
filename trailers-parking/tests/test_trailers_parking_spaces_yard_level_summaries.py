import pytest
import os
import json
import tempfile
from datetime import datetime
from collections import defaultdict

# Import the functions from your src/ module.
# Adjust the import path if your project structure differs.
from src.parking_spaces.trailers_parking_spaces_yard_level_summaries import (
    load_json,
    process_events,
    calculate_yard_summaries,
    display_yard_summaries
)

@pytest.fixture
def sample_events():
    """
    Returns a list of sample event dicts similar to what might appear
    in events_yard_summaries.json.
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
            "timestamp": "2024-01-01T14:00:00",
            "yard_id": "y1",
            "trailer_id": "t2",
            "event_type": "departed",
            "parking_space": "p2"
        },
        {
            "event_id": "e5",
            "timestamp": "2024-01-01T15:00:00",
            "yard_id": "y2",
            "trailer_id": "t3",
            "event_type": "arrived",
            "parking_space": "p3"
        },
        {
            "event_id": "e6",
            "timestamp": "2024-01-01T16:30:00",
            "yard_id": "y2",
            "trailer_id": "t3",
            "event_type": "departed",
            "parking_space": "p3"
        }
    ]


def test_load_json(sample_events):
    """
    Test the load_json function by creating a temporary JSON file, then
    checking if load_json reads it correctly.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
        json.dump(sample_events, tmp_file)
        tmp_file_path = tmp_file.name

    try:
        loaded_data = load_json(tmp_file_path)
        assert len(loaded_data) == len(sample_events), "Loaded data length mismatch."
        assert loaded_data[0]["event_id"] == "e1", "First event ID should be e1."
    finally:
        # Clean up the temp file
        os.remove(tmp_file_path)


def test_process_events(sample_events):
    """
    Test process_events to ensure it correctly aggregates arrivals, departures,
    and parking utilization by yard.
    """
    yard_data = process_events(sample_events)

    # Check for yard 'y1'
    assert "y1" in yard_data, "y1 should be in yard_data."
    assert yard_data["y1"]["arrivals"] == 2, "There should be 2 arrivals in y1."
    assert yard_data["y1"]["departures"] == 2, "There should be 2 departures in y1."

    # Check for yard 'y2'
    assert "y2" in yard_data, "y2 should be in yard_data."
    assert yard_data["y2"]["arrivals"] == 1, "There should be 1 arrival in y2."
    assert yard_data["y2"]["departures"] == 1, "There should be 1 departure in y2."

    # Check parking utilization
    y1_p1_usage = yard_data["y1"]["parking_utilization"]["p1"]
    assert len(y1_p1_usage) == 1, "p1 in y1 should have 1 usage entry."
    assert y1_p1_usage[0]["trailer_id"] == "t1", "Trailer ID for p1 usage should be t1."

    # Ensure departure_time is set for the departed trailer
    assert "departure_time" in y1_p1_usage[0], "Trailer t1 departure_time should be recorded."


def test_calculate_yard_summaries(sample_events):
    """
    Test calculate_yard_summaries to ensure it correctly computes the
    peak utilization and corresponding peak hours.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_yard_summaries(yard_data)

    assert "y1" in yard_summaries, "y1 should be in yard_summaries."
    y1_summary = yard_summaries["y1"]
    assert y1_summary["total_arrivals"] == 2, "y1 should have 2 total arrivals."
    assert y1_summary["total_departures"] == 2, "y1 should have 2 total departures."
    assert y1_summary["peak_utilization"] == 2, "Peak utilization for y1 should be 2."

    # For y1, the trailers overlap around 12:30 - 13:00 or so
    # The peak hours might reflect that overlap. This test checks that at least
    # some hour in that range is captured.
    assert len(y1_summary["peak_hours"]) >= 1, "y1 should have at least one peak hour."

    # Check y2
    y2_summary = yard_summaries["y2"]
    assert y2_summary["total_arrivals"] == 1, "y2 should have 1 total arrival."
    assert y2_summary["total_departures"] == 1, "y2 should have 1 total departure."
    assert y2_summary["peak_utilization"] == 1, "Peak utilization for y2 should be 1."
    assert len(y2_summary["peak_hours"]) >= 1, "y2 should have at least one peak hour."


def test_display_yard_summaries(capfd, sample_events):
    """
    Test display_yard_summaries by capturing the stdout output and verifying
    expected yard summary lines appear.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_yard_summaries(yard_data)

    # Capture printed output
    display_yard_summaries(yard_summaries)
    captured = capfd.readouterr()
    output = captured.out

    assert "Yard y1 Summary:" in output, "Output should contain summary for y1."
    assert "Total Arrivals: 2" in output, "Output should show 2 arrivals for y1."
    assert "Total Departures: 2" in output, "Output should show 2 departures for y1."
    assert "Peak Utilization: 2 trailers" in output, "Output should show peak utilization=2 for y1."

    assert "Yard y2 Summary:" in output, "Output should contain summary for y2."
    assert "Total Arrivals: 1" in output, "Output should show 1 arrival for y2."
    assert "Total Departures: 1" in output, "Output should show 1 departure for y2."
    assert "Peak Utilization: 1 trailers" in output, "Output should show peak utilization=1 for y2."
