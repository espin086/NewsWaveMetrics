import config
import logging
from SQLiteHandler import create_stock_table, upload_stock_to_db, create_news_table

def load_stock_data(stock_data):
    """
    This function loads the dataframe to the database.
    """
    logging.info("Loading Function Initiated")
    print(stock_data)
    # Creating the db and table 
    create_stock_table()
    # Uploading the data to db
    upload_stock_to_db(df = stock_data)

def load_news_data():
    """
    This function loads the JSON files from the processed folder and uploads them to the database.
    """
    logging.info("Main loading function initiated.")
    data = file_handler.load_json_files(directory=config.PROCESSED_DATA_PATH)
    create_news_table()
    check_and_upload_to_db(json_list=data)