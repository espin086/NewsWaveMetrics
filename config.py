import logging

# === General Configs ===
LOGGING_LEVEL = logging.INFO

# === Database Configs ===
DATABASE = "news_wave_metrics.db"
TABLE_STOCK_DATA = "stock_data"

# === Stock Data Required Columns ===
SELECTED_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]