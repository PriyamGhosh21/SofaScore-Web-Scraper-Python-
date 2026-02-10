import pandas as pd
import os

# Paths to the directories
xlsx_files_dir = r'data/xlsx_files'
combine_dir = r'data/combine'

# Create the combine directory if it doesn't exist
if not os.path.exists(combine_dir):
    os.makedirs(combine_dir)

# Function to combine data and calculate Total Shorts
def combine_data(xlsx_file, combined_file):
    try:
        # Read the home and away sheets from the xlsx file
        home_df = pd.read_excel(xlsx_file, sheet_name='Home Team')
        away_df = pd.read_excel(xlsx_file, sheet_name='Away Team')

        # Read the combined file
        combined_df = pd.read_excel(combined_file)

        # Ensure the combined file has the expected columns
        if '+' not in combined_df.columns:
            print(f"Column '+' not found in {combined_file}")
            return

        # Loop through the home team data and update combined file
        for _, home_row in home_df.iterrows():
            name = home_row['name']
            total_pass = home_row['totalPass']
            rating = home_row['rating']

            # Check if name in 'name' column matches any in the '+' column of the combined data
            mask = combined_df['+'].str.contains(name, case=False, na=False)
            if mask.any():
                # Update totalPass and rating columns in the combined file
                combined_df.loc[mask, 'totalPass'] = total_pass
                combined_df.loc[mask, 'rating'] = rating

        # Loop through the away team data and update combined file
        for _, away_row in away_df.iterrows():
            name = away_row['name']
            total_pass = away_row['totalPass']
            rating = away_row['rating']

            # Check if name in 'name' column matches any in the '+' column of the combined data
            mask = combined_df['+'].str.contains(name, case=False, na=False)
            if mask.any():
                # Update totalPass and rating columns in the combined file
                combined_df.loc[mask, 'totalPass'] = total_pass
                combined_df.loc[mask, 'rating'] = rating

        # Now, calculate the Total Shorts column (Shots on target + Shots off target + Shots blocked)
        if 'Shots on target' in combined_df.columns and 'Shots off target' in combined_df.columns and 'Shots blocked' in combined_df.columns:
            combined_df['Total Shorts'] = combined_df['Shots on target'].fillna(0) + \
                                          combined_df['Shots off target'].fillna(0) + \
                                          combined_df['Shots blocked'].fillna(0)
        else:
            print(f"One of the required columns (Shots on target, Shots off target, or Shots blocked) is missing in {combined_file}")

        # Save the updated combined file
        combined_df.to_excel(combined_file, index=False)
        print(f"Updated combined data saved to {combined_file}")

    except Exception as e:
        print(f"An error occurred while processing {xlsx_file} and {combined_file}: {e}")

# Loop through xlsx files in the xlsx_files directory
for xlsx_filename in os.listdir(xlsx_files_dir):
    if xlsx_filename.endswith('.xlsx'):
        # Construct the corresponding combined filename
        base_filename = os.path.splitext(xlsx_filename)[0]
        # Replace underscores with spaces for matching combined files
        combined_filename = f"{base_filename.replace('_', ' ')}_combined.xlsx"

        xlsx_file_path = os.path.join(xlsx_files_dir, xlsx_filename)
        combined_file_path = os.path.join(combine_dir, combined_filename)

        if os.path.exists(combined_file_path):
            combine_data(xlsx_file_path, combined_file_path)
        else:
            print(f"Combined file {combined_file_path} not found.")
