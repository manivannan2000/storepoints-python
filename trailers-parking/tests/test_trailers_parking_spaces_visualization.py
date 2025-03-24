import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.parking_spaces.trailers_parking_spaces_visualization import (
    load_json,
    process_events,
    calculate_granular_statistics,
    visualize_statistics,
)

@pytest.fixture
def sample_events():
    """
    Provide a small set of sample events in JSON-like structure for tests.
    You can also load them from a file under tests/data if desired.
    """
    return [
        {
            "event_id": "e1",
            "timestamp": "2024-01-01T12:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "arrived",
        },
        {
            "event_id": "e2",
            "timestamp": "2024-01-01T14:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "departed",
        },
        {
            "event_id": "e3",
            "timestamp": "2024-01-01T13:00:00",
            "yard_id": "y1",
            "trailer_id": "t2",
            "event_type": "arrived",
        },
        {
            "event_id": "e4",
            "timestamp": "2024-01-01T13:30:00",
            "yard_id": "y1",
            "trailer_id": "t2",
            "event_type": "departed",
        },
        {
            "event_id": "e5",
            "timestamp": "2024-01-01T15:00:00",
            "yard_id": "y2",
            "trailer_id": "t3",
            "event_type": "arrived",
        },
        {
            "event_id": "e6",
            "timestamp": "2024-01-01T16:30:00",
            "yard_id": "y2",
            "trailer_id": "t3",
            "event_type": "departed",
        }
    ]

def test_load_json(tmp_path):
    """
    Test load_json by creating a temporary JSON file and verifying
    if the data loads correctly.
    """
    test_file = tmp_path / "test_events.json"
    sample_data = [{"event_id": "e1", "timestamp": "2024-01-01T12:00:00"}]
    with open(test_file, "w") as f:
        json.dump(sample_data, f)

    loaded_data = load_json(str(test_file))
    assert loaded_data == sample_data, "load_json should return the correct data from file."

def test_process_events(sample_events):
    """
    Test process_events by verifying that the returned structure
    correctly includes yards, arrivals/departures, and durations.
    """
    yard_data = process_events(sample_events)
    assert "y1" in yard_data
    assert "y2" in yard_data

    # Check arrivals/departures count
    assert yard_data["y1"]["arrivals"] == 2, "There should be 2 arrivals in y1."
    assert yard_data["y1"]["departures"] == 2, "There should be 2 departures in y1."
    assert yard_data["y2"]["arrivals"] == 1, "There should be 1 arrival in y2."
    assert yard_data["y2"]["departures"] == 1, "There should be 1 departure in y2."

    # Check trailer_durations structure
    t1_info = yard_data["y1"]["trailer_durations"]["t1"]
    assert isinstance(t1_info["total_time"], timedelta), "Trailer total_time should be a timedelta object."
    assert t1_info["arrival_time"] is None, "After processing, arrival_time should be reset to None if departed."

def test_calculate_granular_statistics(sample_events):
    """
    Test calculate_granular_statistics by verifying the total time
    and trailer percentages are correctly computed.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_granular_statistics(yard_data)

    # Check that y1 has the correct total time for t1 (2 hours) and t2 (0.5 hours).
    # Combined total: 2.5 hours => 9000 seconds
    y1_summary = yard_summaries["y1"]
    assert abs(y1_summary["total_time"].total_seconds() - 9000) < 1e-6, "Total time for y1 should be ~9000 seconds."

    # Trailer percentages:
    # t1: 2 hours out of 2.5 => 80%
    # t2: 0.5 hours out of 2.5 => 20%
    t1_percent = y1_summary["trailer_percentages"].get("t1", 0)
    t2_percent = y1_summary["trailer_percentages"].get("t2", 0)

    assert 79.9 < t1_percent < 80.1, "t1 should be ~80% of y1 total time."
    assert 19.9 < t2_percent < 20.1, "t2 should be ~20% of y1 total time."

    # Check y2 total time (1.5 hours => 5400 seconds)
    y2_summary = yard_summaries["y2"]
    assert abs(y2_summary["total_time"].total_seconds() - 5400) < 1e-6, "Total time for y2 should be ~5400 seconds."

    # Trailer percentages for y2: t3 should be 100%
    t3_percent = y2_summary["trailer_percentages"].get("t3", 0)
    assert 99.9 < t3_percent < 100.1, "t3 should be ~100% of y2 total time."

@patch("matplotlib.pyplot.show")
def test_visualize_statistics(mock_show, sample_events):
    """
    Test visualize_statistics by verifying that no errors are raised
    during plotting. We patch `plt.show()` to avoid displaying actual plots.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_granular_statistics(yard_data)

    # We just want to ensure it runs without error.
    try:
        visualize_statistics(yard_summaries)
    except Exception as e:
        pytest.fail(f"visualize_statistics raised an exception: {e}")

    # Assert that plt.show() was called (once for bar chart, plus once per yard with data)
    # y1 has trailer_percentages, y2 has trailer_percentages => total 1 bar chart + 2 pie charts => 3 calls
    assert mock_show.call_count == 3, "Expected 3 calls to plt.show() (1 for bar chart + 2 pie charts)."
