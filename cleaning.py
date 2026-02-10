import os
import pandas as pd

# Directory containing the CSV files
csv_dir = r'data'

# List of required headers
required_headers = [
    'text',
    'homeScore',
    'awayScore',
    'meta_data__home',
    'meta_data__away',
    'meta_data__date',
    'meta_data__url',
    'name',
    'home',
    'away',
    'homeValue',
    'awayValue'

]

def clean_csv(input_file, output_file, headers):
    print(f"Processing file: {input_file}")  # Debugging statement

    # Read the CSV file
    df = pd.read_csv(input_file)

    # Strip any leading or trailing spaces from column names
    df.columns = df.columns.str.strip()

    # Check if all required headers are present
    missing_headers = [header for header in headers if header not in df.columns]
    if missing_headers:
        print(f"Missing headers in {input_file}: {missing_headers}")
        return

    # Ensure all required headers are present in the DataFrame
    for header in headers:
        if header not in df.columns:
            df[header] = pd.NA

    # Reorder columns to match the required headers
    df = df[headers]

    # Shift data upwards to fill in gaps
    df = df.apply(lambda col: col.dropna().reset_index(drop=True))

    # Save the cleaned DataFrame to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Cleaned CSV file saved to {output_file}")

def delete_old_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted old file: {file_path}")

# Process all .csv files in the directory
files_processed = 0
files_to_delete = []

for file_name in os.listdir(csv_dir):
    if file_name.endswith('.csv'):
        input_file_path = os.path.join(csv_dir, file_name)
        output_file_path = os.path.join(csv_dir, file_name.replace('.csv', '_cleaned.csv'))

        clean_csv(input_file_path, output_file_path, required_headers)
        files_processed += 1
        files_to_delete.append(input_file_path)

if files_processed == 0:
    print("No .csv files found in the directory.")
else:
    print("All matching files have been cleaned.")
    # Delete the old, uncleaned files
    delete_old_files(files_to_delete)
