import os
import pandas as pd


def update_team_names(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Check if the required columns exist in the DataFrame
    if all(col in df.columns for col in ['Home Team', 'Away Team', 'Team']):
        home_team = df['Home Team'].iloc[0]
        away_team = df['Away Team'].iloc[0]

        # Determine which team is missing in the "Team" column
        if home_team not in df['Team'].values:
            missing_team = home_team
        elif away_team not in df['Team'].values:
            missing_team = away_team
        else:
            missing_team = None

        # Replace "Unknown" with the missing team name
        if missing_team:
            df['Team'] = df['Team'].replace('Unknown', missing_team)

        # Save the updated DataFrame back to the Excel file
        df.to_excel(file_path, index=False)
        print(f"Updated file: {file_path}")
    else:
        print(f"Required columns not found in file: {file_path}")


def process_directory(directory):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(directory, filename)
            update_team_names(file_path)


if __name__ == "__main__":
    # Directory containing the Excel files
    combine_dir = r"data/combine"

    # Process the directory
    process_directory(combine_dir)
