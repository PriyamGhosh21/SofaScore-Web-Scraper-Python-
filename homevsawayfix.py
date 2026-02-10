import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


# Function to scrape the teams' names with headless mode
def scrape_teams(url, meta_data):
    max_retries = 10
    delay_between_retries = 15  # seconds

    # Configure Chrome to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless performance
    chrome_options.add_argument("--start-maximized")  # Set window size for proper rendering

    for attempt in range(max_retries):
        try:
            # Initialize WebDriver with headless option
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url)
            
            # Wait for page to load
            time.sleep(3)

            # Try to find the team names using the new page structure
            try:
                # Find home team - it's in a div with ai_end class
                home_element = driver.find_element(By.CSS_SELECTOR, 'div.ai_end bdi.textStyle_display\\.medium')
                home_team = home_element.text.strip()
                
                # Find away team - it's in a div with ai_start class
                away_element = driver.find_element(By.CSS_SELECTOR, 'div.ai_start bdi.textStyle_display\\.medium')
                away_team = away_element.text.strip()
                
                driver.quit()  # Close the browser session
                
                if home_team and away_team:
                    return home_team, away_team
                else:
                    raise Exception("Team names are empty")

            except Exception as e:
                print(f"New CSS Selector failed. Error: {e}")
                print("Trying fallback method...")

                # Fallback: Find all bdi elements with team names
                try:
                    team_elements = driver.find_elements(By.CSS_SELECTOR, 'bdi[class*="textStyle_display.medium"]')
                    
                    # Filter out non-team text and get unique team names
                    teams = []
                    for element in team_elements:
                        text = element.text.strip()
                        if text and len(text) > 2 and text not in teams:  # Basic validation
                            teams.append(text)
                    
                    if len(teams) >= 2:
                        home_team = teams[0]
                        away_team = teams[1]
                        driver.quit()
                        return home_team, away_team
                    
                except Exception as fallback_error:
                    print(f"Fallback method also failed: {fallback_error}")
                
                driver.quit()

        except (TimeoutException, WebDriverException) as e:
            print(f"Error fetching teams from {url}: {e}")
            print(f"Retrying in {delay_between_retries} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(delay_between_retries)

        finally:
            if 'driver' in locals():  # Ensure the driver quits even if an exception occurs
                driver.quit()

    print(f"Failed to fetch teams from {url} after {max_retries} attempts.")
    return None, None


# Function to update the home and away team values in the JSON metadata
def update_meta_data(meta_data, file_path, file, data):
    url = meta_data.get('url')
    if url:
        print(f"Processing URL: {url}")
        home_team, away_team = scrape_teams(url, meta_data)

        # Update meta_data if team names are successfully scraped
        if home_team and away_team:
            meta_data['home'] = home_team
            meta_data['away'] = away_team
            print(f"Updated {file_path}: Home - {home_team}, Away - {away_team}")

            # Move pointer to beginning and overwrite the file with updated content
            file.seek(0)
            json.dump(data, file, indent=4)  # Write the entire data structure back
            file.truncate()  # Remove any leftover content from previous version


# Function to process a single JSON file
def process_json_file(file_path):
    with open(file_path, 'r+', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Skipping file {file_path}: JSON decode error: {e}")
            return

        # Check if the data is a list or dictionary
        if isinstance(data, list):
            # Search for 'meta_data' inside the list
            for item in data:
                if isinstance(item, dict) and 'meta_data' in item:
                    update_meta_data(item['meta_data'], file_path, file, data)
        elif isinstance(data, dict) and 'meta_data' in data:
            update_meta_data(data['meta_data'], file_path, file, data)
        else:
            print(f"Skipping file {file_path}: Invalid JSON structure. File content: {data}")


# Function to process all JSON files in the directory
def process_all_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            process_json_file(file_path)


# Main execution
if __name__ == "__main__":
    # Define the directory where your JSON files are located
    json_directory = r"data"

    process_all_json_files(json_directory)
