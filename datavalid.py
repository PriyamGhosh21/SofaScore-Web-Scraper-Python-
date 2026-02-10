import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openpyxl
import json
import os
from datetime import datetime

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive"]

# Load credentials from the credentials.json file
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open the Google Spreadsheet and the specific sheet
spreadsheet = client.open("Premier League")
google_sheet = spreadsheet.worksheet("Premier League")

# Load data from the XLSX file
xlsx_file_path = r'results.xlsx'
xlsx_wb = openpyxl.load_workbook(xlsx_file_path)
xlsx_sheet = xlsx_wb.active

# Define the team name mapping between Google Sheet and XLSX file
team_name_mapping = {
    "Arsenal": "Arsenal",
    "Wolves": "Wolverhampton",
    "Crystal Palace": "Crystal Palace",
    "Bournemouth": "Bournemouth",
    "Manchester City": "Manchester City",
    "Ipswich": "Ipswich Town",
    "Leicester": "Leicester City",
    "Liverpool": "Liverpool",
    "Brighton": "Brighton & Hove Albion",
    "Nottingham": "Nottingham Forest",
    "West Ham": "West Ham United",
    "Southampton": "Southampton",
    "Everton": "Everton",
    "Newcastle": "Newcastle United",
    "Aston Villa": "Aston Villa",
    "Manchester Utd": "Manchester United",
    "Fulham": "Fulham",
    "Brentford": "Brentford",
    "Tottenham": "Tottenham Hotspur",
    "Chelsea": "Chelsea"
    # Add more mappings as needed
}


# Function to standardize team names using the mapping
def standardize_team_name(team_name):
    return team_name_mapping.get(team_name, team_name)


# Function to extract match data from Google Sheets using gspread
def extract_google_sheet_match_data(worksheet):
    match_data = []
    data = worksheet.get_all_values()
    current_match = None

    for row in data:
        if row[0] == "Date" and row[1] == "Teams":  # Header row found, initialize a new match
            if current_match:  # Save the current match if it exists
                match_data.append(current_match)
            current_match = {"date": None, "home_team": None, "away_team": None}
        elif row[0] and row[1] and current_match is not None:  # Row contains match data
            if not current_match["date"]:  # Assign date and home team
                current_match["date"] = row[0]
                current_match["home_team"] = standardize_team_name(row[1])
            else:  # Assign away team
                current_match["away_team"] = standardize_team_name(row[1])
        elif not any(row) and current_match:  # Blank row, end of the current match data
            match_data.append(current_match)
            current_match = None  # Reset for the next match

    # Add the last match if it's not already added
    if current_match:
        match_data.append(current_match)
    return match_data


# Function to extract match data from the XLSX file
def extract_xlsx_match_data(sheet):
    match_data = []
    current_match = None
    for row in sheet.iter_rows(values_only=True):
        if row[0] == "Date" and row[1] == "Teams":  # Header row found, start a new match
            if current_match:  # Save the previous match if it exists
                match_data.append(current_match)
            current_match = {"date": None, "home_team": None, "away_team": None}
        elif row[0] and row[1] and current_match is not None:  # Row contains match data
            if not current_match["date"]:  # Assign date and home team
                current_match["date"] = row[0]
                current_match["home_team"] = standardize_team_name(row[1])
            else:  # Assign away team
                current_match["away_team"] = standardize_team_name(row[1])
        elif not any(row) and current_match:  # Blank row indicates end of the current match
            match_data.append(current_match)
            current_match = None  # Reset for the next match

    # Add the last match if it's not already added
    if current_match:
        match_data.append(current_match)
    return match_data


# Extract match data from both the Google Sheet and the XLSX file
google_matches = extract_google_sheet_match_data(google_sheet)
xlsx_matches = extract_xlsx_match_data(xlsx_sheet)


# Normalize match data for comparison
def normalize_match_data(matches):
    normalized_data = set((match["date"], match["home_team"], match["away_team"]) for match in matches)
    return normalized_data


google_matches_normalized = normalize_match_data(google_matches)
xlsx_matches_normalized = normalize_match_data(xlsx_matches)

# Compare matches to identify any missing matches in the Google Sheet (ignore order differences)
missing_matches = xlsx_matches_normalized - google_matches_normalized

# Prepare log directory and file
log_dir = "Mis_log"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# Save the missing matches to a JSON file if there are any missing
json_file_path = 'missing_matches.json'
no_missing_file_path = 'Nomissing.txt'

if missing_matches:
    # Remove any existing Nomissing.txt file if missing matches are found
    if os.path.exists(no_missing_file_path):
        os.remove(no_missing_file_path)

    # Save missing matches to JSON file
    missing_matches_list = [
        {"date": match[0], "home_team": match[1], "away_team": match[2]}
        for match in missing_matches
    ]
    with open(json_file_path, 'w') as json_file:
        json.dump(missing_matches_list, json_file, indent=4)
    print(f"Missing matches have been saved to {json_file_path}.")
else:
    # Remove the JSON file if no missing matches are found
    if os.path.exists(json_file_path):
        os.remove(json_file_path)

    # Create Nomissing.txt to indicate no missing data
    with open(no_missing_file_path, 'w') as no_missing_file:
        no_missing_file.write("No missing matches found.")
    print("No missing matches found in Google Sheet.")

# Log the run details
with open(log_file_path, 'w') as log_file:
    log_file.write(f"Run date and time: {datetime.now()}\n")
    log_file.write(f"Number of missing matches: {len(missing_matches)}\n")
    if missing_matches:
        log_file.write("Missing matches:\n")
        for match in missing_matches:
            log_file.write(f"Date: {match[0]}, Home Team: {match[1]}, Away Team: {match[2]}\n")
    else:
        log_file.write("No missing matches found.\n")

print(f"Run details have been logged to {log_file_path}.")

# Display the missing matches, if any
if missing_matches:
    print("Missing matches in Google Sheet:")
    for match in missing_matches:
        print(f"Date: {match[0]}, Home Team: {match[1]}, Away Team: {match[2]}")
else:
    print("No missing matches found in Google Sheet.")
