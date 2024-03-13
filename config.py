import logging

# === General Configs ===
LOGGING_LEVEL = logging.INFO

# === Database Configs ===
DATABASE = "news_wave_metrics.db"
TABLE_STOCK_DATA = "stock_data"
TABLE_NEWS_DATA = "ai_safety_news"

# === Stock Data Required Columns ===
SELECTED_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]

# === API Configs ===
News_SEARCH_URL = "https://newsnow.p.rapidapi.com/newsv2"
News_SEARCH_X_RAPIDAPI_HOST = "newsnow.p.rapidapi.com"

# Pagination for API calls
PAGES = 10