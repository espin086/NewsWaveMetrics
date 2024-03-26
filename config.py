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
TABLE_FRED_DATA = "fred"

# === Stock Data Required Columns ===
SELECTED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

# === API Configs ===
News_SEARCH_URL = "https://newsnow.p.rapidapi.com/newsv2"
News_SEARCH_X_RAPIDAPI_HOST = "newsnow.p.rapidapi.com"
TWILIO_PHONE_NUMBER = "+18559673680"
ALERT_PHONE_NUMBER = "+13233330336"


# Pagination for API calls
PAGES = 10
YEARS_OF_NEWS = 10

# ECONOMIC_METRICS_IDS = [ Exchange Rates, Treasury Yields, Fed Funds Rate, CPI (Consumer Price Index), GDP (Gross Domestic Product), Industrial Production, Unemployment Rate, Consumer Sentiment, PPI (Producer Price Index)]
ECONOMIC_METRICS_IDS = [
    "DTWEXBGS",
    "T10Y2Y",
    "DFF",
    "CPIAUCSL",
    "GDP",
    "INDPRO",
    "UNRATE",
    "UMCSENT",
    "PPIACO",
]

OBSERVATION_START = "2014-01-01"
