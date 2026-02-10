from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import threading
import time
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import sys

# Spinner class to show a rotating indicator in the console
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

# List of team names (full names and their variations) for matching purposes
team_names = {
     "Arsenal": ["Arsenal"],
    "Aston Villa": ["Aston Villa"],
    "Bournemouth": ["Bournemouth"],
    "Brentford": ["Brentford"],
    "Brighton & Hove Albion": ["Brighton", "Brighton & Hove Albion"],
    "Chelsea": ["Chelsea"],
    "Crystal Palace": ["Crystal Palace"],
    "Everton": ["Everton"],
    "Fulham": ["Fulham"],
    "Ipswich Town": ["Ipswich", "Ipswich Town"],
    "Leicester City": ["Leicester", "Leicester City"],
    "Liverpool": ["Liverpool"],
    "Manchester City": ["Man City", "Manchester City"],
    "Manchester United": ["Man Utd", "Manchester United"],
    "Newcastle United": ["Newcastle", "Newcastle United"],
    "Nottingham Forest": ["Forest", "Nottingham Forest"],
    "Southampton": ["Southampton"],
    "Tottenham Hotspur": ["Tottenham", "Tottenham Hotspur"],
    "West Ham United": ["West Ham", "West Ham United"],
    "Wolverhampton": ["Wolves", "Wolverhampton"]
}

# Modified helper function for more robust team validation and matching
def is_valid_team(scraped_team):
    for team, aliases in team_names.items():
        if scraped_team in aliases:
            print(f"DEBUG: Validated team name: '{scraped_team}' matches with '{team}'")
            return True, team  # Return both validation result and canonical team name
    print(f"DEBUG: Invalid team name found: '{scraped_team}'")
    return False, None

# Updated function to find matches using the new HTML structure
def find_matches():
    matches = []
    try:
        # Find all match container elements (anchor tags with data-testid="event_cell")
        print(f"DEBUG: Looking for match elements with XPath: //a[@data-testid='event_cell']")
        match_elements = driver.find_elements(By.XPATH, "//a[@data-testid='event_cell']")
        print(f"DEBUG: Found {len(match_elements)} match elements on the page")
        
        for i, element in enumerate(match_elements):
            href = element.get_attribute('href')
            print(f"DEBUG: Processing match element #{i+1}, href: {href}")
            
            try:
                # Extract the left team name
                print(f"DEBUG: Looking for left team with CSS selector: [data-testid='left_team'] bdi")
                left_team_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='left_team'] bdi")
                left_team = left_team_elem.text.strip()
                print(f"DEBUG: Left team found: '{left_team}'")
                
                # Extract the right team name
                print(f"DEBUG: Looking for right team with CSS selector: [data-testid='right_team'] bdi")
                right_team_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='right_team'] bdi")
                right_team = right_team_elem.text.strip()
                print(f"DEBUG: Right team found: '{right_team}'")
                
                # Validate both team names and get canonical names
                left_valid, left_canonical = is_valid_team(left_team)
                right_valid, right_canonical = is_valid_team(right_team)
                
                if left_valid and right_valid:
                    print(f"DEBUG: Valid match found: {left_canonical} vs {right_canonical}")
                    matches.append({
                        "team_1": left_canonical,
                        "team_2": right_canonical,
                        "raw_team_1": left_team,
                        "raw_team_2": right_team,
                        "url": href
                    })
                else:
                    print(f"DEBUG: Match skipped - team validation failed: {left_team} vs {right_team}")
            except NoSuchElementException as e:
                print(f"DEBUG: Failed to extract team names for match #{i+1}: {str(e)}")
                # Try alternative selectors
                print(f"DEBUG: Trying alternative selectors...")
                try:
                    html = element.get_attribute('innerHTML')
                    print(f"DEBUG: Element HTML: {html[:200]}...")  # Print truncated HTML for debugging
                except:
                    print(f"DEBUG: Could not get innerHTML")
                continue
    except NoSuchElementException as e:
        print(f"DEBUG: Error finding match elements: {str(e)}")
    
    print(f"DEBUG: Total valid matches found: {len(matches)}")
    return matches

# Load missing matches data from JSON file
print("DEBUG: Loading missing_matches.json")
with open('missing_matches.json', 'r') as f:
    missing_matches = json.load(f)
print(f"DEBUG: Loaded {len(missing_matches)} missing matches from file")

# Get today's date in the required format
today_date_str = datetime.now().strftime('%Y-%m-%d')
print(f"DEBUG: Today's date: {today_date_str}")

# Set up Chrome options to use an existing user profile
print("DEBUG: Setting up Chrome options")
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:\\Users\\Priyam\\AppData\\Local\\Google\\Chrome\\User Data")  # Update as needed
chrome_options.add_argument("--profile-directory=Person 1")  # Change to your profile directory
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Set up the WebDriver (update chromedriver path as necessary)
print("DEBUG: Initializing WebDriver")
service = Service(r'chromedriver-win64\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

results = []
spinner = Spinner("Searching for match links")
spinner.start()

try:
    for idx, match in enumerate(missing_matches):
        date_str = match['date']
        print(f"\nDEBUG: Processing match {idx+1}/{len(missing_matches)}: Date {date_str}")

        # Skip matches for today's date
        if date_str == today_date_str:
            print(f"DEBUG: Skipping match on today's date: {date_str} for {match['home_team']} vs {match['away_team']}")
            continue

        home_team = match['home_team']
        away_team = match['away_team']
        print(f"DEBUG: Looking for match: {home_team} vs {away_team}")

        # Build the URL for the match date (e.g., https://www.sofascore.com/football/2025-03-04)
        url = f"https://www.sofascore.com/football/{date_str}"
        print(f"DEBUG: Opening URL: {url}")
        driver.get(url)

        # Wait for 10 seconds to allow the page to load
        print(f"DEBUG: Waiting for page to load (10 seconds)")
        time.sleep(10)
        
        print(f"DEBUG: Current page title: {driver.title}")
        print(f"DEBUG: Current URL: {driver.current_url}")

        # Extract all match elements using the new HTML structure
        print(f"DEBUG: Calling find_matches() function")
        page_matches = find_matches()
        print(f"DEBUG: Checking {len(page_matches)} matches against target: {home_team} vs {away_team}")
        
        match_found = False
        for m in page_matches:
            # Check if both teams match (order independent)
            teams_canonical = [m['team_1'], m['team_2']]
            teams_raw = [m['raw_team_1'], m['raw_team_2']]
            
            print(f"DEBUG: Comparing canonical teams {teams_canonical} with {home_team} and {away_team}")
            print(f"DEBUG: Raw team names on website: {teams_raw}")
            
            # Check for match with canonical names
            if (home_team in teams_canonical and away_team in teams_canonical) or \
               (home_team in team_names.get(teams_canonical[0], []) and away_team in team_names.get(teams_canonical[1], [])) or \
               (home_team in team_names.get(teams_canonical[1], []) and away_team in team_names.get(teams_canonical[0], [])):
                print(f"DEBUG: Match found! {home_team} vs {away_team} at URL: {m['url']}")
                results.append({
                    "team_1": home_team,
                    "team_2": away_team,
                    "url": m['url'],
                    "date": date_str
                })
                match_found = True
                break
        
        if not match_found:
            print(f"DEBUG: No match found for {home_team} vs {away_team} on {date_str}")
finally:
    spinner.stop()

# Save the found matches to a JSON file
print(f"DEBUG: Saving {len(results)} found matches to team_links.json")
with open('team_links.json', 'w') as f:
    json.dump(results, f, indent=4)

print("Match data saved to team_links.json")

# Close the browser
print("DEBUG: Closing browser")
driver.quit()
