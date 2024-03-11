import logging
import streamlit as st
import config
import sqlite3
import pandas as pd
from datetime import date, timedelta
from get_stock_data import get_daily_stock_data
from load_stock_data import load
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from moving_average import moving_average_strategy, plot_stock_data


for key in ['data_fetched', 'query_result', 'displayed_data']:
    if key not in st.session_state:
        st.session_state[key] = False if key == 'data_fetched' else pd.DataFrame()

def fetch_and_store_data(ticker, start_date, end_date):
    stocks_data = get_daily_stock_data(ticker, start_date, end_date)
    if not stocks_data.empty:
        load(stocks_data)
        st.success("Data fetched and stored successfully.")
        return True
    else:
        st.error("No data available for the provided ticker.")
        return False

def query_stock_data(ticker_input):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(config.DATABASE)

        # Perform SQL query for the specific ticker
        query = f"""
            SELECT 
                cast(date as TEXT) as Date,
                ticker as Ticker,
                open_price as Open_Price,
                high_price as High_Price,
                low_price as Low_Price,
                closing_price as Closing_Price,
                volume as Volume
            FROM stock_data 
            WHERE ticker = '{ticker_input}'
            ORDER BY date DESC, ticker DESC
        """
        data = pd.read_sql(query, conn)
        conn.close()
        return data
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Add filters to table", key='add_filter')
    if not modify:
        return df
    df = df.copy()
    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col]).dt.date
            except Exception:
                pass

    to_filter_columns = st.multiselect("Filter dataframe on", df.columns)

    for column in to_filter_columns:
        unique_values = df[column].dropna().unique()
        if len(unique_values) == 0:
            st.warning(f"No available data for filtering on {column}. Skipping this filter.")
            continue

        left, right = st.columns((1, 20))
        left.write("↳")
        # Update the rest of your filtering logic here
        if is_categorical_dtype(df[column]) or df[column].nunique() < 15:
            # Ensure that the default list does not contain NaN
            user_cat_input = right.multiselect(
                f"Values for {column}",
                options=unique_values, 
                default=unique_values, 
            )
            df = df[df[column].isin(user_cat_input)]
        elif is_numeric_dtype(df[column]):
            _min = float(df[column].min())
            _max = float(df[column].max())
            step = (_max - _min) / 100
            user_num_input = right.slider(
                f"Values for {column}",
                _min,
                _max,
                (_min, _max),
                step=step,
            )
            df = df[df[column].between(*user_num_input)]
        elif is_datetime64_any_dtype(df[column]):
            min_date = df[column].min()
            max_date = df[column].max()
            user_date_input = right.date_input(f"Date range for {column}", value=(min_date, max_date), key=column)
            df = df[(df[column] >= user_date_input[0]) & (df[column] <= user_date_input[1])]
        else:
            user_text_input = right.text_input(
                f"Substring or regex in {column}",
            )
            if user_text_input:
                df = df[df[column].str.contains(user_text_input)]
    return df

st.title("Store and Visualize Stock Data")
ticker_input = st.text_input("Enter the Ticker Symbol:", key="ticker_input")

if st.button("Analyze"):
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * 10)  # Example: 5 years of data
    if ticker_input and fetch_and_store_data(ticker_input, start_date, end_date):
        st.session_state['data_fetched'] = True
        st.session_state['query_result'] = query_stock_data(ticker_input)

if st.session_state['data_fetched']:
    # Apply filters to the dataframe for display
    st.session_state['displayed_data'] = filter_dataframe(st.session_state['query_result'])
    st.write("Filtered Table:")
    st.dataframe(st.session_state['displayed_data'])

    # Display moving average window inputs above the graph, in the main page area
    st.write("Graph Controls:")
    short_window = st.slider("Short-term window", 1, 50, 10, key="short_window_new")
    long_window = st.slider("Long-term window", 1, 200, 50, key="long_window_new")

    # Assuming you want to use the original (unfiltered) dataset for the graph
    if not st.session_state['query_result'].empty:
        df_for_graph = st.session_state['query_result'].copy()
        df_for_graph['Date'] = pd.to_datetime(df_for_graph['Date'])
        df_for_graph.set_index('Date', inplace=True)
        signals = moving_average_strategy(df_for_graph, short_window, long_window)
        plot_stock_data(df_for_graph, signals)