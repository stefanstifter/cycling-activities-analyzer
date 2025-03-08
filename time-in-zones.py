import os
import csv
from fitparse import FitFile
from collections import defaultdict

HR_ZONES = {
    "Z1": (79, 98),
    "Z2": (99, 123),
    "Z3": (124, 136),
    "Z4": (137, 150),
    "Z5": (151, 999),
}

CSV_FILENAME = "activity_summary.csv"


def process_fit_file(filepath):
    """Process a single FIT file and return activity information."""
    try:
        fitfile = FitFile(filepath)

        activity_info = {
            'filename': os.path.basename(filepath),
            'start_time': None,
            'total_time': None,
            'moving_time': None,
            'distance': None,
            'heart_rate_data': [],
            'speed_data': []
        }

        for record in fitfile.get_messages('session'):
            for data in record:
                if data.name == 'start_time':
                    activity_info['start_time'] = data.value
                elif data.name == 'total_elapsed_time':
                    activity_info['total_time'] = data.value
                elif data.name == 'total_timer_time':
                    activity_info['moving_time'] = data.value
                elif data.name == 'total_distance':
                    activity_info['distance'] = data.value

        for record in fitfile.get_messages('record'):
            record_data = {field.name: field.value for field in record}

            if "timestamp" in record_data and "heart_rate" in record_data:
                activity_info['heart_rate_data'].append(
                    (record_data["timestamp"], record_data["heart_rate"]))

                speed = record_data.get("speed", 0)
                activity_info['speed_data'].append(speed)

        return activity_info

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None


def format_duration(seconds):
    """Convert seconds to hh:mm:ss format."""
    if seconds is None:
        return "Unknown"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_distance(meters):
    """Convert distance from meters to kilometers."""
    if meters is None:
        return "Unknown"
    return f"{meters/1000:.2f}"


def calculate_time_in_zones(heart_rate_data, speed_data):
    """Computes time spent in each heart rate zone based on moving time."""
    zone_times = defaultdict(int)
    total_moving_time = 0

    if not heart_rate_data:
        print("DEBUG: No heart rate data found.")
        return zone_times

    for i in range(1, len(heart_rate_data)):
        prev_time, prev_hr = heart_rate_data[i - 1]
        curr_time, curr_hr = heart_rate_data[i]
        prev_speed = speed_data[i - 1] if i - 1 < len(speed_data) else 0

        duration = (curr_time - prev_time).total_seconds()

        if prev_speed > 2.78:  # 10 km/h
            total_moving_time += duration
            for zone, (low, high) in HR_ZONES.items():
                if low <= prev_hr <= high:
                    zone_times[zone] += duration
                    break

    print(
        f"DEBUG: Total moving time in zones (> 2.78m/s | 10km/h): {format_duration(total_moving_time)}"
    )
    return zone_times


def format_seconds_to_hms(seconds):
    """Converts seconds into hh:mm:ss format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def write_to_csv(data):
    """Writes activity data to a CSV file."""
    file_exists = os.path.isfile(CSV_FILENAME)

    with open(CSV_FILENAME, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)

        if not file_exists:
            writer.writerow([
                "Date", "Ruhe Puls", "Distance in km", "Duration (total)",
                "Time in Z1", "Time in Z2", "Time in Z3", "Time in Z4",
                "Time in Z5", "Duration (moving)"
            ])

        writer.writerow(data)


def main():
    print("Let's process some \"Fit\" files!")

    activities_dir = "activity-files"
    if not os.path.exists(activities_dir):
        print(f"Error: Directory {activities_dir} not found.")
        return

    fit_files = [
        f for f in os.listdir(activities_dir) if f.lower().endswith('.fit')
    ]
    if not fit_files:
        print(f"No .fit files found in {activities_dir}")
        return

    print(f"Found {len(fit_files)} FIT files to process\n")

    for filename in sorted(fit_files):
        filepath = os.path.join(activities_dir, filename)
        activity_info = process_fit_file(filepath)

        if activity_info:
            print("Activity:", activity_info['filename'])
            print("Date:",
                  activity_info['start_time'].strftime("%Y-%m-%d %H:%M:%S"))
            print("Duration (total):",
                  format_duration(activity_info['total_time']))
            print("Duration (moving):",
                  format_duration(activity_info['moving_time']))
            print("Distance:", format_distance(activity_info['distance']))

            time_in_zones = calculate_time_in_zones(
                activity_info["heart_rate_data"], activity_info["speed_data"])

            for zone, time in time_in_zones.items():
                formatted_time = format_seconds_to_hms(time)
                print(f"{zone}: {formatted_time}")

            print("-" * 50)

            csv_data = [
                activity_info['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                "",
                format_distance(activity_info['distance']),
                format_duration(activity_info['total_time']),
                format_seconds_to_hms(time_in_zones.get("Z1", 0)),
                format_seconds_to_hms(time_in_zones.get("Z2", 0)),
                format_seconds_to_hms(time_in_zones.get("Z3", 0)),
                format_seconds_to_hms(time_in_zones.get("Z4", 0)),
                format_seconds_to_hms(time_in_zones.get("Z5", 0)),
                format_duration(activity_info['moving_time']),
            ]

            write_to_csv(csv_data)


if __name__ == "__main__":
    main()
