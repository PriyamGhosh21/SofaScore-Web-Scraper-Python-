import json
import os
import time  # For adding delay between retries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define the paths
team_links_path = r'team_links.json'  # Path to team_links.json
data_dir = r'data'  # Path to the directory containing the JSON files

# Setup Chrome options
chrome_options = Options()

# chrome_options.add_argument("--headless")  # Run headless for non-GUI operations

# Setup the webdriver (ensure you have the appropriate chromedriver version installed)
service = Service('chromedriver-win64/chromedriver.exe')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()

# Load the team links JSON
with open(team_links_path, 'r') as f:
    team_links = json.load(f)

# Function to scrape the data with retries
def scrape_match_data(url, team_1, team_2, match_date, json_file_path):
    retries = 0
    max_retries = 1
    delay = 10  # Delay between retries in seconds

    while retries < max_retries:
        try:
            # Navigate to the match URL
            driver.get(url)
            
            # Wait for page to load
            time.sleep(3)

            # Scroll down by 100 pixels to load the necessary elements
            driver.execute_script("window.scrollBy(0, 100);")

            # Wait for the team average rating elements to be present (new structure)
            # Team ratings have class "Text jwYwht" with role="meter" and color="onSurface.nLv1"
            rating_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.Text.jwYwht[role='meter'][color='onSurface.nLv1']"))
            )
            
            # The first element is home team (left), second is away team (right)
            if len(rating_elements) >= 2:
                left_avg_rating = rating_elements[0].get_attribute("aria-valuenow") or rating_elements[0].text
                right_avg_rating = rating_elements[1].get_attribute("aria-valuenow") or rating_elements[1].text
            else:
                raise Exception(f"Expected 2 rating elements, but found {len(rating_elements)}")

            # Load the existing JSON data
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)

            # Check if the JSON data is a list, and append the ratings data
            if isinstance(json_data, list):
                ratings_data = {
                    'key': 'ratings',
                    'name': 'sofascore Rating',
                    'homeValue': left_avg_rating,
                    'awayValue': right_avg_rating
                }
                json_data.append(ratings_data)

                # Save the updated list back to the file
                with open(json_file_path, 'w') as f:
                    json.dump(json_data, f, indent=4)

                print(f"Updated data for {team_1} vs {team_2} on {match_date}.")
                return  # Exit the loop and function after successful data fetch

            else:
                print(f"Unexpected JSON format for {team_1} vs {team_2} on {match_date}. Expected a list.")
                return

        except Exception as e:
            retries += 1
            print(f"Error on attempt {retries}/{max_retries} for {team_1} vs {team_2} on {match_date}: {e}")
            if retries < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # Wait before retrying
            else:
                print(f"Failed to fetch data after {max_retries} attempts for {team_1} vs {team_2} on {match_date}.")

# Iterate through each match in team_links.json
for match in team_links:
    team_1 = match['team_1'].replace(" ", "_")
    team_2 = match['team_2'].replace(" ", "_")
    match_date = match['date']
    url = match['url']

    # Construct the JSON file name based on the team names and date
    json_file_name = f"{team_1}_VS_{team_2}_{match_date}.json_combined.json"
    json_file_path = os.path.join(data_dir, json_file_name)

    # Check if the file exists before proceeding
    if os.path.exists(json_file_path):
        scrape_match_data(url, team_1, team_2, match_date, json_file_path)
    else:
        print(f"File not found for {team_1} vs {team_2} on {match_date}.")

# Quit the driver after all iterations are done
driver.quit()
