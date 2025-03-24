import os
import json
import pytest
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch


from src.parking_spaces.trailers_parking_spaces_granular_statistics import (
    load_json,
    process_events,
    calculate_granular_statistics,
    display_granular_statistics
)

@pytest.fixture
def sample_events():
    """
    Provide a fixture of sample events that reflect the JSON structure
    in events_granular_statistics.json. This can be adjusted to your own
    testing needs or to match your real data shape.
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
        }
    ]


def test_load_json(tmp_path):
    """
    Test that load_json correctly loads data from a valid JSON file.
    """
    test_file = tmp_path / "test.json"
    data_to_write = [{"key": "value"}, {"another_key": "another_value"}]

    # Write data to temporary file
    with open(test_file, "w") as f:
        json.dump(data_to_write, f)

    # Load using the function
    loaded_data = load_json(test_file)

    assert loaded_data == data_to_write, "Loaded data does not match the expected content."


def test_load_json_invalid_file_path():
    """
    Test that load_json raises an error for an invalid file path.
    """
    invalid_path = "non_existent_file.json"
    with pytest.raises(FileNotFoundError):
        load_json(invalid_path)


def test_process_events(sample_events):
    """
    Test process_events to ensure it calculates arrivals, departures, and durations.
    """
    yard_data = process_events(sample_events)

    # We expect to have 2 yards: y1 and y2
    assert set(yard_data.keys()) == {"y1", "y2"}, "Yard IDs do not match expected."

    # Check yard y1 stats
    assert yard_data["y1"]["arrivals"] == 2, "Expected 2 arrivals in yard y1."
    assert yard_data["y1"]["departures"] == 2, "Expected 2 departures in yard y1."

    # Check yard y2 stats
    assert yard_data["y2"]["arrivals"] == 1, "Expected 1 arrival in yard y2."
    assert yard_data["y2"]["departures"] == 1, "Expected 1 departure in yard y2."

    # Check trailer durations for yard y1
    t1_info = yard_data["y1"]["trailer_durations"]["t1"]
    t2_info = yard_data["y1"]["trailer_durations"]["t2"]
    assert t1_info["total_time"] == timedelta(hours=2), "Trailer t1 should have spent 2 hours in yard y1."
    assert t2_info["total_time"] == timedelta(minutes=30), "Trailer t2 should have spent 30 minutes in yard y1."


def test_calculate_granular_statistics(sample_events):
    """
    Test calculate_granular_statistics to ensure it produces the correct summary info.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_granular_statistics(yard_data)

    # We expect y1 and y2 in summaries
    assert set(yard_summaries.keys()) == {"y1", "y2"}, "Yard summaries do not match expected yard IDs."

    # Check total time for yard y1
    y1_summary = yard_summaries["y1"]
    expected_y1_total = timedelta(hours=2) + timedelta(minutes=30)  # 2:00 + 0:30 = 2:30
    assert y1_summary["total_time"] == expected_y1_total, "Incorrect total time for yard y1."

    # Check average time per trailer in y1
    # Two trailers (t1, t2) contributed durations of 2h and 0.5h => average 1h15m
    expected_avg_y1 = expected_y1_total / 2
    assert y1_summary["average_time_per_trailer"] == expected_avg_y1, "Incorrect average time for yard y1."

    # Check unique trailers for yard y1 (two: t1, t2)
    assert y1_summary["unique_trailers"] == 2, "Expected 2 unique trailers in yard y1."

    # Check the trailer with most time in y1
    assert y1_summary["most_time_trailer"] == "t1", "Trailer t1 should have the most time in yard y1."
    assert y1_summary["most_time_duration"] == timedelta(hours=2), "Trailer t1 duration should be 2 hours."

    # Check the trailer with least time in y1
    assert y1_summary["least_time_trailer"] == "t2", "Trailer t2 should have the least time in yard y1."
    assert y1_summary["least_time_duration"] == timedelta(minutes=30), "Trailer t2 duration should be 30 minutes."

    # Check trailer percentages
    t1_percentage = y1_summary["trailer_percentages"]["t1"]
    t2_percentage = y1_summary["trailer_percentages"]["t2"]
    # t1 = 2h, t2 = 0.5h => total 2.5h. t1 is 80%, t2 is 20%.
    assert pytest.approx(t1_percentage, 0.01) == 80.0, "Trailer t1 should be ~80% of total yard time."
    assert pytest.approx(t2_percentage, 0.01) == 20.0, "Trailer t2 should be ~20% of total yard time."

    # Check yard y2
    y2_summary = yard_summaries["y2"]
    expected_y2_total = timedelta(hours=1, minutes=30)  # from 15:00 to 16:30
    assert y2_summary["total_time"] == expected_y2_total, "Incorrect total time for yard y2."
    # Only one trailer (t3), so average time = total time.
    assert y2_summary["average_time_per_trailer"] == expected_y2_total, "Average time for yard y2 is incorrect."
    assert y2_summary["unique_trailers"] == 1, "Expected 1 unique trailer in yard y2."
    assert y2_summary["most_time_trailer"] == "t3", "t3 should have the most time in yard y2."
    assert y2_summary["least_time_trailer"] == "t3", "t3 should also have the least time in yard y2."
    # Percentage for t3 must be 100% if it’s the only trailer
    assert pytest.approx(list(y2_summary["trailer_percentages"].values())[0], 0.01) == 100.0, \
        "Single trailer t3 in yard y2 should have 100% yard utilization."


def test_display_granular_statistics(sample_events):
    """
    Test display_granular_statistics by capturing printed output and
    verifying that it contains the expected summary lines for each yard.
    """
    yard_data = process_events(sample_events)
    yard_summaries = calculate_granular_statistics(yard_data)

    # Patch stdout so we can capture the printed output
    with patch('sys.stdout', new=StringIO()) as fake_out:
        display_granular_statistics(yard_summaries)
        printed_output = fake_out.getvalue()

    assert "Yard y1 Summary:" in printed_output, "Yard y1 summary header not found in printed output."
    assert "Yard y2 Summary:" in printed_output, "Yard y2 summary header not found in printed output."
    assert "Total Time Spent by All Trailers:" in printed_output, "Missing 'Total Time' line."
    assert "Average Time Per Trailer:" in printed_output, "Missing 'Average Time' line."
    assert "Trailer with Most Time:" in printed_output, "Missing 'Most Time' line."
    assert "Trailer with Least Time:" in printed_output, "Missing 'Least Time' line."
    assert "Unique Trailers:" in printed_output, "Missing 'Unique Trailers' line."
    assert "Percentage of Yard Utilization by Each Trailer:" in printed_output, \
        "Missing 'Percentage of Yard Utilization' line."

    # Optionally, do more fine-grained checks on numeric values if needed.
