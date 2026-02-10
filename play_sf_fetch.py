import json
import requests
import os
import re
import pandas as pd
import time

# Paths to the files and directories
team_links_path = r'team_links.json'  # Path to your team_links.json
json_output_dir = r'data/ss'  # Directory where you want to save the JSON files
xlsx_output_dir = r'data/xlsx_files'  # Directory where you want to save the Excel files

# Create the output directories if they don't exist
if not os.path.exists(json_output_dir):
    os.makedirs(json_output_dir)

if not os.path.exists(xlsx_output_dir):
    os.makedirs(xlsx_output_dir)


# Function to extract ID from URL
def extract_id_from_url(url):
    match = re.search(r'id:(\d+)', url)
    if match:
        return match.group(1)
    return None


# Function to fetch and clean lineup data with retry logic
def fetch_and_save_lineup(event_id, home_team, away_team):
    url = f"https://www.sofascore.com/api/v1/event/{event_id}/lineups"
    retries = 20
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            # Initialize cleaned data
            cleaned_data = {
                "home": {"players": []},
                "away": {"players": []}
            }

            # Extract and clean data for home and away teams
            for team_key in ["home", "away"]:
                if team_key in data and "players" in data[team_key]:
                    for player_entry in data[team_key]["players"]:
                        player = player_entry.get("player", {})
                        statistics = player_entry.get("statistics", {})

                        cleaned_player = {
                            "name": player.get("name"),
                            "slug": player.get("slug"),
                            "totalPass": statistics.get("totalPass"),
                            "rating": statistics.get("rating")
                        }

                        cleaned_data[team_key]["players"].append(cleaned_player)

            # Create a filename based on home and away teams
            json_filename = f"{home_team.replace(' ', '_')} vs {away_team.replace(' ', '_')}.json"
            json_output_file = os.path.join(json_output_dir, json_filename)

            # Save cleaned JSON to the file
            with open(json_output_file, 'w') as json_file:
                json.dump(cleaned_data, json_file, indent=4)
            print(f"Saved cleaned lineup data for {home_team} vs {away_team} to {json_output_file}")

            # Convert JSON to Excel
            convert_json_to_excel(json_output_file, home_team, away_team)
            break  # Exit loop if successful

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in 10 seconds...")
                time.sleep(10)  # Wait for 10 minutes before retrying


# Function to convert cleaned JSON to Excel
def convert_json_to_excel(json_file, home_team, away_team):
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Prepare data for DataFrame
    home_players = data.get("home", {}).get("players", [])
    away_players = data.get("away", {}).get("players", [])

    home_df = pd.DataFrame(home_players)
    away_df = pd.DataFrame(away_players)

    # Create an Excel writer object
    xlsx_filename = f"{home_team.replace(' ', '_')} vs {away_team.replace(' ', '_')}.xlsx"
    xlsx_output_file = os.path.join(xlsx_output_dir, xlsx_filename)

    with pd.ExcelWriter(xlsx_output_file, engine='xlsxwriter') as writer:
        home_df.to_excel(writer, sheet_name='Home Team', index=False)
        away_df.to_excel(writer, sheet_name='Away Team', index=False)

    print(f"Saved lineup data for {home_team} vs {away_team} to {xlsx_output_file}")


# Load team links JSON
try:
    with open(team_links_path, 'r') as file:
        team_links = json.load(file)
except FileNotFoundError:
    print(f"File {team_links_path} not found.")
    exit(1)

# Loop through team links and fetch data
for entry in team_links:
    url = entry.get("url")
    event_id = extract_id_from_url(url)
    home_team = entry.get("team_1")
    away_team = entry.get("team_2")
    if event_id and home_team and away_team:
        fetch_and_save_lineup(event_id, home_team, away_team)
    else:
        print(f"ID, home team, or away team not found in entry: {entry}")
