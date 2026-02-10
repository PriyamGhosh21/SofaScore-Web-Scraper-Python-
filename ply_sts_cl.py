import pandas as pd
import os

# Define the input and output paths
input_path = r'data\output'
output_path = r'data\combine'

# Create output directory if it doesn't exist
os.makedirs(output_path, exist_ok=True)

# Columns to keep in the final output
columns_to_keep = ['Date', 'Home Team', 'Away Team', 'Team', '+','Goals', 'Assists', 'Total tackles',
                    'Blocked shots',  'Shots blocked', 'Shots off target', 'Key passes', 'Fouls',
                   'Saves', 'Shots on target', 'Expected Goals (xG)', 'Accurate passes' ]


# Function to combine sheets based on player names in the '+' column
def combine_player_statistics(file_path):
    # Load the Excel file
    xls = pd.ExcelFile(file_path)

    print(f"Processing file: {file_path}")

    # List of sheet names to read
    sheets = ['Player Statistics', 'Attack Statistics', 'Defence Statistics', 'Passing Statistics', 'Duels Statistics',
              'Goalkeeper Statistics']
    dataframes = {}

    # Read each sheet into a DataFrame
    for sheet in sheets:
        if sheet in xls.sheet_names:
            df = xls.parse(sheet)
            print(f"Loaded sheet: {sheet} with {df.shape[0]} rows and {df.shape[1]} columns")
            # Check if the '+' column exists in the sheet
            if '+' in df.columns:
                # Drop columns with suffixes to avoid conflicts
                df = df.loc[:, ~df.columns.str.contains('_x|_y')]
                dataframes[sheet] = df
            else:
                print(f"Sheet {sheet} does not contain a '+' column.")
        else:
            print(f"Sheet {sheet} not found in {file_path}")

    if not dataframes:
        print("No valid sheets found in the file.")
        return

    # Initialize an empty DataFrame to combine data
    combined_df = pd.DataFrame()

    # Process 'Player Statistics' first
    if 'Player Statistics' in dataframes:
        combined_df = dataframes['Player Statistics']

    # Merge data from other sheets based on the '+' column
    for sheet, df in dataframes.items():
        if sheet != 'Player Statistics':
            # Remove duplicates based on the '+' column
            df = df.drop_duplicates(subset='+', keep='first')
            # Merge with the combined DataFrame
            combined_df = pd.merge(combined_df, df, on='+', how='outer', suffixes=('', '_dup'))

            # Remove columns that have '_dup' suffix to handle duplicates
            duplicate_cols = [col for col in combined_df.columns if col.endswith('_dup')]
            combined_df = combined_df.drop(columns=duplicate_cols)

    # Keep only the specified columns
    combined_df = combined_df[columns_to_keep]

    # Define the output file name based on the input file name
    base_name = os.path.basename(file_path)
    file_name, _ = os.path.splitext(base_name)
    output_file = os.path.join(output_path, f'{file_name}_combined.xlsx')

    # Write the combined dataframe to an Excel file
    combined_df.to_excel(output_file, index=False)

    print(f'Combined file saved to {output_file}')


# Process all Excel files in the input directory
for file_name in os.listdir(input_path):
    if file_name.endswith('.xlsx'):
        file_path = os.path.join(input_path, file_name)
        combine_player_statistics(file_path)
