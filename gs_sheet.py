import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import glob
import numpy as np

# Define the scope of the application
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from the service account
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet
spreadsheet_name = "Premier League"  # Replace with your spreadsheet name
sheet_name = "Premier League"  # Replace with your sheet name

try:
    sheet = client.open(spreadsheet_name).worksheet(sheet_name)
except gspread.exceptions.SpreadsheetNotFound as e:
    print(f"SpreadsheetNotFound: {e}")
    exit(1)
except gspread.exceptions.WorksheetNotFound as e:
    print(f"WorksheetNotFound: {e}")
    exit(1)

# Directory containing the CSV files
data_directory = r"data\import"
csv_pattern = os.path.join(data_directory, "*.csv")

# List all CSV files in the directory
csv_files = glob.glob(csv_pattern)

if not csv_files:
    print("No CSV files found in the directory.")
    exit(0)

# Process each CSV file
for csv_file in csv_files:
    print(f"Processing file: {csv_file}")

    try:
        df = pd.read_csv(csv_file)
        if df.empty:
            print(f"DataFrame from {csv_file} is empty, skipping.")
            continue

        # Ensure all required columns are present; add missing columns with 'NA' values
        required_columns = [
            'Date', 'Teams', 'Goals', 'Ball possession', 'Total shots', 'Shots on target',
            'Tackles', 'Expected goals', 'Big chances',  'Fouls', 'Big chances missed',
            'Goalkeeper saves', 'Corner kicks', 'Offsides',
            'Goal kicks', 'Throw-ins', 'Red cards', 'Yellow cards', 'sofascore Rating'
        ]

        # Add missing columns with 'NA' values
        for col in required_columns:
            if col not in df.columns:
                df[col] = "NA"

        # Reorder columns to ensure 'Date', 'Teams', 'Goals' are first
        columns_order = ['Date', 'Teams', 'Goals'] + [col for col in required_columns if
                                                      col not in ['Date', 'Teams', 'Goals']]
        df = df[columns_order]

        # Replace NaN values with "NA"
        df.replace({np.nan: "NA"}, inplace=True)

        # Get the column headers and data from the DataFrame
        columns = df.columns.tolist()
        data = df.values.tolist()

        # Print the headers and data to check correctness
        print(f"Columns: {columns}")
        print(f"First row of data: {data[0] if data else 'No data'}")

        # Prepare all rows to be inserted
        all_rows = [columns] + data

        # Find the last non-empty row and determine the start row for new data
        cell_values = sheet.get_all_values()
        last_row = len(cell_values)  # Last row with data

        # Calculate the starting row for the new data
        start_row = last_row + 2  # Leave one row gap

        # Correct cell range calculation
        num_rows = len(all_rows)
        num_cols = len(all_rows[0])
        end_col = chr(65 + (num_cols - 1) % 26)
        end_row = chr(65 + (num_cols - 1) // 26) if num_cols > 26 else ''
        cell_range = f'A{start_row}:{end_col}{start_row + num_rows - 1}'

        print(f"Updating cell range: {cell_range}")

        # Generate the cell list for batch update
        cell_list = sheet.range(cell_range)
        for i, cell in enumerate(cell_list):
            row_index = i // num_cols
            col_index = i % num_cols
            cell.value = all_rows[row_index][col_index]

        sheet.update_cells(cell_list)
        print(f"Data from {csv_file} imported successfully!")

    except PermissionError as e:
        print(f"PermissionError: {e}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except pd.errors.EmptyDataError as e:
        print(f"EmptyDataError: {e}")
    except pd.errors.ParserError as e:
        print(f"ParserError: {e}")
    except gspread.exceptions.APIError as e:
        print(f"APIError: {e}")

print("All CSV files processed.")
