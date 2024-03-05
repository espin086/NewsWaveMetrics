import yfinance as yf
import logging
import config
import pandas as pd
from datetime import date, timedelta


def get_daily_stock_data(tickerSymbol,start_date,end_date):
    """
    This function extracts stocks data from the yfinance library.
    """
    try:
        logging.info(
            "Starting extraction process for ticker: %s",
            tickerSymbol,
        )
        # Defining the ticker symbol
        tickerData = yf.Ticker(tickerSymbol)

        # Getting the data for this ticker
        tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)

        #Getting the desired coulmns
        selected_tickerDf = tickerDf.loc[:, config.SELECTED_COLUMNS]

        # Extracting the date from the "Date" column
        selected_tickerDf["Date"] = pd.to_datetime(selected_tickerDf["Date"], utc=True).dt.date

        # Adding the Ticker Column
        selected_tickerDf["Ticker"] = tickerSymbol

        logging.info(
            "Extraction process completed for ticker: %s",
            tickerSymbol,
        )
    
    except Exception as e:
        logging.error("An error occurred in the extract function: %s", str(e))

    return selected_tickerDf

if __name__ == "__main__":
    logging.info("Application started.")
    end_date = date.today()
    start_date = end_date - timedelta(days=5 * 365)
    stocks_data = get_daily_stock_data("DIS",start_date,end_date)
    print(stocks_data)
    logging.info("Application finished.")