from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime
import pytz

def fetch_matches():
    options = Options()
    profile_path = "C:/Users/Priyam/AppData/Local/Google/Chrome/User Data/Person 16"
    options.add_argument(f"user-data-dir={profile_path}")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    url = 'https://www.soccer24.com/england/premier-league/results/'
    driver.get(url)
    
    time.sleep(10)  # Allow page to load
    
    matches = []
    header = {'Date': 'Date', 'Teams': 'Teams', 'Goals': 'Goals'}
    first_match = True
    
    match_divs = driver.find_elements(By.CLASS_NAME, 'event__match')
    
    for match_div in match_divs:
        try:
            date_time_element = match_div.find_element(By.CLASS_NAME, 'event__time')
            date_time = date_time_element.text.strip() if date_time_element else 'N/A'
        except:
            print("Div event__time not found!")
            date_time = 'N/A'
        
        if date_time != 'N/A':
            date, match_time = date_time.split(' ', 1)
            match_date = datetime.strptime(date, "%d.%m.")
            match_date = match_date.replace(year=2024 if match_date.month >= 8 else 2025)
            formatted_date = match_date.strftime("%Y-%m-%d")
            
            match_datetime_naive = datetime.strptime(f"{formatted_date} {match_time}", "%Y-%m-%d %H:%M")
            gmt_plus_5_30 = pytz.timezone('Asia/Kolkata')
            match_datetime_ist = gmt_plus_5_30.localize(match_datetime_naive)
            formatted_date_ist = match_datetime_ist.strftime("%Y-%m-%d")
        else:
            formatted_date_ist = 'N/A'
        
        try:
            home_team = match_div.find_element(By.CLASS_NAME, 'event__homeParticipant').text.strip()
        except:
            print("Div event__homeParticipant not found!")
            home_team = 'N/A'
        
        try:
            away_team = match_div.find_element(By.CLASS_NAME, 'event__awayParticipant').text.strip()
        except:
            print("Div event__awayParticipant not found!")
            away_team = 'N/A'
        
        try:
            score_home = match_div.find_element(By.CSS_SELECTOR, 'span[data-side="1"]').text.strip()
        except:
            print("Div event__score--home not found!")
            score_home = "N/A"
        
        try:
            score_away = match_div.find_element(By.CSS_SELECTOR, 'span[data-side="2"]').text.strip()
        except:
            print("Div event__score--away not found!")
            score_away = "N/A"
        
        if score_home != 'N/A' and score_away != 'N/A':
            if not first_match:
                matches.append(header)
            first_match = False
            
            matches.append({'Date': formatted_date_ist, 'Teams': home_team, 'Goals': score_home})
            matches.append({'Date': formatted_date_ist, 'Teams': away_team, 'Goals': score_away})
            matches.append({'Date': '', 'Teams': '', 'Goals': ''})
    
    driver.quit()
    return matches

def save_to_excel(matches, filename):
    df = pd.DataFrame(matches)
    if 'Time' in df.columns:
        df.drop(columns=['Time'], inplace=True)
    df.to_excel(filename, index=False)

def main():
    matches = fetch_matches()
    if matches:
        save_to_excel(matches, 'results.xlsx')
        print("Matches saved to 'results.xlsx'.")
    else:
        print("No matches found.")

if __name__ == "__main__":
    main()
