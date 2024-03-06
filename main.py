import logging
import streamlit as st
import config
import sqlite3
import pandas as pd
from datetime import date, timedelta
from get_stock_data import get_daily_stock_data
from load_stock_data import load

logging.basicConfig(level=logging.INFO)

st.title("Fetch and Store Stock Data")

ticker_input = st.text_input("Enter the Ticker Symbol:")

if st.button("Run Search"):
    end_date = date.today()
    start_date = end_date - timedelta(days=5 * 365)
    stocks_data = get_daily_stock_data(ticker_input,start_date,end_date)
    load(stocks_data)
    st.success("Search complete!")

if st.button("Query DB"):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(config.DATABASE)

        # Perform SQL query
        query = """
            SELECT 
                date as Date,
                ticker as Ticker,
                open_price as Open Price,
                high_price as High Price,
                low_price as Low Price,
                closing_price as Closing Price,
                volume as Volume
            FROM stock_data 
            ORDER BY date DESC, ticker DESC
        """
        query_result = pd.read_sql(query, conn)
        conn.close()
        st.write(query_result)

    except Exception as e:
        st.error(f"An error occurred: {e}")