import logging
from pathlib import Path
import os

# === General Configs ===
LOGGING_LEVEL = logging.INFO

# === Data Configs ===
CWD_PATH = Path(os.getcwd())
RAW_DATA_PATH = Path(f"{CWD_PATH}/temp/data/raw").resolve()
PROCESSED_DATA_PATH = Path(f"{CWD_PATH}/temp/data/processed").resolve()

# === Database Configs ===
DATABASE = "news_wave_metrics.db"
TABLE_STOCK_DATA = "stock_data"
TABLE_NEWS_DATA = "ai_safety_news"

# === Stock Data Required Columns ===
SELECTED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

# === API Configs ===
News_SEARCH_URL = "https://newsnow.p.rapidapi.com/newsv2"
News_SEARCH_X_RAPIDAPI_HOST = "newsnow.p.rapidapi.com"

# Pagination for API calls
PAGES = 15
YEARS_OF_NEWS = 10
