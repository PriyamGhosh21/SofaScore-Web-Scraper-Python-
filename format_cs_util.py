import os
import pandas as pd

# Directory containing the cleaned CSV files
csv_dir = r'C:\Users\Priyam\Desktop\python\Final\data'


def format_and_paste_data(input_file, output_file):
    print(f"Processing file: {input_file}")  # Debugging statement

    # Read the CSV file
    df = pd.read_csv(input_file)

    # Check if required columns exist
    required_columns = [
        'incidents__incidents__homeScore',
        'incidents__incidents__awayScore',
        'incidents__home',
        'incidents__away',
        'incidents__date'
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Missing columns in {input_file}: {missing_columns}")
        return

    # Initialize formatted data
    formatted_data = []

    for index, row in df.iterrows():
        home_team = row.get('incidents__home', 'Unknown Home Team')
        away_team = row.get('incidents__away', 'Unknown Away Team')
        home_score = row.get('incidents__incidents__homeScore', 0)
        away_score = row.get('incidents__incidents__awayScore', 0)
        match_date = row.get('incidents__date', 'Unknown Date')

        formatted_data.append({
            'Date': match_date,
            'Teams': home_team,
            'Goals': home_score
        })
        formatted_data.append({
            'Date': match_date,
            'Teams': away_team,
            'Goals': away_score
        })

    # Create DataFrame from formatted data
    df_formatted = pd.DataFrame(formatted_data)

    # Save the formatted DataFrame to a new CSV file
    df_formatted.to_csv(output_file, index=False)
    print(f"Formatted CSV file saved to {output_file}")


# Process all cleaned .csv files in the directory
files_processed = 0

for file_name in os.listdir(csv_dir):
    if file_name.endswith('_cleaned.csv'):
        input_file_path = os.path.join(csv_dir, file_name)
        output_file_path = os.path.join(csv_dir, file_name.replace('_cleaned.csv', '_formatted.csv'))

        format_and_paste_data(input_file_path, output_file_path)
        files_processed += 1

if files_processed == 0:
    print("No cleaned .csv files found in the directory.")
else:
    print("All cleaned files have been formatted.")
