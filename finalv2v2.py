import sys
import time
import json
import re
import os
import logging
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
MAX_RETRIES = 10
RETRY_DELAY = 10  # seconds

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spinner class to show rotating indicator
class Spinner:
    def __init__(self, message="Processing..."):
        self.message = message
        self.spinner = threading.Thread(target=self.spin)
        self.stop_running = threading.Event()

    def spin(self):
        spinner_sequence = ['|', '/', '-', '\\']
        idx = 0
        while not self.stop_running.is_set():
            sys.stdout.write(f"\r{self.message} {spinner_sequence[idx]}")
            sys.stdout.flush()
            idx = (idx + 1) % len(spinner_sequence)
            time.sleep(0.1)

    def start(self):
        self.spinner.start()

    def stop(self):
        self.stop_running.set()
        self.spinner.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')  # Clear the line
        sys.stdout.flush()

# Function to create a valid file name
def create_valid_filename(home_team, away_team, date_str, url):
    if home_team and away_team:
        return f"{home_team.replace(' ', '_')}_VS_{away_team.replace(' ', '_')}_{date_str}.json"
    else:
        url_safe_name = re.sub(r'[^\w]', '_', url)  # Replace non-alphanumeric characters with underscores
        return f"{url_safe_name}_{date_str}.json"

# Function to initialize ChromeDriver
def initialize_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # Run headless Chrome
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-extensions")  # Disable extensions to reduce resource usage
    chrome_options.add_argument("--disable-background-networking")  # Further reduce resource usage
    chrome_options.add_argument("--disable-software-rasterizer")  # Reduce CPU usage
    chrome_options.add_argument("--single-process")  # Run Chrome in single-process mode

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to fetch data from a URL using Selenium with a reusable driver
def fetch_data(driver, url, headless=True):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            driver.get(url)
            time.sleep(5)  # Wait for the page to load
            # Extract JSON data from page source
            try:
                json_data = driver.execute_script("return JSON.parse(document.body.innerText)")
                return json_data
            except Exception as e:
                logging.error(f"Failed to parse JSON data from {url}: {e}")
                return None
        except Exception as e:
            logging.error(f"Connection error for {url}: {e}")
            if headless and retries < 1:  # Only retry with non-headless browser once
                # Retry with a non-headless browser
                logging.info("Retrying with non-headless browser...")
                return fetch_data(driver, url, headless=False)
            else:
                # Wait before retrying
                retries += 1
                if retries < MAX_RETRIES:
                    logging.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
    logging.error(f"Failed to fetch data from {url} after {MAX_RETRIES} attempts.")
    return None

# Function to replace placeholders in data
def replace_placeholders(data, home_team, away_team):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "home":
                data[key] = home_team
            elif key == "away":
                data[key] = away_team
            elif isinstance(value, str):
                value = value.replace("{HOME}", home_team).replace("{AWAY}", away_team)
                data[key] = value
            elif isinstance(value, (dict, list)):
                replace_placeholders(value, home_team, away_team)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, str):
                item = item.replace("{HOME}", home_team).replace("{AWAY}", away_team)
                data[index] = item
            elif isinstance(item, (dict, list)):
                replace_placeholders(item, home_team, away_team)

# Function to extract match ID from URL
def extract_match_id(url):
    match_id_match = re.search(r'id:(\d+)', url)
    if match_id_match:
        return match_id_match.group(1)
    return None

# Read the team_links.json file
def read_team_links(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Directory to save statistics and incidents data
def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)

def main():
    team_links = read_team_links('team_links.json')
    statistics_dir = 'data'
    ensure_directory(statistics_dir)

    # Initialize a single ChromeDriver instance for reuse
    driver = initialize_driver(headless=True)

    for link in team_links:
        url = link.get('url')
        home_team = link.get('team_1', '')
        away_team = link.get('team_2', '')
        match_id = extract_match_id(url)
        date_str = link.get('date')  # Get the date from the team link entry
        if match_id:
            # Statistics URL
            statistics_url = f"https://www.sofascore.com/api/v1/event/{match_id}/statistics"
            incidents_url = f"https://www.sofascore.com/api/v1/event/{match_id}/incidents"

            spinner = Spinner(f"Fetching data for match {home_team} VS {away_team}")
            spinner.start()

            try:
                statistics_data = fetch_data(driver, statistics_url)
                if statistics_data:
                    statistics_data['date'] = date_str
                    replace_placeholders(statistics_data, home_team, away_team)
                    file_name = create_valid_filename(home_team, away_team, date_str, url)
                    file_path = os.path.join(statistics_dir, f"{file_name}_statistics.json")
                    with open(file_path, 'w') as file:
                        json.dump(statistics_data, file, indent=2)
                    logging.info(f"Statistics data for match {home_team} VS {away_team} has been saved to {file_path}")

                incidents_data = fetch_data(driver, incidents_url)
                if incidents_data:
                    incidents_data['date'] = date_str
                    replace_placeholders(incidents_data, home_team, away_team)
                    file_path = os.path.join(statistics_dir, f"{file_name}_incidents.json")
                    with open(file_path, 'w') as file:
                        json.dump(incidents_data, file, indent=2)
                    logging.info(f"Incidents data for match {home_team} VS {away_team} has been saved to {file_path}")

            except Exception as e:
                logging.error(f"An error occurred while fetching data: {e}")

            spinner.stop()
        else:
            logging.error(f"Match ID not found in URL: {url}")

    driver.quit()  # Close the browser instance

    # Ensure the script exits gracefully
    logging.info("All processes completed. Exiting...")
    sys.exit(0)

if __name__ == "__main__":
    main()
