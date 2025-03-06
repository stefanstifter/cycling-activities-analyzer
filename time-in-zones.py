import os
from fitparse import FitFile
from collections import defaultdict

HR_ZONES = {
    "Z1": (79, 98),
    "Z2": (99, 123),
    "Z3": (124, 136),
    "Z4": (137, 150),
    "Z5": (151, 999),
}


def process_fit_file(filepath):
    """Process a single FIT file and return activity information."""
    try:
        fitfile = FitFile(filepath)
        activity_info = {
            'filename': os.path.basename(filepath),
            'start_time': None,
            'moving_time': None,
            'distance': None,
            'heart_rate_data': [],
        }

        # Extract activity information from the session messages
        for record in fitfile.get_messages('session'):
            for data in record:
                if data.name == 'start_time':
                    activity_info['start_time'] = data.value
                elif data.name == 'total_timer_time':  # Moving time
                    activity_info['moving_time'] = data.value
                elif data.name == 'total_distance':
                    activity_info['distance'] = data.value

        # Extract heart rate data from the record messages
        prev_timestamp = None
        for record in fitfile.get_messages('record'):
            record_data = {field.name: field.value for field in record}

            if "timestamp" in record_data and "heart_rate" in record_data:
                curr_timestamp = record_data["timestamp"]
                heart_rate = record_data["heart_rate"]

                # Only include HR data if timestamps move forward
                # (avoids duplicates or resets)
                if prev_timestamp is None or curr_timestamp > prev_timestamp:
                    activity_info['heart_rate_data'].append(
                        (curr_timestamp, heart_rate))
                    prev_timestamp = curr_timestamp

        return activity_info

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None


def format_duration(seconds):
    """Convert seconds to hours:minutes:seconds format."""
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
    return f"{meters/1000:.2f} km"


def calculate_time_in_zones(heart_rate_data):
    """Computes time spent in each heart rate zone based on moving time."""
    zone_times = defaultdict(int)

    if not heart_rate_data:
        print("DEBUG: No heart rate data found.")
        return zone_times

    total_tracked_time = 0

    for i in range(1, len(heart_rate_data)):
        prev_time, prev_hr = heart_rate_data[i - 1]
        curr_time, curr_hr = heart_rate_data[i]
        duration = (curr_time - prev_time).total_seconds()
        total_tracked_time += duration

        for zone, (low, high) in HR_ZONES.items():
            if low <= prev_hr <= high:
                zone_times[zone] += duration
                break  # Stop at the first matching zone

    print(f"DEBUG: Total time in zones: {format_duration(total_tracked_time)}")
    return zone_times


def format_seconds_to_hms(seconds):
    """Converts seconds into hh:mm:ss format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def main():
    print("Let's process some \"Fit\" files!")

    activities_dir = "activity-files"
    if not os.path.exists(activities_dir):
        print(f"Error: Directory {activities_dir} not found.")

    fit_files = [
        f for f in os.listdir(activities_dir) if f.lower().endswith('.fit')
    ]
    if not fit_files:
        print(f"No .fit files found in {activities_dir}")
        return

    print(f"Found {len(fit_files)} FIT files to process\n")

    # Process each file
    for filename in sorted(fit_files):
        filepath = os.path.join(activities_dir, filename)
        activity_info = process_fit_file(filepath)

        if activity_info:
            print("Activity:", activity_info['filename'])
            if activity_info['start_time']:
                print(
                    "Date:",
                    activity_info['start_time'].strftime("%Y-%m-%d %H:%M:%S"))
            print("Duration (moving):",
                  format_duration(activity_info['moving_time']))
            print("Distance:", format_distance(activity_info['distance']))

            # Compute and display time in zones
            time_in_zones = calculate_time_in_zones(
                activity_info["heart_rate_data"])
            for zone, time in time_in_zones.items():
                formatted_time = format_seconds_to_hms(time)
                print(f"{zone}: {formatted_time}")

            print("-" * 50)


if __name__ == "__main__":
    main()
