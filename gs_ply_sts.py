import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import glob

# Define the scope of the application
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from the service account
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet
sheet_name = "Premier League"  # Replace with your sheet name
try:
    spreadsheet = client.open(sheet_name)
except gspread.exceptions.SpreadsheetNotFound as e:
    print(f"SpreadsheetNotFound: {e}")
    exit(1)

# Directory containing the combined Excel files
combined_directory = r"data\combine"
xlsx_pattern = os.path.join(combined_directory, "*.xlsx")

# List all Excel files in the directory
xlsx_files = glob.glob(xlsx_pattern)

if not xlsx_files:
    print("No Excel files found in the directory.")
    exit(0)

# Columns to keep in the final output
columns_to_keep = [
    'Date', 'Home Team', 'Away Team', 'Team', '+', 'Goals', 'Assists', 'Total tackles', 'Shots on target',
    'Shots off target', 'Total Shorts', 'Expected Goals (xG)',  'totalPass', 'Key passes', 'Fouls', 'Saves', 'rating'
]

def update_google_sheet(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path)
    base_name = os.path.basename(file_path)
    file_name, _ = os.path.splitext(base_name)

    if df.empty:
        print(f"DataFrame from {file_path} is empty, skipping.")
        return

    # Keep only the specified columns
    df = df[columns_to_keep]

    # Handle NaN values by replacing them with "NA"
    df = df.fillna("NA")

    # Add a 'Match' column
    df['Match'] = df.apply(lambda row: f"{row['Home Team']} vs {row['Away Team']}", axis=1)

    # Separate data for Home Team and Away Team
    home_team = df['Home Team'].iloc[0]
    away_team = df['Away Team'].iloc[0]

    home_team_df = df[df['Team'] == home_team]
    away_team_df = df[df['Team'] == away_team]

    # Update Google Sheet for Home Team
    if not home_team_df.empty:
        update_team_sheet(home_team, home_team_df)

    # Update Google Sheet for Away Team
    if not away_team_df.empty:
        update_team_sheet(away_team, away_team_df)

def update_team_sheet(team_name, team_df):
    # Find the Google Sheet by team name
    try:
        gsheet = spreadsheet.worksheet(team_name)
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"Worksheet {team_name} not found in Google Sheets.")
        return

    # Prepare data for Google Sheets
    columns_order = ['Date', 'Match'] + [col for col in columns_to_keep if col not in ['Date', 'Home Team', 'Away Team', 'Team']]
    team_df = team_df[columns_order]

    # Convert DataFrame to list of lists for Google Sheets
    data = team_df.values.tolist()
    all_rows = [team_df.columns.tolist()] + data

    # Find the last non-empty row and determine the start row for new data
    cell_values = gsheet.get_all_values()
    last_row = len(cell_values)  # Last row with data

    # Calculate the starting row for the new data
    start_row = last_row + 2  # Leave one row gap

    # Determine the cell range
    num_rows = len(all_rows)
    num_cols = len(all_rows[0])
    end_col = chr(65 + (num_cols - 1) % 26)
    cell_range = f'A{start_row}:{end_col}{start_row + num_rows - 1}'

    print(f"Updating cell range: {cell_range} in sheet: {team_name}")

    # Generate the cell list for batch update
    cell_list = gsheet.range(cell_range)
    for i, cell in enumerate(cell_list):
        row_index = i // num_cols
        col_index = i % num_cols
        cell.value = all_rows[row_index][col_index]

    gsheet.update_cells(cell_list)
    print(f"Data for {team_name} updated successfully in Google Sheets!")

# Process all Excel files in the directory
for xlsx_file in xlsx_files:
    print(f"Processing file: {xlsx_file}")
    update_google_sheet(xlsx_file)

print("All Excel files processed.")
