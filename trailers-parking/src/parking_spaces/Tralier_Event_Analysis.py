import json
from datetime import datetime
from typing import List, Dict, Any


class TrailerEvent:
    """
    Represents a single trailer event in the yard.
    For example, an event might be a trailer arriving or departing,
    or a loading/unloading action, etc.
    """

    def __init__(
            self,
            event_id: str,
            yard_id: str,
            event_type: str,
            timestamp: str,
            trailer_id: str
    ):
        self.event_id = event_id
        self.yard_id = yard_id
        self.event_type = event_type
        self.timestamp_str = timestamp
        self.trailer_id = trailer_id

        # Attempt to parse the timestamp into a datetime object
        # for easier comparison, grouping, etc.
        try:
            self.timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            self.timestamp = None

    def __repr__(self) -> str:
        return (
            f"TrailerEvent(event_id={self.event_id}, "
            f"yard_id={self.yard_id}, event_type={self.event_type}, "
            f"timestamp={self.timestamp_str}, trailer_id={self.trailer_id})"
        )


class TrailerEventAnalyzer:
    """
    Provides functionality to load event data from a JSON file
    and extract various insights.
    """

    def __init__(self, filepath: str):
        """
        Initialize the analyzer with a path to the JSON data file.
        """
        self.filepath = filepath
        self.events: List[TrailerEvent] = []

    def load_data(self) -> None:
        """
        Loads the event data from the specified JSON file
        and populates a list of TrailerEvent objects.
        """
        with open(self.filepath, 'r') as file:
            data = json.load(file)  # Expecting a list of event records in JSON

        # Parse each JSON record into a TrailerEvent object
        self.events = [
            TrailerEvent(
                event_id=record["event_id"],
                yard_id=record["yard_id"],
                event_type=record["event_type"],
                timestamp=record["timestamp"],
                trailer_id=record["trailer_id"]
            )
            for record in data
        ]

    def get_event_count_by_yard(self) -> Dict[str, int]:
        """
        Returns a dictionary mapping each yard_id to its count of events.
        """
        yard_counts: Dict[str, int] = {}
        for event in self.events:
            yard_counts[event.yard_id] = yard_counts.get(event.yard_id, 0) + 1
        return yard_counts

    def get_most_frequent_event_type(self) -> str:
        """
        Returns the most common event type across all yards.
        If there are no events, returns an empty string.
        """
        if not self.events:
            return ""
        event_type_counts: Dict[str, int] = {}
        for event in self.events:
            event_type_counts[event.event_type] = (
                    event_type_counts.get(event.event_type, 0) + 1
            )
        # Find the event type with the maximum count
        return max(event_type_counts, key=event_type_counts.get)

    def get_event_distribution_for_yard(self, yard_id: str) -> Dict[str, int]:
        """
        Returns a dictionary of event_type -> count for the specified yard.
        """
        distribution: Dict[str, int] = {}
        for event in self.events:
            if event.yard_id == yard_id:
                distribution[event.event_type] = (
                        distribution.get(event.event_type, 0) + 1
                )
        return distribution

    def get_average_events_per_day(self, yard_id: str) -> float:
        """
        Calculates the average number of events per day for a given yard.
        Simplified approach:
          - finds the earliest and latest event timestamps for that yard,
          - calculates the total days in that range,
          - divides the total event count by days.

        Returns 0.0 if no events or if time range is invalid.
        """
        yard_events = [e for e in self.events if e.yard_id == yard_id]
        if not yard_events:
            return 0.0

        valid_events = [e for e in yard_events if e.timestamp is not None]
        if not valid_events:
            return 0.0

        # Sort events by timestamp
        valid_events.sort(key=lambda x: x.timestamp)
        start_time = valid_events[0].timestamp
        end_time = valid_events[-1].timestamp

        # Calculate total days in range
        days_diff = (end_time - start_time).days
        # If there's 0 days difference, avoid division by zero
        # and assume at least 1 day (this logic can differ by use case)
        days_diff = max(days_diff, 1)

        # Average events per day
        return len(valid_events) / days_diff

    def get_events_in_timerange(self, start: datetime, end: datetime) -> List[TrailerEvent]:
        """
        Returns all events occurring within the specified [start, end] datetime range.
        """
        return [
            event
            for event in self.events
            if event.timestamp is not None and start <= event.timestamp <= end
        ]


def main():
    # Example usage:

    # 1. Initialize the analyzer with a JSON file path
    analyzer = TrailerEventAnalyzer(filepath="../data_set/events_TrailerEventAnalyzer.json")

    # 2. Load the data
    analyzer.load_data()

    # 3. Get the event count by yard
    yard_counts = analyzer.get_event_count_by_yard()
    print("Event count by yard:", yard_counts)

    # 4. Get the most frequent event type
    most_common_event = analyzer.get_most_frequent_event_type()
    print("Most frequent event type:", most_common_event)

    # 5. Distribution of event types for a specific yard
    some_yard_id = "YARD-001"
    distribution = analyzer.get_event_distribution_for_yard(some_yard_id)
    print(f"Event distribution for {some_yard_id}:", distribution)

    # 6. Average events per day for a specific yard
    avg_events_per_day = analyzer.get_average_events_per_day(some_yard_id)
    print(f"Average events per day for {some_yard_id}:", avg_events_per_day)

    # 7. Events in a custom time range
    start_dt = datetime(2025, 1, 1)
    end_dt = datetime(2025, 1, 31)
    events_in_january = analyzer.get_events_in_timerange(start_dt, end_dt)
    print("Events in January:", events_in_january)


if __name__ == "__main__":
    main()
