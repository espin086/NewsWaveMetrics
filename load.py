import config
import logging
import pprint
from file_handler import FileHandler
import get_stock_data
import extract_economic_data
from SQLiteHandler import (
    create_stock_table,
    upload_stock_to_db,
    create_news_table,
    upload_news_to_db,
    create_fred_table,
    upload_fred_to_db,
)

pp = pprint.PrettyPrinter(indent=4)
logging.basicConfig(
    level=config.LOGGING_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = FileHandler(
    raw_path=config.RAW_DATA_PATH, processed_path=config.PROCESSED_DATA_PATH
)


def load_stock_data(stock_data):
    """
    This function loads the dataframe to the database.
    """
    logging.info("Loading Function Initiated")
    # Creating the db and table
    create_stock_table()
    # Uploading the data to db
    upload_stock_to_db(df=stock_data)


def load_news_data(search_topic):
    """
    This function loads the JSON files from the processed folder and uploads them to the database.
    """
    logging.info("Main loading function initiated.")
    data = file_handler.load_json_files(directory=config.PROCESSED_DATA_PATH)
    create_news_table()
    upload_news_to_db(json_list=data, search_topic=search_topic)


def load_fred_data(fred_data):
    """
    This function loads the JSON files from the processed folder and uploads them to the database.
    """
    logging.info("Loading Function Initiated")
    create_fred_table()

    upload_fred_to_db(df=fred_data)


def get_all_stock_data():
    """Get all stock data from many tickers"""
    # Loading All Stock Data
    TICKERS = config.TICKERS
    for ticker in TICKERS:
        logging.info("Extracting data for ticker: %s", ticker)
        stock_data = get_stock_data.get_daily_stock_data(
            tickerSymbol=ticker,
            start_date=config.OBSERVATION_START,
            end_date=config.OBSERVATION_END,
        )
        load_stock_data(stock_data)
        logging.info("Data for ticker: %s loaded successfully", ticker)


def main():
    """Loads all stock data from large list of stock tickers. Also pulls all economic data"""
    logging.info("Extracting all stock data")
    get_all_stock_data()
    # Load all Federal Reserve Economic Data
    logging.info("Extracting all economic data")
    df_all_econ = extract_economic_data.extract_all_economic_data()
    load_fred_data(df_all_econ)
    logging.info("All economic data loaded successfully")


if __name__ == "__main__":
    main()
