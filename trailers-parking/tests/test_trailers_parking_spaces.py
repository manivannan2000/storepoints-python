
import json
import pytest
import os
from datetime import datetime
from pathlib import Path
from src.parking_spaces.trailers_parking_spaces import (
    load_json,
    process_events,
    calculate_utilization,
    TrailerEvent,
    TrailerEventAnalyzer
)

# --------------------------------------------------
# 1. Test load_json
# --------------------------------------------------
def test_load_json(tmp_path):
    # Create sample data and write it to a temp JSON file
    sample_data = [
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
            "timestamp": "2024-01-01T13:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "departed",
            "parking_space": "p1"
        }
    ]
    test_file = tmp_path / "test_events.json"
    with open(test_file, "w") as f:
        json.dump(sample_data, f)

    # Call the function
    result = load_json(test_file)

    # Assertions
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["event_id"] == "e1"
    assert result[1]["event_type"] == "departed"

# --------------------------------------------------
# 2. Test process_events
# --------------------------------------------------
def test_process_events():
    # Sample in-memory list of events
    events = [
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
            "timestamp": "2024-01-01T13:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "departed",
            "parking_space": "p1"
        },
        {
            "event_id": "e3",
            "timestamp": "2024-01-01T15:00:00",
            "yard_id": "y2",
            "trailer_id": "t2",
            "event_type": "arrived",
            "parking_space": "p2"
        }
    ]

    yard_stats, parking_utilization = process_events(events)

    # Assertions for yard_stats
    assert yard_stats["y1"]["arrivals"] == 1
    assert yard_stats["y1"]["departures"] == 1
    assert yard_stats["y2"]["arrivals"] == 1
    assert yard_stats["y2"]["departures"] == 0  # no departure events in sample

    # Assertions for parking_utilization
    # p1 has 1 dict in its list
    assert len(parking_utilization["p1"]) == 1
    assert parking_utilization["p1"][0]["trailer_id"] == "t1"
    assert "departure_time" in parking_utilization["p1"][0]

    # p2 has 1 dict
    assert len(parking_utilization["p2"]) == 1
    assert parking_utilization["p2"][0]["trailer_id"] == "t2"
    assert "departure_time" not in parking_utilization["p2"][0]  # not yet departed

# --------------------------------------------------
# 3. Test calculate_utilization
# --------------------------------------------------
def test_calculate_utilization():
    # Build a fake parking_utilization dictionary in the same structure as process_events returns
    timestamp_arrival = datetime(2024, 1, 1, 12, 0, 0)
    timestamp_departure = datetime(2024, 1, 1, 15, 0, 0)

    parking_utilization = {
        "p1": [
            {
                "trailer_id": "t1",
                "arrival_time": timestamp_arrival,
                "departure_time": timestamp_departure
            }
        ],
        "p2": [
            {
                "trailer_id": "t2",
                "arrival_time": timestamp_arrival
                # no departure_time => still parked
            }
        ]
    }

    # Calculate utilization
    utilization_stats = calculate_utilization(parking_utilization)

    # For p1, 12:00 to 15:00 => 3 hours
    assert utilization_stats["p1"] == 3.0
    # For p2, there's no departure_time, so usage is 0
    assert utilization_stats["p2"] == 0.0

# --------------------------------------------------
# 4. Test the TrailerEvent class
# --------------------------------------------------
def test_trailer_event_valid_timestamp():
    event = TrailerEvent(
        event_id="e1",
        yard_id="y1",
        event_type="arrived",
        parking_space="p1",
        timestamp="2024-01-01T12:00:00",
        trailer_id="t1"
    )
    assert event.timestamp is not None
    assert event.timestamp.year == 2024
    assert event.event_type == "arrived"

def test_trailer_event_invalid_timestamp():
    # Provide an invalid timestamp to ensure it doesn't crash
    event = TrailerEvent(
        event_id="e2",
        yard_id="y1",
        event_type="arrived",
        parking_space="p1",
        timestamp="invalid-date-string",
        trailer_id="t1"
    )
    assert event.timestamp is None  # fallback as per class code
    assert event.event_id == "e2"

# --------------------------------------------------
# 5. Test the TrailerEventAnalyzer class
# --------------------------------------------------
@pytest.fixture
def sample_json_file(tmp_path):
    # Create a temporary JSON file for testing
    data = [
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
            "timestamp": "2024-01-01T13:00:00",
            "yard_id": "y1",
            "trailer_id": "t1",
            "event_type": "departed",
            "parking_space": "p1"
        },
        {
            "event_id": "e3",
            "timestamp": "2024-01-01T15:00:00",
            "yard_id": "y2",
            "trailer_id": "t2",
            "event_type": "arrived",
            "parking_space": "p2"
        }
    ]
    file_path = tmp_path / "events.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path

def test_trailer_event_analyzer_load_data(sample_json_file):
    analyzer = TrailerEventAnalyzer(str(sample_json_file))
    analyzer.load_data()

    # We expect 3 events loaded
    assert len(analyzer.events) == 3
    assert analyzer.events[0].event_id == "e1"
    assert analyzer.events[1].event_type == "departed"

def test_trailer_event_analyzer_get_yard_stats(sample_json_file):
    analyzer = TrailerEventAnalyzer(str(sample_json_file))
    analyzer.load_data()

    yard_stats = analyzer.get_yard_stats()
    # yard y1: 1 arrival, 1 departure
    assert yard_stats["y1"]["arrivals"] == 1
    assert yard_stats["y1"]["departures"] == 1
    # yard y2: 1 arrival, 0 departures
    assert yard_stats["y2"]["arrivals"] == 1
    assert yard_stats["y2"]["departures"] == 0

def test_trailer_event_analyzer_get_parking_departure(sample_json_file):
    analyzer = TrailerEventAnalyzer(str(sample_json_file))
    analyzer.load_data()
    park_departures = analyzer.get_parking_departure()
    # p1 should have an arrival_time and a departure_time
    assert len(park_departures["p1"]) == 1
    assert "arrival_time" in park_departures["p1"][0]
    assert "departure_time" in park_departures["p1"][0]
    # p2 only has an arrival, no departure
    assert len(park_departures["p2"]) == 1
    assert "departure_time" not in park_departures["p2"][0]

def test_trailer_event_analyzer_get_utilization_stats(sample_json_file):
    analyzer = TrailerEventAnalyzer(str(sample_json_file))
    analyzer.load_data()
    stats = analyzer.get_utilization_stats()
    # p1: arrived at 12:00, departed at 13:00 => 1 hour
    assert stats["p1"] == 1
    # p2: arrived at 15:00, no departure => 0 hours
    assert stats["p2"] == 0
