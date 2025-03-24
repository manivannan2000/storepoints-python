'''
Yard-level summaries for the above solution.

To calculate yard-level summaries for the above solution, we can group parking utilization and peak usage
by yard. This involves tracking arrivals, departures, and utilization per yard.

Modified Solution
Here’s an updated solution to include yard-level summaries:

Explanation
Yard y1:

2 arrivals (t1 and t2) and 2 departures.
Peak utilization: 2 trailers during 12:00 and 13:00.
Yard y2:

1 arrival (t3) and 1 departure.
Peak utilization: 1 trailer during 15:00 and 16:00.
Key Features
Summarization by Yard:

Group events and metrics by yard_id.
Utilization and Peak Hours:

Track parking usage for each hour to calculate peak utilization.
Scalability:

Easily handles multiple yards and parking spaces.

This approach ensures comprehensive yard-level insights, including utilization trends and peak hours.
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
    yard_data = defaultdict(lambda: {"arrivals": 0, "departures": 0, "parking_utilization": defaultdict(list)})

    for event in events:
        yard_id = event["yard_id"]
        parking_space = event["parking_space"]
        trailer_id = event["trailer_id"]
        timestamp = datetime.fromisoformat(event["timestamp"])
        event_type = event["event_type"]

        if event_type == "arrived":
            yard_data[yard_id]["arrivals"] += 1
            yard_data[yard_id]["parking_utilization"][parking_space].append(
                {"trailer_id": trailer_id, "arrival_time": timestamp})
        elif event_type == "departed":
            yard_data[yard_id]["departures"] += 1
            for entry in yard_data[yard_id]["parking_utilization"][parking_space]:
                if entry["trailer_id"] == trailer_id and "departure_time" not in entry:
                    entry["departure_time"] = timestamp
                    break

    return yard_data


# Step 3: Calculate yard-level utilization and peak hours
def calculate_yard_summaries(yard_data):
    yard_summaries = {}

    for yard_id, data in yard_data.items():
        hour_usage = defaultdict(int)

        # Calculate hour-wise utilization
        for parking_space, usage in data["parking_utilization"].items():
            for entry in usage:
                if "departure_time" in entry:
                    arrival = entry["arrival_time"]
                    departure = entry["departure_time"]

                    # Increment usage for each hour during the trailer's stay
                    current_time = arrival.replace(minute=0, second=0, microsecond=0)
                    while current_time < departure:
                        hour_usage[current_time] += 1
                        current_time += timedelta(hours=1)

        # Determine peak utilization and hours
        max_utilization = max(hour_usage.values(), default=0)
        peak_hours = [hour for hour, count in hour_usage.items() if count == max_utilization]

        yard_summaries[yard_id] = {
            "total_arrivals": data["arrivals"],
            "total_departures": data["departures"],
            "peak_utilization": max_utilization,
            "peak_hours": peak_hours
        }

    return yard_summaries


# Step 4: Display yard-level summaries
def display_yard_summaries(yard_summaries):
    for yard_id, summary in yard_summaries.items():
        print(f"Yard {yard_id} Summary:")
        print(f"  Total Arrivals: {summary['total_arrivals']}")
        print(f"  Total Departures: {summary['total_departures']}")
        print(f"  Peak Utilization: {summary['peak_utilization']} trailers")
        print("  Peak Hours:")
        for hour in summary["peak_hours"]:
            print(f"    {hour.strftime('%Y-%m-%d %H:%M:%S')}")
        print()


# Main Function
if __name__ == "__main__":
    file_path = "../data_set/events_yard_summaries.json"  # Replace with your JSON file path
    events = load_json(file_path)
    yard_data = process_events(events)
    yard_summaries = calculate_yard_summaries(yard_data)
    display_yard_summaries(yard_summaries)
