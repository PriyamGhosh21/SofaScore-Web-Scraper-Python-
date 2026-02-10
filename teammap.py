import json

# Define a dictionary with full names as keys and short names as values
team_name_mappings = {
    "Wolverhampton": "Wolverhampton Wanderers"
    
    # Add other teams as needed
}

def shorten_team_names(json_file_path):
    # Load the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Iterate through each match and replace full names with short names
    for match in data:
        team_1_full = match["team_1"]
        team_2_full = match["team_2"]
        
        # Replace full names with short names if they exist in the dictionary
        match["team_1"] = team_name_mappings.get(team_1_full, team_1_full)
        match["team_2"] = team_name_mappings.get(team_2_full, team_2_full)

    # Save the modified data back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Updated team names in {json_file_path}")

# Usage example
json_file_path = r'team_links.json'  # Replace with your actual file path
shorten_team_names(json_file_path)
