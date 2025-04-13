# Time In Zones - Cycling Activities Analyzer

analyze garmin .fit files and provide basic cycling activity data.  
(date, duration, distance, total moving time, time in heart rate zone)  

## Usage
  - provide .fit file or .zip (containing the .fit file) in `activity-files/` folder
  - run: `python3 time-in-zones.py`
  - data in: `zones.csv`

## Dependencies
Make sure these depencencies are installed:  
  - [python-fitparse](https://github.com/dtcooper/python-fitparse) is installed  
    `pip3 install fitparse`

## @ToDo
  - move files into `done/` folder or something like that
