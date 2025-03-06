import os
from fitparse import FitFile
from collections import defaultdict

HR_ZONES = {
    "Z1": (0, 114),  # Example: <60% HRmax
    "Z2": (115, 133),  # 60-70% HRmax
    "Z3": (134, 152),  # 70-80% HRmax
    "Z4": (153, 171),  # 80-90% HRmax
    "Z5": (172, 999),  # >90% HRmax
}


def process_fit_file(filepath):
    """Process a single FIT file and return activity information."""
    try:
        fitfile = FitFile(filepath)

        # Get basic activity info
        activity_info = {
            'filename': os.path.basename(filepath),
            'start_time': None,
            'total_time': None,
            'distance': None,
            'heart_rate_data': [],  # Stores (timestamp, heart_rate)
        }

        # Extract activity information from the session messages
        for record in fitfile.get_messages('session'):
            for data in record:
                if data.name == 'start_time':
                    activity_info['start_time'] = data.value
                elif data.name == 'total_elapsed_time':
                    activity_info['total_time'] = data.value
                elif data.name == 'total_distance':
                    activity_info['distance'] = data.value

        # Extract heart rate data from the record messages
        for record in fitfile.get_messages('record'):
            record_data = {field.name: field.value for field in record}

            if "timestamp" in record_data and "heart_rate" in record_data:
                activity_info['heart_rate_data'].append(
                    (record_data["timestamp"], record_data["heart_rate"]))

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
    """Computes time spent in each heart rate zone."""
    zone_times = defaultdict(int)

    if not heart_rate_data:
        return zone_times

    for i in range(1, len(heart_rate_data)):
        prev_time, prev_hr = heart_rate_data[i - 1]
        curr_time, curr_hr = heart_rate_data[i]

        duration = (curr_time - prev_time).total_seconds()

        for zone, (low, high) in HR_ZONES.items():
            if low <= prev_hr <= high:
                zone_times[zone] += duration
                break  # Stop at the first matching zone

    return zone_times


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
            print("Duration:", format_duration(activity_info['total_time']))
            print("Distance:", format_distance(activity_info['distance']))

            # Compute and display time in zones
            time_in_zones = calculate_time_in_zones(
                activity_info["heart_rate_data"])
            for zone, time in time_in_zones.items():
                print(f"{zone}: {time / 60:.1f} min")  # Convert to minutes

            print("-" * 50)


if __name__ == "__main__":
    main()
