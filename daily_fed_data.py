import argparse
import pandas as pd
from extract_economic_data import extract_all_economic_data
from load import load_fred_data
import sms
import logging
import time
import datetime

logging.basicConfig(level=logging.INFO)


def fetch_and_store_fred_data():
    df = extract_all_economic_data()
    if not df.empty:
        load_fred_data(df)
        logging.info(f"Data fetched and stored successfully.")
        return True
    else:
        logging.info("No data available")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fetch and store Federal Reserve data")
    parser.add_argument(
        "--fetch", action="store_true", help="Fetch and store Federal Reserve data"
    )

    args = parser.parse_args()

    if args.fetch:
        fetch_and_store_fred_data()


if __name__ == "__main__":
    while True:
        try:
            current_time = datetime.datetime.now()
            current_time = datetime.datetime.now()
            if current_time.weekday() < 5 and 6 <= current_time.hour < 18:
                main()
                sms.send_sms(
                    "StockHunter: SUCCESS - Federal Reserve data fetched and stored successfully."
                )
            time.sleep(3600)

        except Exception as e:
            sms.send_sms(
                "StockHunter: FAILED - Federal Reserve NOT data fetched and stored successfully."
            )
