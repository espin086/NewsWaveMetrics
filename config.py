import logging

# === General Configs ===
LOGGING_LEVEL = logging.INFO

# === Database Configs ===
DATABASE = "news_wave_metrics.db"
TABLT_STOCK_DATA = "stock_data"

# === Stock Data Required Columns ===
SELECTED_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]