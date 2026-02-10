import pandas as pd
import os
import glob
import re


# Define directories
data_directory = r"data"
import_directory = r"data/import"

# Define the columns to keep and their desired order
columns_to_keep = [
    "Date", "Teams", "Goals", "Ball possession", "Total shots",
    "Shots on target", "Tackles", "Expected goals", "Big chances", "Big chances missed", "Fouls", "Goalkeeper saves",
    "Corner kicks", "Offsides", "Yellow cards", "Red cards",
    "Throw-ins", "Goal kicks", "sofascore Rating"
]



# Ensure the import directory exists
os.makedirs(import_directory, exist_ok=True)

def extract_team_names_from_filename(filename):
    match = re.search(r'_football_match_(.*?)_dsJ_id_', filename)
    if match:
        teams = match.group(1).replace('_', ' ').title()
        return teams
    return None

# List all CSV files in the data directory
csv_pattern = os.path.join(data_directory, "*.csv")
csv_files = glob.glob(csv_pattern)

if not csv_files:
    print("No CSV files found in the directory.")
    exit(0)

# Process each CSV file
for csv_file in csv_files:
    print(f"Processing file: {csv_file}")

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Extract team names from the file name if the "Teams" column is missing or has NaN values
        if "Teams" in df.columns:
            if df["Teams"].isnull().all():
                file_name = os.path.basename(csv_file)
                team_names = extract_team_names_from_filename(file_name)
                if team_names:
                    df["Teams"] = team_names
                else:
                    print(f"Cannot extract team names from file name: {file_name}")
        else:
            file_name = os.path.basename(csv_file)
            team_names = extract_team_names_from_filename(file_name)
            if team_names:
                df["Teams"] = team_names
            else:
                print(f"Cannot extract team names from file name: {file_name}")

        # Add or fill "Yellow cards", "Red cards", "Throw-ins", and "Goal kicks" columns if missing
        for column in ["Yellow cards", "Red cards", "Throw-ins", "Goal kicks"]:
            if column not in df.columns:
                df[column] = "NA"
            else:
                df[column] = df[column].fillna("NA")

        # Check if any of the required columns are missing
        missing_columns = [col for col in columns_to_keep if col not in df.columns]
        if missing_columns:
            print(f"Missing columns in {csv_file}: {missing_columns}")
            for col in missing_columns:
                df[col] = 'None'

        # Keep only the specified columns in the desired order
        df_cleaned = df[columns_to_keep]

        # Construct the new file name and path
        file_name = os.path.basename(csv_file)
        cleaned_file_path = os.path.join(import_directory, file_name)

        # Save the cleaned DataFrame to the new directory
        df_cleaned.to_csv(cleaned_file_path, index=False)
        print(f"Cleaned data saved to: {cleaned_file_path}")

    except PermissionError as e:
        print(f"PermissionError: {e}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except pd.errors.EmptyDataError as e:
        print(f"EmptyDataError: {e}")
    except pd.errors.ParserError as e:
        print(f"ParserError: {e}")

print("All CSV files processed and cleaned.")

