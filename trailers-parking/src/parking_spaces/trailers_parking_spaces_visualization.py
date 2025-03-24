'''
Adding visualization for the above solution for utilization trends using libraries like matplotlib.

Here’s an updated solution with visualizations for yard utilization trends using matplotlib.
The visualization will show:

Total Time Spent by Trailers in Each Yard (Bar Chart).
Trailer-wise Percentage Utilization for Each Yard (Pie Charts).

Explanation of Visualization

Bar Chart:

Displays the total time spent by trailers in each yard.
Useful for comparing overall yard utilization.

Pie Charts:

Shows the percentage of total utilization contributed by each trailer in a specific yard.
Useful for identifying dominant trailers in each yard.

Output Visualization
Bar Chart: Total Time Spent by Trailers

Yard y1: 2.5 hours
Yard y2: 1.5 hours

Pie Chart: Trailer-Wise Utilization

Yard y1:

Trailer t1: 80%
Trailer t2: 20%

Yard y2:

Trailer t3: 100%

Key Features
Bar Chart:

Highlights the overall time spent by trailers across all yards.

Pie Charts:

Provides detailed insights into how each trailer contributed to a yard's total utilization.

Scalable:

Automatically adapts to multiple yards and trailers.
This solution effectively combines data processing with visual insights, making it easier to analyze
utilization trends.

'''
import matplotlib.pyplot as plt
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
            trailer_percentages = {
                trailer_id: (trailer_times[trailer_id].total_seconds() / total_time.total_seconds()) * 100
                for trailer_id in trailer_times if total_time > timedelta(0)
            }
        else:
            trailer_percentages = {}

        yard_summaries[yard_id] = {
            "total_time": total_time,
            "trailer_percentages": trailer_percentages,
        }

    return yard_summaries

# Step 4: Visualize yard statistics
def visualize_statistics(yard_summaries):
    # Bar Chart: Total Time Spent in Each Yard
    yards = []
    total_times = []
    for yard_id, summary in yard_summaries.items():
        yards.append(yard_id)
        total_times.append(summary["total_time"].total_seconds() / 3600)  # Convert to hours

    plt.figure(figsize=(10, 5))
    plt.bar(yards, total_times, color="skyblue")
    plt.title("Total Time Spent by Trailers in Each Yard")
    plt.xlabel("Yard")
    plt.ylabel("Total Time (hours)")
    plt.show()

    # Pie Charts: Trailer-Wise Utilization for Each Yard
    for yard_id, summary in yard_summaries.items():
        trailer_percentages = summary["trailer_percentages"]
        if trailer_percentages:
            plt.figure(figsize=(6, 6))
            plt.pie(
                trailer_percentages.values(),
                labels=trailer_percentages.keys(),
                autopct="%1.1f%%",
                startangle=140,
            )
            plt.title(f"Trailer-Wise Yard Utilization for Yard {yard_id}")
            plt.show()

# Main Function
if __name__ == "__main__":
    file_path = "../data_set/events_granular_statistics.json"  # Replace with your JSON file path
    events = load_json(file_path)
    yard_data = process_events(events)
    yard_summaries = calculate_granular_statistics(yard_data)
    visualize_statistics(yard_summaries)
