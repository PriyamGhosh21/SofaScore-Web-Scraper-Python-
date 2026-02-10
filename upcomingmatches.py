from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Function to fetch up to 10 upcoming matches from Soccer24 using Selenium
def fetch_matches(limit=10):
    # Set up the Selenium driver with the existing Chrome profile
    options = webdriver.ChromeOptions()
    profile_path = "C:/Users/Priyam/AppData/Local/Google/Chrome/User Data/Person 16"  # Replace with your profile path
    options.add_argument(f"user-data-dir={profile_path}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    url = 'https://www.soccer24.com/england/premier-league/fixtures/'
    driver.get(url)

    # Give the page some time to load
    time.sleep(5)  # Adjust as necessary

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    matches = []

    # Find all match divs
    match_divs = soup.find_all('div', class_='event__match')

    for idx, match_div in enumerate(match_divs):
        if idx >= limit:  # Stop after scraping the specified number of matches
            break

        # Extracting date and time
        date_time = match_div.find('div', class_='event__time').text.strip() if match_div.find('div',
                                                                                               class_='event__time') else 'N/A'

        if date_time != 'N/A':
            date, match_time = date_time.split(' ', 1)
            match_date = datetime.strptime(date, "%d.%m.").replace(year=datetime.now().year)
            formatted_date = match_date.strftime("%d/%m/%Y")

            # Combine date and time and parse as a naive datetime
            match_datetime_naive = datetime.strptime(f"{formatted_date} {match_time}", "%d/%m/%Y %H:%M")

            # Localize to GMT+5
            gmt_plus_5 = pytz.timezone('Asia/Kolkata')
            match_datetime_gmt5 = gmt_plus_5.localize(match_datetime_naive)

            # Convert to IST (GMT+5:30)
            gmt_plus_5_30 = pytz.timezone('Asia/Kolkata')
            match_datetime_ist = match_datetime_gmt5.astimezone(gmt_plus_5_30)

            formatted_date_ist = match_datetime_ist.strftime("%d/%m/%Y")
            formatted_time_ist = match_datetime_ist.strftime("%H:%M")
        else:
            formatted_date_ist = 'N/A'
            formatted_time_ist = 'N/A'

        # Extracting home team
        home_team_div = match_div.find('div', class_='event__homeParticipant')
        home_team = home_team_div.text.strip() if home_team_div else 'N/A'

        # Extracting away team
        away_team_div = match_div.find('div', class_='event__awayParticipant')
        away_team = away_team_div.text.strip() if away_team_div else 'N/A'

        # Add match data to the list
        matches.append({
            "date": formatted_date_ist,
            "time": formatted_time_ist,
            "team_1": home_team,
            "team_2": away_team
        })

    driver.quit()  # Close the browser
    return matches


# Function to save matches to a JSON file
def save_to_json(matches, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(matches, json_file, indent=4, ensure_ascii=False)
    print(f"Matches saved to '{filename}'.")


# Function to upload data to Google Sheets (Sheet2)
def upload_to_google_sheets(data, sheet_name, worksheet_name):
    # Define the scope and authenticate with Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)  # Update with your credentials file
    gc = gspread.authorize(credentials)

    try:
        # Open the Google Sheet
        sh = gc.open(sheet_name)
        worksheet = sh.worksheet(worksheet_name)  # Select the specified worksheet

        # Clear the worksheet and update headers
        worksheet.clear()
        headers = ["Date", "Time", "Team 1", "Team 2"]
        worksheet.append_row(headers)

        # Add match data row by row
        for match in data:
            worksheet.append_row([match["date"], match["time"], match["team_1"], match["team_2"]])

        print(f"Data successfully uploaded to Google Sheet '{sheet_name}', Worksheet '{worksheet_name}'.")
    except Exception as e:
        print(f"Error uploading data to Google Sheets: {e}")


# Main execution
if __name__ == "__main__":
    # Step 1: Fetch up to 10 matches
    matches = fetch_matches(limit=10)

    if matches:
        # Step 2: Save matches to JSON
        save_to_json(matches, 'upcoming_matches.json')

        # Step 3: Upload to Google Sheets (Sheet2)
        upload_to_google_sheets(matches, 'EPL Predictor', 'Upcoming Matches')  # Update with your Google Sheet and Worksheet name
    else:
        print("No matches found.")
