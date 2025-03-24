'''
To extend the solution with more granular statistics, we can calculate additional metrics such as:

Total time trailers spent in each yard.
Average time spent per trailer in each yard.
Percentage of the total yard utilization for each trailer.
Number of unique trailers visiting each yard.
Updated Solution
Here’s the enhanced Python code:

Explanation of Granular Statistics
Total Time:

Total cumulative time spent by all trailers in the yard.
Average Time Per Trailer:

Total time divided by the number of trailers.
Percentage of Yard Utilization:

Each trailer’s contribution to the total yard time as a percentage.
Unique Trailers:

Count of trailers that visited the yard.
Most and Least Time Trailers:

Identifies trailers with the longest and shortest durations in the yard.

Enhancements in Output
Comprehensive Time Analysis:

Total and average times provide a better understanding of yard usage.
Trailer Contributions:

Percentages help identify which trailers utilized the yard the most.
Unique Trailer Count:

Useful for tracking yard activity and diversity of trailer visits.
This enhanced solution offers a complete view of yard utilization and trailer activities.

'''

from collections import defaultdict
from datetime import datetime, timedelta
import json


# Step 1: Load the JSON dataset
def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


# Step 2: Process events to track yard and trailer statistics
def process_events(events):
    yard_data = defaultdict(lambda: {
        "arrivals": 0,
        "departures": 0,
        "trailer_durations": defaultdict(lambda: {"arrival_time": None, "total_time": timedelta(0)}),
    })

    for event in events:
        yard_id = event["yard_id"]
        trailer_id = event["trailer_id"]
        timestamp = datetime.fromisoformat(event["timestamp"])
        event_type = event["event_type"]

        if event_type == "arrived":
            yard_data[yard_id]["arrivals"] += 1
            yard_data[yard_id]["trailer_durations"][trailer_id]["arrival_time"] = timestamp
        elif event_type == "departed":
            yard_data[yard_id]["departures"] += 1
            trailer_info = yard_data[yard_id]["trailer_durations"][trailer_id]
            if trailer_info["arrival_time"]:
                duration = timestamp - trailer_info["arrival_time"]
                trailer_info["total_time"] += duration
                trailer_info["arrival_time"] = None  # Reset arrival time

    return yard_data


# Step 3: Calculate granular statistics for each yard
def calculate_granular_statistics(yard_data):
    yard_summaries = {}

    for yard_id, data in yard_data.items():
        total_time = timedelta(0)
        trailer_times = {}
        unique_trailers = set()

        for trailer_id, duration_data in data["trailer_durations"].items():
            total_time += duration_data["total_time"]
            trailer_times[trailer_id] = duration_data["total_time"]
            if duration_data["total_time"] > timedelta(0):
                unique_trailers.add(trailer_id)

        if trailer_times:
            most_time_trailer = max(trailer_times, key=trailer_times.get)
            least_time_trailer = min(trailer_times, key=trailer_times.get)
            average_time = total_time / len(trailer_times)
        else:
            most_time_trailer = None
            least_time_trailer = None
            average_time = timedelta(0)

        trailer_percentages = {
            trailer_id: (trailer_times[trailer_id].total_seconds() / total_time.total_seconds()) * 100
            for trailer_id in trailer_times if total_time > timedelta(0)
        }

        yard_summaries[yard_id] = {
            "total_time": total_time,
            "average_time_per_trailer": average_time,
            "most_time_trailer": most_time_trailer,
            "most_time_duration": trailer_times.get(most_time_trailer, timedelta(0)),
            "least_time_trailer": least_time_trailer,
            "least_time_duration": trailer_times.get(least_time_trailer, timedelta(0)),
            "unique_trailers": len(unique_trailers),
            "trailer_percentages": trailer_percentages,
        }

    return yard_summaries


# Step 4: Display detailed yard statistics
def display_granular_statistics(yard_summaries):
    for yard_id, summary in yard_summaries.items():
        print(f"Yard {yard_id} Summary:")
        print(f"  Total Time Spent by All Trailers: {summary['total_time']}")
        print(f"  Average Time Per Trailer: {summary['average_time_per_trailer']}")
        print(f"  Trailer with Most Time: {summary['most_time_trailer']} ({summary['most_time_duration']})")
        print(f"  Trailer with Least Time: {summary['least_time_trailer']} ({summary['least_time_duration']})")
        print(f"  Unique Trailers: {summary['unique_trailers']}")
        print("  Percentage of Yard Utilization by Each Trailer:")
        for trailer_id, percentage in summary["trailer_percentages"].items():
            print(f"    Trailer {trailer_id}: {percentage:.2f}%")
        print()


# Main Function
if __name__ == "__main__":
    file_path = "../data_set/events_granular_statistics.json"  # Replace with your JSON file path
    events = load_json(file_path)
    yard_data = process_events(events)
    yard_summaries = calculate_granular_statistics(yard_data)
    display_granular_statistics(yard_summaries)
