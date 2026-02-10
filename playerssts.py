import json
import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Load team links from JSON file
with open('team_links.json', 'r') as file:
    team_links = json.load(file)

# Setup WebDriver with specified ChromeDriver path
chrome_driver_path = r'chromedriver-win64\chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument("--disable-popup-blocking")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
driver.maximize_window()

# Define output directory
output_dir = r'data\output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def retry_on_failure(func, *args, **kwargs):
    max_retries = 20
    delay = 15
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (TimeoutException, WebDriverException) as e:
            print(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"All attempts failed for function {func.__name__}")
    return None

def scrape_player_statistics(url, home_team, away_team, date):
    driver.get(url)

    try:
        # Wait for the "Player Statistics" div to be present and clickable
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Player statistics")]'))
        )
        # Find and click the "Player Statistics" div
        player_stats_div = driver.find_element(By.XPATH, '//div[contains(text(), "Player statistics")]')
        player_stats_div.click()

        # Wait for the player statistics table to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table'))
        )
        time.sleep(5)  # Additional wait for the table to load

        # Scrape table data
        table = driver.find_element(By.XPATH, '//table')  # Adjust XPath as needed
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Extract table headers
        headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, 'th')]

        # Include team names and date as additional columns
        headers.extend(['Team', 'Home Team', 'Away Team', 'Date'])

        # Extract table rows
        data = []
        for row in rows[1:]:
            columns = row.find_elements(By.TAG_NAME, 'td')
            row_data = [column.text for column in columns]

            try:
                # Extract the logo and its alt attribute
                logo = row.find_element(By.XPATH, './/img')
                logo_alt = logo.get_attribute('alt')

                # Determine the team based on the logo's alt attribute
                if home_team in logo_alt:
                    team = home_team
                elif away_team in logo_alt:
                    team = away_team
                else:
                    team = 'Unknown'
            except:
                # Default to 'Unknown' if logo cannot be found
                team = 'Unknown'

            # Add team name, home team, away team, and date to each row
            row_data.extend([team, home_team, away_team, date])
            data.append(row_data)

        # Create DataFrame and return
        df = pd.DataFrame(data, columns=headers)
        return df

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_statistics(url, home_team, away_team, date, tab_id):
    driver.get(url)

    try:
        # Wait for the tab button to be present and clickable
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, f'//button[@data-tabid="{tab_id}Group"]'))
        )
        # Find and click the tab button
        tab_button = driver.find_element(By.XPATH, f'//button[@data-tabid="{tab_id}Group"]')
        tab_button.click()

        # Wait for the statistics table to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table'))
        )
        time.sleep(5)  # Additional wait for the table to load

        # Scrape table data
        table = driver.find_element(By.XPATH, '//table')  # Adjust XPath as needed
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Extract table headers
        headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, 'th')]

        # Include team names and date as additional columns
        headers.extend(['Team', 'Home Team', 'Away Team', 'Date'])

        # Extract table rows
        data = []
        for row in rows[1:]:
            columns = row.find_elements(By.TAG_NAME, 'td')
            row_data = [column.text for column in columns]

            try:
                # Extract the logo and its alt attribute
                logo = row.find_element(By.XPATH, './/img')
                logo_alt = logo.get_attribute('alt')

                # Determine the team based on the logo's alt attribute
                if home_team in logo_alt:
                    team = home_team
                elif away_team in logo_alt:
                    team = away_team
                else:
                    team = 'Unknown'
            except:
                # Default to 'Unknown' if logo cannot be found
                team = 'Unknown'

            # Add team name, home team, away team, and date to each row
            row_data.extend([team, home_team, away_team, date])
            data.append(row_data)

        # Create DataFrame and return
        df = pd.DataFrame(data, columns=headers)
        return df

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def process_team_link(team_info):
    url = team_info.get('url')
    home_team = team_info.get('team_1')
    away_team = team_info.get('team_2')
    date = team_info.get('date', 'Unknown Date')  # Extract date from JSON

    if url:
        print(f"Processing {home_team} vs {away_team} ({url})")

        # Create a dictionary to hold DataFrames
        sheets = {}

        df_player = retry_on_failure(scrape_player_statistics, url, home_team, away_team, date)
        if df_player is not None:
            sheets['Player Statistics'] = df_player

        df_attack = retry_on_failure(scrape_statistics, url, home_team, away_team, date, 'attack')
        if df_attack is not None:
            sheets['Attack Statistics'] = df_attack

        df_defence = retry_on_failure(scrape_statistics, url, home_team, away_team, date, 'defence')
        if df_defence is not None:
            sheets['Defence Statistics'] = df_defence

        df_passing = retry_on_failure(scrape_statistics, url, home_team, away_team, date, 'passing')
        if df_passing is not None:
            sheets['Passing Statistics'] = df_passing

        df_duels = retry_on_failure(scrape_statistics, url, home_team, away_team, date, 'duels')
        if df_duels is not None:
            sheets['Duels Statistics'] = df_duels

        df_goalkeeper = retry_on_failure(scrape_statistics, url, home_team, away_team, date, 'goalkeeper')
        if df_goalkeeper is not None:
            sheets['Goalkeeper Statistics'] = df_goalkeeper

        if sheets:
            # Create Excel file with multiple sheets
            filename = f'{home_team} vs {away_team}.xlsx'
            file_path = os.path.join(output_dir, filename)
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                for sheet_name, df in sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Match statistics exported to {file_path}")
        return True
    return False

# Track URLs that failed to scrape
failed_urls = []

# First pass to scrape all URLs
for team_info in team_links:
    if not process_team_link(team_info):
        failed_urls.append(team_info)

# Retry failed URLs if any
if failed_urls:
    print("Retrying failed URLs...")
    for team_info in failed_urls:
        process_team_link(team_info)

# Close the WebDriver
driver.quit()
