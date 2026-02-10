import os
import json

def clean_json(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Initialize the output list and flags for the first occurrences of statistics
    cleaned_data = []
    statistics_found = {
        "ballPossession": False,
        "totalShotsOnGoal": False,
        "goalkeeperSaves": False,
        "cornerKicks": False,
        "totalTackle": False,
        "fouls": False,
        "yellowCards": False,
        "redCards": False,
        "shotsOnGoal": False,
        "offsides": False,
        "goalKicks": False,
        "throwIns": False,
        "expectedGoals": False,
        "bigChanceCreated": False,
        "bigChanceMissed" : False

    }

    # Process incidents
    if 'incidents' in data and isinstance(data['incidents'], list):
        for entry in data['incidents']:
            if isinstance(entry, dict) and entry.get("text") == "FT":
                cleaned_entry = {
                    "addedTime": entry.get("addedTime"),
                    "awayScore": entry.get("awayScore"),
                    "homeScore": entry.get("homeScore"),
                    "incidentType": entry.get("incidentType"),
                    "isLive": entry.get("isLive"),
                    "reversedPeriodTime": entry.get("reversedPeriodTime"),
                    "text": entry.get("text"),
                    "time": entry.get("time")
                }
                cleaned_data.append(cleaned_entry)

    # Process statistics
    if 'statistics' in data and isinstance(data['statistics'], dict) and 'statistics' in data['statistics']:
        statistics_list = data['statistics']['statistics']
        for group in statistics_list:
            if 'groups' in group:
                for stat_group in group['groups']:
                    if 'statisticsItems' in stat_group:
                        group_name = stat_group.get('groupName')
                        for item in stat_group['statisticsItems']:
                            key = item.get("key")
                            if group_name == "Match overview" and key in statistics_found and not statistics_found[key]:
                                cleaned_data.append(item)
                                statistics_found[key] = True
                            elif group_name == "Shots" and key == "shotsOnGoal" and not statistics_found["shotsOnGoal"]:
                                cleaned_data.append(item)
                                statistics_found["shotsOnGoal"] = True
                            elif group_name == "Attack" and key == "offsides" and not statistics_found["offsides"]:
                                cleaned_data.append(item)
                                statistics_found["offsides"] = True
                            elif group_name == "Attack" and key == "bigChanceMissed" and not statistics_found["bigChanceMissed"]:
                                cleaned_data.append(item)
                                statistics_found["bigChanceMissed"] = True
                            elif group_name == "Goalkeeping" and key == "goalKicks" and not statistics_found["goalKicks"]:
                                cleaned_data.append(item)
                                statistics_found["goalKicks"] = True
                            elif group_name == "Passes" and key == "throwIns" and not statistics_found["throwIns"]:
                                cleaned_data.append(item)
                                statistics_found["throwIns"] = True

    # Process meta_data
    if 'meta_data' in data and isinstance(data['meta_data'], dict):
        cleaned_data.append({
            "meta_data": {
                "home": data['meta_data'].get("home"),
                "away": data['meta_data'].get("away"),
                "date": data['meta_data'].get("date"),
                "url": data['meta_data'].get("url")
            }
        })

    # Save the cleaned data to the output file
    with open(output_file, 'w') as f:
        json.dump(cleaned_data, f, indent=4)

def process_all_json_files(directory):
    # List all JSON files in the data directory
    files = [f for f in os.listdir(directory) if f.endswith('.json')]

    for file in files:
        input_path = os.path.join(directory, file)
        output_path = os.path.join(directory, file)  # Output file with the same name

        print(f"Processing file: {input_path}")

        # Clean the JSON file
        clean_json(input_path, output_path)

        # Delete the input file after processing
        # os.remove(input_path)
        # print(f"Deleted file: {input_path}")

# Example usage
data_directory = r'data'  # Directory containing JSON files
process_all_json_files(data_directory)
