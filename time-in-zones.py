import os


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


if __name__ == "__main__":
    main()
