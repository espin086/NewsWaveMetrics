import config
import logging
from SQLiteHandler import create_stock_table, upload_stock_to_db

def load(stock_data):
    """
    This function loads the dataframe to the database.
    """
    logging.info("Loading Function Initiated")
    print(stock_data)
    # Creating the db and table 
    create_stock_table()
    # Uploading the data to db
    upload_stock_to_db(df = stock_data)

