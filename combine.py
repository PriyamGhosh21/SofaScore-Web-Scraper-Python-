import os
import json

# Directory containing the JSON files
json_dir = r'data'

# Path to the team_links.json file
team_links_file = r'team_links.json'

# Function to load team links data
def load_team_links():
    with open(team_links_file, 'r') as f:
        return json.load(f)

# Function to extract incidents data
def extract_incidents_data(incidents_file, team_links):
    with open(incidents_file, 'r') as f:
        incidents_data = json.load(f)

    # Get home and away teams
    home_team = incidents_data.get("home", "")
    away_team = incidents_data.get("away", "")

    # Get the URL based on team names
    url = ""
    for link in team_links:
        if link["team_1"] == home_team and link["team_2"] == away_team:
            url = link["url"]
            break

    # Extract only the required incidents section and meta data
    return {
        "incidents": incidents_data.get("incidents", []),
        "meta_data": {
            "home": home_team,
            "away": away_team,
            "date": incidents_data.get("date", ""),
            "url": url
        }
    }

# Function to combine statistics and incidents JSON files
def combine_json_files(statistics_file, incidents_file, output_file, team_links):
    with open(statistics_file, 'r') as f:
        statistics_data = json.load(f)

    incidents_data = extract_incidents_data(incidents_file, team_links)

    # Combine the two JSON objects with incidents data on top
    combined_data = {
        "incidents": incidents_data["incidents"],
        "meta_data": incidents_data["meta_data"],
        "statistics": statistics_data
    }

    # Save the combined data to a new JSON file
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)

# Function to delete original JSON files
def delete_files(files_to_delete):
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

# Load team links data
team_links = load_team_links()

# Get a list of all JSON files in the directory
json_files = os.listdir(json_dir)

# Track files to delete
files_to_delete = []

# Find pairs of statistics and incidents files and combine them
for file_name in json_files:
    if file_name.endswith("_statistics.json"):
        base_name = file_name.replace("_statistics.json", "")
        incidents_file_name = base_name + "_incidents.json"

        statistics_file_path = os.path.join(json_dir, file_name)
        incidents_file_path = os.path.join(json_dir, incidents_file_name)
        output_file_path = os.path.join(json_dir, base_name + "_combined.json")

        if os.path.exists(incidents_file_path):
            combine_json_files(statistics_file_path, incidents_file_path, output_file_path, team_links)
            print(f"Combined JSON for {base_name} has been saved to {output_file_path}")

            # Add original files to the delete list
            files_to_delete.extend([statistics_file_path, incidents_file_path])
        else:
            print(f"No matching incidents file found for {base_name}")

# Delete the original uncombined files
delete_files(files_to_delete)

print("All matching files have been combined and original files deleted.")
