import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from io import StringIO

# Assuming your code is in src/trailers_parking_spaces_time_summaries.py
from src.parking_spaces.trailers_parking_spaces_time_summaries import (
    load_json,
    process_events,
    calculate_trailer_time_summaries,
    display_trailer_time_summaries,
)

@pytest.fixture
def sample_events():
    """
    Returns a list of sample events that simulates
    'arrived' and 'departed' usage for multiple yards and trailers.
    """
    return [
        {
            "event_id": "e1",
            "timestamp": "2024-01-01T12:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "arrived"
        },
        {
            "event_id": "e2",
            "timestamp": "2024-01-01T14:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "departed"
        },
        {
            "event_id": "e3",
            "timestamp": "2024-01-01T13:00:00",
            "yard_id": "y1",
            "trailer_id": "t2",
            "event_type": "arrived"
        },
        {
            "event_id": "e4",
            "timestamp": "2024-01-01T13:30:00",
            "yard_id": "y1",
            "trailer_id": "t2",
            "event_type": "departed"
        },
        {
            "event_id": "e5",
            "timestamp": "2024-01-01T15:00:00",
            "yard_id": "y2",
            "trailer_id": "t3",
            "event_type": "arrived"
        },
        {
            "event_id": "e6",
            "timestamp": "2024-01-01T16:30:00",
            "yard_id": "y2",
            "trailer_id": "t3",
            "event_type": "departed"
        },
    ]


def test_load_json(tmp_path):
    """
    Test the load_json function to ensure it correctly loads JSON data from a file.
    """
    # Create a temporary JSON file
    test_file = tmp_path / "test_events.json"
    data_to_write = [
        {"event_id": "e1", "timestamp": "2024-01-01T12:00:00", "yard_id": "y1", "trailer_id": "t1", "event_type": "arrived"}
    ]
    with open(test_file, "w") as f:
        json.dump(data_to_write, f)

    # Test loading the JSON data
    loaded_data = load_json(test_file)
    assert len(loaded_data) == 1
    assert loaded_data[0]["event_id"] == "e1"
    assert loaded_data[0]["timestamp"] == "2024-01-01T12:00:00"
    assert loaded_data[0]["yard_id"] == "y1"
    assert loaded_data[0]["trailer_id"] == "t1"
    assert loaded_data[0]["event_type"] == "arrived"


def test_process_events(sample_events):
    """
    Test process_events to check if arrivals and departures are counted properly
    and trailer durations are recorded accurately.
    """
    yard_data = process_events(sample_events)

    # Check yard y1 data
    assert yard_data["y1"]["arrivals"] == 2   # t1 arrived once, t2 arrived once
    assert yard_data["y1"]["departures"] == 2 # t1 departed once, t2 departed once
    assert "t1" in yard_data["y1"]["trailer_durations"]
    assert "t2" in yard_data["y1"]["trailer_durations"]

    # Check that total_time was set for t1
    t1_data = yard_data["y1"]["trailer_durations"]["t1"]
    assert "total_time" in t1_data
    # Duration for t1: 14:00 - 12:00 = 2 hours
    assert t1_data["total_time"] == timedelta(hours=2)

    # Check yard y2 data
    assert yard_data["y2"]["arrivals"] == 1
    assert yard_data["y2"]["departures"] == 1
    t3_data = yard_data["y2"]["trailer_durations"]["t3"]
    # Duration for t3: 16:30 - 15:00 = 1 hour 30 minutes
    assert t3_data["total_time"] == timedelta(hours=1, minutes=30)


def test_calculate_trailer_time_summaries(sample_events):
    """
    Test the calculation of most/least time spent by trailers in each yard.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_trailer_time_summaries(yard_data)

    # y1 should have t1 as the "most_time_trailer" (2 hours)
    # and t2 as the "least_time_trailer" (30 minutes)
    y1_summary = yard_summaries["y1"]
    assert y1_summary["most_time_trailer"] == "t1"
    assert y1_summary["most_time_duration"] == timedelta(hours=2)
    assert y1_summary["least_time_trailer"] == "t2"
    assert y1_summary["least_time_duration"] == timedelta(minutes=30)

    # y2 should have only t3
    y2_summary = yard_summaries["y2"]
    assert y2_summary["most_time_trailer"] == "t3"
    assert y2_summary["most_time_duration"] == timedelta(hours=1, minutes=30)
    assert y2_summary["least_time_trailer"] == "t3"
    assert y2_summary["least_time_duration"] == timedelta(hours=1, minutes=30)


def test_calculate_trailer_time_summaries_no_data():
    """
    Test the function when there is no trailer data for a yard,
    ensuring the result sets trailer IDs to None and durations to 0.
    """
    # yard_data with a single empty yard
    yard_data = {
        "y1": {
            "arrivals": 0,
            "departures": 0,
            "trailer_durations": {}
        }
    }
    yard_summaries = calculate_trailer_time_summaries(yard_data)
    summary = yard_summaries["y1"]

    assert summary["most_time_trailer"] is None
    assert summary["least_time_trailer"] is None
    assert summary["most_time_duration"] == timedelta(0)
    assert summary["least_time_duration"] == timedelta(0)


def test_display_trailer_time_summaries(sample_events, capsys):
    """
    Test that display_trailer_time_summaries prints the expected output.
    Use pytest's capsys fixture to capture stdout.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_trailer_time_summaries(yard_data)

    display_trailer_time_summaries(yard_summaries)
    captured = capsys.readouterr()

    # Basic checks to ensure key info is printed
    assert "Yard y1 Summary:" in captured.out
    assert "Trailer with Most Time: t1 (2:00:00)" in captured.out
    assert "Trailer with Least Time: t2 (0:30:00)" in captured.out

    assert "Yard y2 Summary:" in captured.out
    assert "Trailer with Most Time: t3 (1:30:00)" in captured.out
    assert "Trailer with Least Time: t3 (1:30:00)" in captured.out
