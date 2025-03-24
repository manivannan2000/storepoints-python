'''

Here’s a generic solution to process and extract insights from a JSON dataset of events related to parking
spaces for trailers. This solution includes steps for reading the JSON file, processing the data, and extracting
specific insights.

Solution Outline
Read the JSON File:

Parse the JSON file into a Python dictionary or list for processing.
Understand the Dataset: events.json file.

Extract Insights:

Calculate metrics such as:
Number of trailers arriving and departing per yard.
Parking space utilization.
Average time trailers spend in parking spaces.
Identify busy hours or yards.

Explanation of the Code
Load JSON Data:

The load_json function reads the events from a JSON file.
Process Events:

Events are iterated to count arrivals and departures by yard.
Parking space utilization is tracked by storing arrival and departure times for trailers.
Calculate Utilization:

For each parking space, the total time trailers spent in it is calculated by summing up durations
between arrival and departure.

Display Results:

Summarizes the number of arrivals and departures for each yard and the total usage time for each parking space.

Customization
You can modify this code to calculate additional insights such as:

Peak utilization hours.
Yard-level summaries.
Trailers spending the most/least time in a yard.

'''


import json
from datetime import datetime
from collections import defaultdict
from typing import List, DefaultDict, Any

# Step 1: Load the JSON dataset
def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Step 2: Process events to extract insights
def process_events(events):
    # Metrics
    yard_stats = defaultdict(lambda: {"arrivals": 0, "departures": 0})
    parking_utilization = defaultdict(list)  # {parking_space: [(arrival_time, departure_time)]}

    for event in events:
        yard_id = event["yard_id"]
        event_type = event["event_type"]
        parking_space = event["parking_space"]
        trailer_id = event["trailer_id"]
        timestamp = datetime.fromisoformat(event["timestamp"])

        # Count arrivals and departures by yard
        if event_type == "arrived":
            yard_stats[yard_id]["arrivals"] += 1
            parking_utilization[parking_space].append({"trailer_id": trailer_id, "arrival_time": timestamp})
        elif event_type == "departed":
            yard_stats[yard_id]["departures"] += 1
            # Match departure with previous arrival for the same trailer
            for entry in parking_utilization[parking_space]:
                if entry["trailer_id"] == trailer_id and "departure_time" not in entry:
                    entry["departure_time"] = timestamp
                    break

    return yard_stats, parking_utilization

# Step 3: Calculate additional insights
def calculate_utilization(parking_utilization):
    utilization_stats = {}
    for parking_space, usage in parking_utilization.items():
        total_time = 0
        for entry in usage:
            if "departure_time" in entry:
                duration = (entry["departure_time"] - entry["arrival_time"]).total_seconds() / 3600  # Hours
                total_time += duration
        utilization_stats[parking_space] = total_time
    return utilization_stats

# Step 4: Display results
def display_results(yard_stats, utilization_stats):
    print("Yard Stats:")
    for yard, stats in yard_stats.items():
        print(f"Yard {yard}: Arrivals: {stats['arrivals']}, Departures: {stats['departures']}")

    print("\nParking Utilization:")
    for parking_space, total_time in utilization_stats.items():
        print(f"Parking Space {parking_space}: Total Usage Time: {total_time:.2f} hours")


class TrailerEvent:
    """
    represents a single Trailer event in the park
    """
    def __init__(self,
                 event_id: str,
                 yard_id: str,
                 event_type: str,
                 parking_space: str,
                 timestamp: str,
                 trailer_id: str
                 ):
        self.event_id = event_id
        self.yard_id = yard_id
        self.event_type = event_type
        self.parking_space = parking_space
        self.trailer_id = trailer_id

        try:
            self.timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            self.timestamp = None

class TrailerEventAnalyzer:

    def __init__(self, filepath: str):
        """
        Initialize the analyzer with data file path
        """
        self.filepath = filepath
        self.events: List[TrailerEvent] = []

    def load_data(self) -> None:
        with open(self.filepath, 'r') as file:
            data = json.load(file)

        self.events = [
            TrailerEvent(
                event_id=record["event_id"],
                yard_id=record["yard_id"],
                event_type=record["event_type"],
                parking_space=record["parking_space"],
                timestamp=record["timestamp"],
                trailer_id=record["trailer_id"]
            )
            for record in data
        ]

    def get_yard_stats(self) -> DefaultDict[str, int]:
        yard_statistics2: DefaultDict[str, int] = defaultdict(lambda: {"arrivals": 0, "departures": 0})

        for event in self.events:
            if event.event_type == 'arrived':
                yard_statistics2[event.yard_id]["arrivals"] += 1
            elif event.event_type == 'departed':
                yard_statistics2[event.yard_id]["departures"] += 1

        return yard_statistics2

    def get_parking_departure(self) -> DefaultDict[str, list]:
        park_util: DefaultDict[str, list] = defaultdict(list)

        for event in self.events:
            if event.event_type == "arrived":
                park_util[event.parking_space].append(
                {"trailer_id": event.trailer_id, "arrival_time": event.timestamp})
            elif event.event_type == "departed":
                for entry in park_util[event.parking_space]:
                    if entry["trailer_id"]== event.trailer_id and "departure_time" not in entry:
                        entry["departure_time"] = event.timestamp

        return park_util

    def get_utilization_stats(self) -> dict:
        util_stats = {}
        park_util = self.get_parking_departure()
        print()
        print(park_util)
        print()

        for park_space, item in park_util.items():
            total_time=0
            for entry in item:
                if "departure_time" in entry:
                    duration = (entry["departure_time"] - entry["arrival_time"]).total_seconds() // 3600
                    total_time += duration
            util_stats[park_space] = total_time

        return util_stats

# Main Function
if __name__ == "__main__":
    file_path = "../data_set/events.json"  # Replace with your JSON file path
    events = load_json(file_path)
    yard_stats, parking_utilization = process_events(events)
    utilization_stats = calculate_utilization(parking_utilization)
    display_results(yard_stats, utilization_stats)

    print()
    print("Results after applying OOP")
    print()
    analyzer = TrailerEventAnalyzer(file_path)

    analyzer.load_data()

    yard_statistics = analyzer.get_yard_stats()
    for yard, statistics in yard_statistics.items():
        print(f"Yard {yard}: Arrivals: {statistics['arrivals']}, Departures: {statistics['departures']}")

    utilization_stats = analyzer.get_utilization_stats()

    for parking_space, total_time in utilization_stats.items():
        print(f"Parking Space {parking_space}: Total Usage Time: {total_time:.2f} hours")





