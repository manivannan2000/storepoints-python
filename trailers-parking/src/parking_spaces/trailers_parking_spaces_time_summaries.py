'''
Trailers spending the most/least time in a yard for the above solution.

To identify the trailers that spent the most and least time in a yard, we can extend the above solution
to calculate the total time each trailer spends in the yard and track the maximum and minimum durations
for each yard.

Modified Solution
Here’s an updated solution to calculate trailers spending the most and least time in each yard.

Explanation
Tracking Durations:

When a trailer arrives, the arrival_time is recorded in the trailer_durations dictionary for the respective
yard.
When a trailer departs, the time difference between the departure_time and arrival_time is calculated and
stored as total_time.

Identify Most/Least Time Trailers:

For each yard, iterate through trailer_durations to find:
Most Time: Trailer with the maximum total_time.
Least Time: Trailer with the minimum total_time.

Handle Edge Cases:

If no trailers are in a yard, the most and least time trailers are set to None.

Output:

Display the trailer IDs and their corresponding durations for each yard.

Explanation of the Output
Yard y1:

Trailer t1 spent 2 hours in the yard (12:00–14:00).
Trailer t2 spent 30 minutes in the yard (13:00–13:30).
Yard y2:

Only Trailer t3 was in the yard, spending 1 hour 30 minutes (15:00–16:30).
Features
Tracks total time spent by trailers in each yard.
Identifies trailers that spent the most and least time.
Handles edge cases where no trailers exist for a yard.

'''


from collections import defaultdict
from datetime import datetime, timedelta
import json

# Step 1: Load the JSON dataset
def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Step 2: Process events to track yard and parking utilization
def process_events(events):
    yard_data = defaultdict(lambda: {"arrivals": 0, "departures": 0, "trailer_durations": defaultdict(timedelta)})

    for event in events:
        yard_id = event["yard_id"]
        trailer_id = event["trailer_id"]
        timestamp = datetime.fromisoformat(event["timestamp"])
        event_type = event["event_type"]

        if event_type == "arrived":
            yard_data[yard_id]["arrivals"] += 1
            yard_data[yard_id]["trailer_durations"][trailer_id] = {"arrival_time": timestamp}
        elif event_type == "departed":
            yard_data[yard_id]["departures"] += 1
            if trailer_id in yard_data[yard_id]["trailer_durations"]:
                arrival_data = yard_data[yard_id]["trailer_durations"][trailer_id]
                if "arrival_time" in arrival_data:
                    duration = timestamp - arrival_data["arrival_time"]
                    yard_data[yard_id]["trailer_durations"][trailer_id]["total_time"] = duration

    return yard_data

# Step 3: Calculate trailers spending the most/least time in each yard
def calculate_trailer_time_summaries(yard_data):
    yard_summaries = {}

    for yard_id, data in yard_data.items():
        trailer_times = {
            trailer_id: duration_data.get("total_time", timedelta(0))
            for trailer_id, duration_data in data["trailer_durations"].items()
        }

        if trailer_times:
            most_time_trailer = max(trailer_times, key=trailer_times.get)
            least_time_trailer = min(trailer_times, key=trailer_times.get)

            yard_summaries[yard_id] = {
                "most_time_trailer": most_time_trailer,
                "most_time_duration": trailer_times[most_time_trailer],
                "least_time_trailer": least_time_trailer,
                "least_time_duration": trailer_times[least_time_trailer],
            }
        else:
            yard_summaries[yard_id] = {
                "most_time_trailer": None,
                "most_time_duration": timedelta(0),
                "least_time_trailer": None,
                "least_time_duration": timedelta(0),
            }

    return yard_summaries

# Step 4: Display yard-level trailer time summaries
def display_trailer_time_summaries(yard_summaries):
    for yard_id, summary in yard_summaries.items():
        print(f"Yard {yard_id} Summary:")
        print(f"  Trailer with Most Time: {summary['most_time_trailer']} ({summary['most_time_duration']})")
        print(f"  Trailer with Least Time: {summary['least_time_trailer']} ({summary['least_time_duration']})")
        print()

# Main Function
if __name__ == "__main__":
    file_path = "../data_set/events_time_summaries.json"  # Replace with your JSON file path
    events = load_json(file_path)
    yard_data = process_events(events)
    yard_summaries = calculate_trailer_time_summaries(yard_data)
    display_trailer_time_summaries(yard_summaries)
