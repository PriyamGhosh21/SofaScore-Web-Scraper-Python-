import os
import pandas as pd

# Directory containing the unformatted CSV files
csv_dir = r'data'


def process_unformatted_csv(input_file, output_file):
    print(f"Processing file: {input_file}")  # Debugging statement

    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Print column names for debugging
        print(f"Columns in file {input_file}: {df.columns.tolist()}")

        # Initialize formatted data
        formatted_data = {
            'Date': [],
            'Teams': [],
            'Goals': []
        }

        # Check for necessary columns
        required_columns = ['meta_data__date', 'meta_data__home', 'meta_data__away', 'homeScore', 'awayScore']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"Missing columns in file {input_file}: {', '.join(missing_columns)}")
            return

        # Extract the date, teams, and goals
        date = df['meta_data__date'].iloc[0]
        home_team = df['meta_data__home'].iloc[0]
        away_team = df['meta_data__away'].iloc[0]
        home_score = df['homeScore'].iloc[0]
        away_score = df['awayScore'].iloc[0]

        formatted_data['Date'].extend([date, date])
        formatted_data['Teams'].extend([home_team, away_team])
        formatted_data['Goals'].extend([home_score, away_score])

        # Extract and process statistics data
        for index, row in df.iterrows():
            stat_name = row.get('name')
            home_stat_value = row.get('homeValue')
            away_stat_value = row.get('awayValue')

            if stat_name not in formatted_data:
                formatted_data[stat_name] = [None, None]

            formatted_data[stat_name][0] = home_stat_value
            formatted_data[stat_name][1] = away_stat_value

        # Create DataFrame from formatted data
        df_formatted = pd.DataFrame(formatted_data)

        # Save the formatted DataFrame to a new CSV file
        df_formatted.to_csv(output_file, index=False)
        print(f"Formatted CSV file saved to {output_file}")

    except Exception as e:
        print(f"Error processing file {input_file}: {e}")


def process_all_unformatted_csv_files(csv_dir):
    files_processed = 0

    for file_name in os.listdir(csv_dir):
        if file_name.endswith('.csv') and not file_name.endswith('_formatted.csv'):
            input_file_path = os.path.join(csv_dir, file_name)
            output_file_path = os.path.join(csv_dir, file_name.replace('.csv', '_formatted.csv'))

            process_unformatted_csv(input_file_path, output_file_path)

            # Delete the original unformatted CSV file
            # Uncomment the following line if you want to delete original files after successful processing
            os.remove(input_file_path)
            print(f"Deleted original file: {input_file_path}")

            files_processed += 1

    if files_processed == 0:
        print("No unformatted .csv files found in the directory.")
    else:
        print("All unformatted files have been processed, formatted, and deleted.")


# Run the script to process all unformatted CSV files in the directory
process_all_unformatted_csv_files(csv_dir)
