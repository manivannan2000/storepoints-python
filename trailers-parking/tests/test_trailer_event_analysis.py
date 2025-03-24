import json
from datetime import datetime
import pytest
from pathlib import Path

from src.parking_spaces.Tralier_Event_Analysis import TrailerEventAnalyzer


@pytest.fixture
def sample_data():
    # Provide a small set of events for testing
    return [
        {
            "event_id": "E1001",
            "yard_id": "YARD-001",
            "event_type": "LOAD",
            "timestamp": "2025-01-01T08:30:00",
            "trailer_id": "TRAILER-1001"
        },
        {
            "event_id": "E1002",
            "yard_id": "YARD-001",
            "event_type": "UNLOAD",
            "timestamp": "2025-01-02T09:15:00",
            "trailer_id": "TRAILER-1002"
        },
        {
            "event_id": "E1003",
            "yard_id": "YARD-002",
            "event_type": "ENTER",
            "timestamp": "2025-01-03T10:00:00",
            "trailer_id": "TRAILER-1003"
        },
        {
            "event_id": "E1004",
            "yard_id": "YARD-002",
            "event_type": "LOAD",
            "timestamp": "2025-01-04T11:00:00",
            "trailer_id": "TRAILER-1004"
        },
    ]


@pytest.fixture
def json_file_path(tmp_path, sample_data):
    # Create a temporary JSON file for testing
    test_file = tmp_path / "test_events.json"
    with open(test_file, "w") as f:
        json.dump(sample_data, f)
    return test_file


def test_load_data(json_file_path, sample_data):
    analyzer = TrailerEventAnalyzer(filepath=str(json_file_path))
    analyzer.load_data()

    # Ensure the events are loaded
    assert len(analyzer.events) == len(sample_data), "Loaded events count mismatch"

    # Check a sample event's attributes
    first_event = analyzer.events[0]
    assert first_event.event_id == sample_data[0]["event_id"]
    assert first_event.yard_id == sample_data[0]["yard_id"]
    assert first_event.event_type == sample_data[0]["event_type"]


def test_get_event_count_by_yard(json_file_path):
    analyzer = TrailerEventAnalyzer(filepath=str(json_file_path))
    analyzer.load_data()

    counts = analyzer.get_event_count_by_yard()
    # Expecting 2 events for YARD-001, 2 for YARD-002
    assert counts["YARD-001"] == 2
    assert counts["YARD-002"] == 2


def test_get_most_frequent_event_type(json_file_path):
    analyzer = TrailerEventAnalyzer(filepath=str(json_file_path))
    analyzer.load_data()

    # In our sample, LOAD appears twice, UNLOAD and ENTER appear once each
    assert analyzer.get_most_frequent_event_type() == "LOAD"


def test_get_event_distribution_for_yard(json_file_path):
    analyzer = TrailerEventAnalyzer(filepath=str(json_file_path))
    analyzer.load_data()

    # Distribution for YARD-001 => {LOAD: 1, UNLOAD: 1}
    dist_yard_001 = analyzer.get_event_distribution_for_yard("YARD-001")
    assert dist_yard_001["LOAD"] == 1
    assert dist_yard_001["UNLOAD"] == 1

    # Distribution for YARD-002 => {ENTER: 1, LOAD: 1}
    dist_yard_002 = analyzer.get_event_distribution_for_yard("YARD-002")
    assert dist_yard_002["ENTER"] == 1
    assert dist_yard_002["LOAD"] == 1


def test_get_average_events_per_day(json_file_path):
    analyzer = TrailerEventAnalyzer(filepath=str(json_file_path))
    analyzer.load_data()

    # For YARD-001, earliest timestamp is 2025-01-01, latest is 2025-01-02
    # That's technically 1 day difference, but we clamp to at least 1 day.
    # There are 2 events in that yard, so average = 2 events / 1 day = 2.0
    average_001 = analyzer.get_average_events_per_day("YARD-001")
    assert average_001 == 2.0

    # For YARD-002, from 2025-01-03 to 2025-01-04 => 1 day difference
    # 2 events / 1 day => 2.0
    average_002 = analyzer.get_average_events_per_day("YARD-002")
    assert average_002 == 2.0


def test_get_events_in_timerange(json_file_path):
    analyzer = TrailerEventAnalyzer(filepath=str(json_file_path))
    analyzer.load_data()

    start_dt = datetime(2025, 1, 1, 0, 0, 0)
    end_dt = datetime(2025, 1, 2, 23, 59, 59)

    events_jan_1_to_2 = analyzer.get_events_in_timerange(start_dt, end_dt)
    # Expect the first two events only: 2025-01-01T08:30:00 and 2025-01-02T09:15:00
    assert len(events_jan_1_to_2) == 2
    assert all(e.yard_id == "YARD-001" for e in events_jan_1_to_2)
