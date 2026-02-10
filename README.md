# Football Match & Player Statistics Automation Pipeline

A comprehensive automated data pipeline designed to scrape, clean, analyze, and visualize football match data and player statistics from Sofascore. This tool automates the entire workflow from data discovery to cloud visualization.

## 🚀 Features

### 🔍 Automated Data Discovery
- **Smart Scraping**: Uses Selenium to navigate Sofascore, handling dynamic content, lazy loading, and "Show More" buttons automatically.
- **Robust Navigation**: Includes retry mechanisms, error handling, and auto-scrolling to ensure all matches for a given date are captured.
- **Flexible Scheduling**: Can process specific dates, user-provided URLs, or default to the most recent matches.

### 📊 Deep Data Extraction
- **Match Analytics**: Extracts detailed match statistics including possession, shots, expected goals (xG), big chances, and more.
- **Player Performance**: Scrapes individual player ratings and stats (goals, assists, tackles, key passes).
- **Hybrid Approach**: Combines UI scraping for match discovery with direct API interception for high-fidelity data extraction.

### 🧹 Data Processing & Cleaning
- **Intelligent Cleaning**: Automated scripts to fix team name discrepancies, handle missing values, and normalize data formats.
- **Data Standardization**: Converts raw JSON data into structured CSVs ready for analysis.
- **Home/Away Correction**: specialized logic to ensure accurate team attribution.

### ☁️ Cloud Integration
- **Google Sheets Sync**: Automatically uploads processed match and player data to designated Google Sheets.
- **Batch Processing**: Handles large volumes of data efficiently using sequential batch execution.

## 🛠️ Tech Stack

- **Python**: Core logic and data processing.
- **Selenium**: Web automation and scraping.
- **Pandas**: Data manipulation and CSV formatting.
- **Google Sheets API (gspread)**: Cloud data integration.
- **Batch Scripting**: Pipeline orchestration.

## 📂 Project Structure

- `finalv6.py`: Main entry point for scraping match URLs.
- `finalv2v2.py`: Extracts detailed statistics and incidents via API endpoints.
- `combine.py` & `json_clean.py`: Aggregates and cleans raw JSON data.
- `gs_sheet.py`: Uploads match statistics to Google Sheets.
- `playerssts.py` & `gs_ply_sts.py`: Scrapes and uploads player-specific statistics.
- `setup_and_run_scripts.bat`: Master orchestration script that runs the full pipeline.

## 📋 Prerequisites

- Python 3.8+
- Google Chrome
- Chrome Driver (compatible with your Chrome version)
- Google Service Account Credentials (`credentials.json`)

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/football-stats-pipeline.git
   cd football-stats-pipeline
   ```

2. **Install Dependencies**
   Run the helper script to check and install missing Python packages:
   ```bash
   python install_dependencies.py
   ```

3. **Setup Credentials**
   Place your Google Service Account `credentials.json` file in the root directory.

## 🚀 Usage

1. **Start the Pipeline**
   Double-click `setup_and_run_scripts.bat` or run it from the terminal:
   ```cmd
   .\setup_and_run_scripts.bat
   ```

2. **Follow On-Screen Prompts**
   - The script may ask for a specific date or URL if it cannot find `previous.csv`.
   - Watch the progress logs as each stage completes (Scraping -> Cleaning -> Uploading).

3. **View Results**
   - Check the `data/output` folder for local CSVs.
   - Open your connected Google Sheet to see the live data populate.

## 🛡️ robust Error Handling
The pipeline includes a `Spinner` class for visual feedback and comprehensive logging in the `log/` directory. If a step fails, the logs provide detailed tracebacks for easy debugging.

---
*Built for the love of the beautiful game and data science.*
