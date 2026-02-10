from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import threading
import sys
import csv
import os
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

# Read and display ASCII art from a file
with open('repo.txt', 'r') as file:
    ascii_art = file.read()
print(ascii_art)

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
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

# Function to get user input with a timeout and countdown
def get_user_input(prompt, timeout=30):
    print(prompt)
    user_input = []
    input_received = threading.Event()

    def input_thread():
        try:
            result = input()
            user_input.append(result)
            input_received.set()
        except:
            pass

    thread = threading.Thread(target=input_thread)
    thread.daemon = True  # Make thread daemon so it doesn't block program exit
    thread.start()
    
    # Countdown display
    start_time = time.time()
    while not input_received.is_set():
        elapsed = int(time.time() - start_time)
        remaining = timeout - elapsed
        
        if remaining <= 0:
            # Timeout occurred
            print(f"\n\nTimeout! No response received within {timeout} seconds.")
            print("Using automatic date (yesterday)...")
            return None
        
        # Show countdown every second
        sys.stdout.write(f"\rTime remaining: {remaining} seconds... ")
        sys.stdout.flush()
        time.sleep(1)
    
    # Clear countdown line
    sys.stdout.write('\r' + ' ' * 50 + '\r')
    sys.stdout.flush()
    
    # Input was received
    return user_input[0] if user_input else ""

# Function to get URL from user
def get_url_from_user():
    user_url = get_user_input("No team names found. Please paste the URL to use:")
    return user_url if user_url else None

# Function to read dates from previous.csv
def read_dates_from_csv():
    """Read dates from previous.csv file if it exists"""
    try:
        if os.path.exists('previous.csv'):
            dates = []
            with open('previous.csv', 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if row:  # Skip empty rows
                        date_str = row[0].strip()
                        # Try to parse the date to validate it
                        try:
                            datetime.strptime(date_str, '%Y-%m-%d')
                            dates.append(date_str)
                        except ValueError:
                            print(f"Skipping invalid date format: {date_str}")
            
            if dates:
                print(f"Found previous.csv with {len(dates)} date(s)")
                return dates
        return None
    except Exception as e:
        print(f"Error reading previous.csv: {e}")
        return None

# Get the date to use for the URL
def get_date_url(timeout=30):
    user_choice = get_user_input(
        "Do you want to use the current date (press Enter) or a specific date (enter date in YYYY-MM-DD format)?",
        timeout=timeout)

    if user_choice:
        try:
            selected_date = datetime.strptime(user_choice, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Using today's date.")
            selected_date = datetime.now()
    else:
        selected_date = datetime.now() - timedelta(days=1)

    formatted_date = selected_date.strftime('%Y-%m-%d')
    url = f"https://www.sofascore.com/football/{formatted_date}"

    if not user_choice:  # If automatic date is used (empty string or None)
        print(f"Automatic Date: {formatted_date}")
        print(f"Formed URL: {url}")

    return url, formatted_date

# List of team names to look for (full names and short forms)
# TEAM VALIDATION DISABLED - All matches will be scraped
# team_names = {
#     "Arsenal": ["Arsenal"],
#     "AFC Bournemouth": ["Bournemouth", "AFC Bournemouth"],
#     "Aston Villa": ["Aston Villa"],
#     "Brentford": ["Brentford"],
#     "Brighton & Hove Albion": ["Brighton", "Brighton & Hove Albion"],
#     "Burnley": ["Burnley"],
#     "Chelsea": ["Chelsea"],
#     "Crystal Palace": ["Crystal Palace"],
#     "Everton": ["Everton"],
#     "Fulham": ["Fulham"],
#     "Leeds United": ["Leeds", "Leeds United"],
#     "Leicester City": ["Leicester", "Leicester City"],
#     "Liverpool": ["Liverpool"],
#     "Manchester City": ["Man City", "Manchester City"],
#     "Manchester United": ["Man Utd", "Manchester United"],
#     "Newcastle United": ["Newcastle", "Newcastle United"],
#     "Nottingham Forest": ["Forest", "Nottingham Forest"],
#     "Sunderland": ["Sunderland"],
#     "Tottenham Hotspur": ["Tottenham", "Tottenham Hotspur"],
#     "West Ham United": ["West Ham", "West Ham United"]
# }

# Helper function to validate scraped team names
# DISABLED - Team validation is turned off
# def is_valid_team(scraped_team):
#     for aliases in team_names.values():
#         if scraped_team in aliases:
#             return True
#     return False

# Function to click on the favourites tab
def click_favourites_tab():
    try:
        # Wait for the page to load and find the favourites button
        wait = WebDriverWait(driver, 15)
        
        # Try multiple possible selectors for the favourites tab (prioritize data-testid)
        possible_selectors = [
            (By.CSS_SELECTOR, "button[data-testid='tab-favorites']"),
            (By.CSS_SELECTOR, "button[data-testid='tab-favourites']"),
            (By.XPATH, "//button[@data-testid='tab-favorites']"),
            (By.XPATH, "//button[@data-testid='tab-favourites']"),
            (By.XPATH, "//button[contains(text(), 'Favourites')]"),
            (By.XPATH, "//button[contains(text(), 'Favorites')]"),
            (By.XPATH, "//button[@role='tab' and contains(text(), 'Favourites')]"),
            (By.XPATH, "//button[@role='tab' and contains(text(), 'Favorites')]"),
        ]
        
        favourites_button = None
        for by_type, selector in possible_selectors:
            try:
                favourites_button = wait.until(EC.element_to_be_clickable((by_type, selector)))
                break
            except (TimeoutException, NoSuchElementException):
                continue
        
        if favourites_button:
            # Try to click the button
            try:
                favourites_button.click()
                time.sleep(5)  # Wait for content to load
                return True
            except ElementClickInterceptedException:
                # Try JavaScript click if regular click fails
                driver.execute_script("arguments[0].click();", favourites_button)
                time.sleep(5)  # Wait for content to load
                return True
        else:
            return False
            
    except Exception as e:
        return False

# Set up Chrome options to use an existing profile
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:\\Users\\Priyam\\AppData\\Local\\Google\\Chrome\\User Data")
chrome_options.add_argument("--profile-directory=Person 1")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Set up the WebDriver with custom chromedriver path
service = Service(r'chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Configuration
use_favourites = True  # Always click favourites tab
use_team_filter = False  # DISABLED - Team validation is off, all matches will be scraped

# Check for previous.csv first
print("Checking for previous.csv file...")
time.sleep(1)  # Brief pause to check for file

dates_to_process = read_dates_from_csv()

if dates_to_process is None:
    # No previous.csv found, wait 15 seconds for user input
    print("previous.csv not found.")
    print("Waiting 15 seconds for date input...")
    url, date_str = get_date_url(timeout=15)
    dates_to_process = [date_str]
    urls_to_process = [url]
else:
    # Use dates from previous.csv
    urls_to_process = [f"https://www.sofascore.com/football/{date}" for date in dates_to_process]

# Function to load page and click favourites
def load_page_with_favourites(url):
    """Load a page and click favourites tab"""
    max_retries = 20
    retry_delay = 15
    attempts = 0
    
    while attempts < max_retries:
        try:
            driver.get(url)
            time.sleep(3)
            
            if use_favourites:
                click_favourites_tab()
            
            return True
        except Exception as e:
            print(f"Attempt {attempts + 1} failed with error: {e}")
            attempts += 1
            if attempts < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached.")
                return False
    return False

# Function to expand all collapsed sections (leagues/tournaments)
def expand_all_sections():
    try:
        # Try to find and click any "Show more" or expand buttons
        expand_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(text(), 'Show more') or contains(text(), 'Show all') or contains(@aria-label, 'expand')]")
        
        if expand_buttons:
            for btn in expand_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.5)
                except:
                    pass
    except:
        pass

# Function to scroll page to load all matches (for lazy loading)
def scroll_to_load_all_matches():
    try:
        # First, expand any collapsed sections
        expand_all_sections()
        
        # Scroll down multiple times to trigger lazy loading
        for i in range(8):
            driver.execute_script(f"window.scrollTo(0, {(i + 1) * 500});")
            time.sleep(0.3)
            
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    except:
        pass

# Modified function to find team links using the new HTML structure
def find_team_links(apply_filter=True):
    try:
        # Scroll to ensure all matches are loaded
        scroll_to_load_all_matches()
        
        # Locate all match elements by finding anchor tags with data-id attribute
        # that have href containing '/football/match/'
        match_elements = driver.find_elements(By.XPATH, "//a[@data-id and contains(@href, '/football/match/')]")
    except NoSuchElementException:
        print("No match elements found on the page.")
        return {}

    url_to_teams = {}
    
    for element in match_elements:
        link_url = element.get_attribute('href')
        teams_found = []
        
        try:
            # Find all bdi elements with class containing 'textStyle_body.medium' and 'trunc_true'
            # These are the team name elements
            bdi_elements = element.find_elements(By.CSS_SELECTOR, "bdi.textStyle_body\\.medium.trunc_true")
            
            # Extract team names
            for bdi in bdi_elements:
                team_text = bdi.text.strip()
                # Filter out date and status text, only keep team names
                if team_text and not team_text.upper() in ['FT', 'LIVE', 'NS', 'HT', 'AET', 'PEN'] and '/' not in team_text and not team_text.isdigit():
                    teams_found.append(team_text)
        except NoSuchElementException:
            pass
        
        # Skip if no teams found
        if not teams_found:
            continue
        
        # TEAM VALIDATION DISABLED - Add all matches without filtering
        # if apply_filter:
        #     # Only add the match if all scraped teams are valid (i.e. in team_names)
        #     if all(is_valid_team(team) for team in teams_found):
        #         url_to_teams[link_url] = teams_found
        # else:
        #     # No filtering - add all matches
        #     url_to_teams[link_url] = teams_found
        
        # Add all matches without team validation
        url_to_teams[link_url] = teams_found
    
    return url_to_teams

# Main scraping logic - Process each date
results = []

for idx, (url, date_str) in enumerate(zip(urls_to_process, dates_to_process)):
    print(f"\nProcessing date {idx + 1}/{len(dates_to_process)}: {date_str}")
    
    # Load the page
    if not load_page_with_favourites(url):
        print(f"Failed to load page for {date_str}, skipping...")
        continue
    
    # Search for team links
    timeout = 40
    found = False
    retry_attempts = 5
    retry_delay_team_links = 10
    
    spinner = Spinner("Searching for team links")
    spinner.start()
    
    try:
        start_time = time.time()
        while retry_attempts > 0:
            try:
                while time.time() - start_time < timeout:
                    url_to_teams = find_team_links(apply_filter=use_team_filter)
                    if url_to_teams:
                        found = True
                        break
                    time.sleep(10)

                if not found:
                    spinner.stop()
                    custom_url = get_url_from_user() or url
                    driver.get(custom_url)
                    time.sleep(3)
                    if use_favourites:
                        click_favourites_tab()
                    spinner.start()
                    url_to_teams = find_team_links(apply_filter=use_team_filter)

                if url_to_teams:
                    for link_url, teams in url_to_teams.items():
                        if len(teams) > 1:
                            for i in range(len(teams)):
                                for j in range(i + 1, len(teams)):
                                    results.append({
                                        "team_1": teams[i],
                                        "team_2": teams[j],
                                        "url": link_url,
                                        "date": date_str
                                    })
                        else:
                            results.append({
                                "team": teams[0],
                                "url": link_url,
                                "date": date_str
                            })
                    break
                else:
                    raise Exception("No team links found.")

            except Exception as e:
                print(f"An error occurred: {e}")
                retry_attempts -= 1
                if retry_attempts > 0:
                    print(f"Retrying... ({retry_attempts} attempts left)")
                    time.sleep(retry_delay_team_links)
                else:
                    print(f"Failed to find team links for {date_str} after multiple attempts.")
                    break

    finally:
        spinner.stop()

# Export results to JSON if any results were found
if results:
    with open('team_links.json', 'w') as f:
        json.dump(results, f, indent=4)

    print("\nook boss")

    # Create a marker file when the script is done
    with open("finalv6_done.txt", "w") as f:
        f.write("done")
else:
    print("\nNo matches found.")

# Close the browser
driver.quit()

# Exit the script
sys.exit(0)
