import json
from datetime import datetime, timedelta
import subprocess

def date_to_words(date_str):
    """ Convert a date string to a more readable format with month names. """
    months = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    day, month, year = date_str.split('/')
    return f"{day}_{months[month]}_{year}"

def task_exists(task_name):
    """ Check if a task with the given name already exists. """
    command = f'schtasks /query /tn "{task_name}" /fo LIST /v'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode == 0 and "TaskName" in result.stdout

try:
    # Step 1: Read the JSON file
    with open('upcoming_matches.json', 'r') as file:
        matches = json.load(file)
except FileNotFoundError:
    print("ERROR: 'upcoming_matches.json' file not found.")
    exit(1)
except json.JSONDecodeError:
    print("ERROR: Failed to decode JSON.")
    exit(1)

# Step 2: Parse the JSON data to find the last match of each day
matches_by_date = {}
for match in matches:
    try:
        match_date = match['date']
        if match_date not in matches_by_date:
            matches_by_date[match_date] = []
        matches_by_date[match_date].append(match)
    except KeyError:
        print("ERROR: Missing 'date' key in match data.")
        continue

# Step 3: Find the last match of each day
last_matches = []
for date, matches in matches_by_date.items():
    last_match = max(matches, key=lambda x: x['time'])
    last_matches.append(last_match)

# Step 4: Schedule a task for the next day at 6:00 AM IST
for match in last_matches:
    match_date_str = match['date']
    match_date = datetime.strptime(match_date_str, '%d/%m/%Y')
    schedule_date = match_date + timedelta(days=1)
    schedule_date_str = schedule_date.strftime('%d/%m/%Y')  # Correct format dd/mm/yyyy

    bat_file_path = 'C:\\Users\\Priyam\\Desktop\\EPL.bat'
    task_name = f'Epl_{date_to_words(match_date_str)}'  # Updated task name format
    time_to_run = '06:30'  # 6:00 AM IST

    if task_exists(task_name):
        print(f"Task '{task_name}' already exists.")
    else:
        # Command to create the task
        command = f'schtasks /create /tn "{task_name}" /tr "{bat_file_path}" /sc once /st {time_to_run} /sd {schedule_date_str} /f'

        # Run the command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: {result.stderr.strip()}")
        else:
            print(f"Task scheduled to run {bat_file_path} on {schedule_date_str} at {time_to_run}")
