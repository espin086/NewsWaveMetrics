import config
import logging
import pprint
from file_handler import FileHandler
from SQLiteHandler import create_stock_table, upload_stock_to_db, create_news_table, upload_news_to_db, create_fred_table, upload_fred_to_db

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
    upload_stock_to_db(df = stock_data)

def load_news_data(search_topic):
    """
    This function loads the JSON files from the processed folder and uploads them to the database.
    """
    logging.info("Main loading function initiated.")
    data = file_handler.load_json_files(directory=config.PROCESSED_DATA_PATH)
    create_news_table()
    upload_news_to_db(json_list=data, search_topic= search_topic)

def load_fred_data(fred_data):
    """
    This function loads the JSON files from the processed folder and uploads them to the database.
    """
    logging.info("Loading Function Initiated")
    create_fred_table()
    upload_fred_to_db(df = fred_data)

# if __name__ == "__main__":
#     load_news_data("Federal Reserve")