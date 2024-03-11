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

if 'data_queried' not in st.session_state:
    st.session_state['data_queried'] = False    

if 'query_result' not in st.session_state:
    st.session_state['query_result'] = pd.DataFrame()

if 'filtered_result' not in st.session_state:
    st.session_state['filtered_result'] = pd.DataFrame()

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    modify = st.checkbox("Add filters")

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
                options=unique_values,  # Use the filtered list of unique values
                default=unique_values,  # Default to all unique values (excluding NaN)
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
    
# Function to fetch or get cached data
def get_or_fetch_data(ticker_input):
    st.session_state.query_result = query_stock_data(ticker_input)
    return st.session_state.query_result

# Function to handle visualization
def handle_visualization(ticker_input):

    df = get_or_fetch_data(ticker_input)

    # User input for moving average window parameters
    short_window = st.slider("Select short-term moving average window:", 1, 50, 10, key="short_window")
    long_window = st.slider("Select long-term moving average window:", 1, 200, 50, key="long_window")

    # Cache the selected data to prevent re-computation
    cache_key = f"{short_window}_{long_window}"
    if cache_key not in st.session_state:
        # Filter data for the selected ticker and cache it
        selected_data = df.copy()
        selected_data = selected_data.set_index("Date")
        signals = moving_average_strategy(selected_data, short_window, long_window)
        st.session_state[cache_key] = (selected_data, signals)

    # Retrieve cached data
    selected_data, signals = st.session_state[cache_key]

    # Display stock data and trading signals
    plot_stock_data(selected_data, signals)

logging.basicConfig(level=logging.INFO)

st.title("Store and Visualize Stock Data")

ticker_input = st.text_input("Enter the Ticker Symbol:")

if st.button("Analyze"):
    if not ticker_input:
        st.error("Please enter a valid Ticker Symbol.")
    else:
        end_date = date.today()
        start_date = end_date - timedelta(days=10 * 365)
        stocks_data = get_daily_stock_data(ticker_input,start_date,end_date)
        if stocks_data.empty:
            st.error("No data is available for this ticker.")
        else:
            load(stocks_data)
            st.success("Search complete!")
            if st.session_state['query_result'].empty:
                st.session_state['data_queried'] = True
                st.session_state['query_result'] = query_stock_data(ticker_input)
        if st.session_state['data_queried']:
            filtered_df = filter_dataframe(st.session_state['query_result'])

            # Check if filters have changed
            if 'filtered_result' not in st.session_state or st.session_state['filtered_result'].shape[0] != filtered_df.shape[0]:
                st.session_state['filtered_result'] = filtered_df

            else:
                st.session_state['filtered_result'] = filtered_df

            st.dataframe(filtered_df)
            handle_visualization(ticker_input)