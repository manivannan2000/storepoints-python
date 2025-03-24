'''
To calculate peak utilization hours, we need to determine the hours when the maximum number of trailers
are in parking spaces. This involves tracking when trailers arrive and leave, and counting how many trailers
are in parking spaces during each hour.

Modified Solution
Here’s the updated solution with a calculation for peak utilization hours:

Explanation
Track Parking Utilization by Time:

For each trailer's stay, calculate the range of hours from arrival_time to departure_time.
Increment the trailer count for each hour during this range.
Calculate Peak Utilization:

Use a dictionary (hour_usage) to track the number of trailers in parking spaces for each hour.
Determine the maximum number of trailers present in any single hour (max_utilization).
Find Peak Hours:

Identify all hours where the trailer count equals the maximum utilization.
Output:

Display the peak utilization and the corresponding hours.

How it Works
At 12:00:

Trailer t1 arrives (p1).
Trailer t2 arrives (p2).
Total: 2 trailers.
At 13:00:

Both trailers are still parked.
Total: 2 trailers.
At 14:00:

Only t2 is parked.
Total: 1 trailer.
The peak utilization of 2 trailers occurs during the hours starting at 12:00 and 13:00.

Customizations
You can:

Extend the solution to group peak hours by yards.
Add visualization for utilization trends using libraries like matplotlib.
Modify time granularity (e.g., use 30-minute intervals).

'''


from collections import defaultdict
from datetime import datetime, timedelta
import json

# Step 1: Load the JSON dataset
def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Step 2: Process events to track parking usage by time
def process_events(events):
    parking_utilization = defaultdict(list)  # {parking_space: [(arrival_time, departure_time)]}

    for event in events:
        parking_space = event["parking_space"]
        trailer_id = event["trailer_id"]
        timestamp = datetime.fromisoformat(event["timestamp"])
        event_type = event["event_type"]

        # Track arrivals and departures
        if event_type == "arrived":
            parking_utilization[parking_space].append({"trailer_id": trailer_id, "arrival_time": timestamp})
        elif event_type == "departed":
            for entry in parking_utilization[parking_space]:
                if entry["trailer_id"] == trailer_id and "departure_time" not in entry:
                    entry["departure_time"] = timestamp
                    break

    return parking_utilization

# Step 3: Calculate peak utilization hours
def calculate_peak_hours(parking_utilization):
    hour_usage = defaultdict(int)  # {hour: number_of_trailers}

    for parking_space, usage in parking_utilization.items():
        for entry in usage:
            if "departure_time" in entry:
                arrival = entry["arrival_time"]
                departure = entry["departure_time"]

                # Increment usage for each hour during the trailer's stay
                current_time = arrival.replace(minute=0, second=0, microsecond=0)
                while current_time < departure:
                    hour_usage[current_time] += 1
                    current_time += timedelta(hours=1)

    # Find the peak hour(s) with maximum utilization
    max_utilization = max(hour_usage.values(), default=0)
    peak_hours = [hour for hour, count in hour_usage.items() if count == max_utilization]

    return max_utilization, peak_hours

# Step 4: Display results
def display_results(max_utilization, peak_hours):
    print(f"Peak Utilization: {max_utilization} trailers")
    print("Peak Hours:")
    for hour in peak_hours:
        print(hour.strftime("%Y-%m-%d %H:%M:%S"))

# Main Function
if __name__ == "__main__":
    file_path = "../data_set/events_peak_hours.json"  # Replace with your JSON file path
    events = load_json(file_path)
    parking_utilization = process_events(events)
    max_utilization, peak_hours = calculate_peak_hours(parking_utilization)
    display_results(max_utilization, peak_hours)
