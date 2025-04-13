# Time In Zones – Cycling Activities Analyzer

analyze garmin .fit files for time spent per heart rate zone.  
also shows basic activity data (date, duration, distance, moving time).  
writes results into `zones.csv`.

:warning: after processing, all `.zip` files in `activity-files/` will be deleted.  
the extracted `.fit` files will be moved to `done/`.

## Dependencies

make sure these are installed:  
- `pip3 install fitparse`  
  [python-fitparse](https://github.com/dtcooper/python-fitparse)

## Usage

1. put `.fit` or `.zip` (containing a `.fit`) into `activity-files/`
2. run: `python3 time-in-zones.py`
3. view: `zones.csv`
