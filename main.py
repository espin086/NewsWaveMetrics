import logging
import streamlit as st
import config
import sqlite3
import pandas as pd
from datetime import date, timedelta
from get_stock_data import get_daily_stock_data
from data_transform import DataTransformer
from file_handler import FileHandler
from extract_news import extract
from datetime import datetime 

from config import (
    PROCESSED_DATA_PATH,
    RAW_DATA_PATH,
)
from load import load_stock_data, load_news_data
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from moving_average import moving_average_strategy, plot_stock_data


for key in [
    "data_fetched",
    "news_data_fetched",
    "news_query_result",
    "query_result",
    "displayed_data",
    "displayed_news_data",
]:
    if key not in st.session_state:
        st.session_state[key] = (
            False
            if key == "data_fetched" or key == "news_data_fetched"
            else pd.DataFrame()
        )

file_handler = FileHandler(raw_path=RAW_DATA_PATH, processed_path=PROCESSED_DATA_PATH)


def run_transform():
    DataTransformer(
        raw_path=RAW_DATA_PATH,
        processed_path=PROCESSED_DATA_PATH,
        data=file_handler.import_news_data_from_dir(dirpath=RAW_DATA_PATH),
    ).transform()


def fetch_and_store_stock_data(ticker, start_date, end_date):
    stocks_data = get_daily_stock_data(ticker, start_date, end_date)
    if not stocks_data.empty:
        load_stock_data(stocks_data)
        st.success("Data fetched and stored successfully.")
        return True
    else:
        st.error("No data available for the provided ticker.")
        return False


def fetch_and_store_news_data(news_topic, start_date, end_date):

    if news_topic:
        extract(news_topic, start_date, end_date)
        run_transform()
        load_news_data(news_topic)

        file_handler.delete_local()

        st.success("Search complete!")
        return True
    else:
        st.warning("Please enter News Topic")
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


def query_news_data(news_topic):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(config.DATABASE)

        # Perform SQL query
        query = f"""
            SELECT 
                cast(date as TEXT) as Date,
                title as title,
                top_image as top_image,
                videos as videos,
                url as url,
                short_description as short_description,
                text as text,
                source as source,
                sentiment as sentiment
            FROM ai_safety_news 
            WHERE search_topic = '{news_topic}'
            ORDER BY date DESC
        """
        data = pd.read_sql(query, conn)
        conn.close()
        return data
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Add filters to table", key="add_filter")
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
            st.warning(
                f"No available data for filtering on {column}. Skipping this filter."
            )
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
            user_date_input = right.date_input(
                f"Date range for {column}", value=(min_date, max_date), key=column
            )
            df = df[
                (df[column] >= user_date_input[0]) & (df[column] <= user_date_input[1])
            ]
        else:
            user_text_input = right.text_input(
                f"Substring or regex in {column}",
            )
            if user_text_input:
                df = df[df[column].str.contains(user_text_input)]
    return df


with st.sidebar:
    st.image(
        "https://www.fidelity.co.uk/media/filer_public_thumbnails/PI%20UK/images/sharecast/stocks-hero.jpg__1200x535_q85_subsampling-2.jpg",
        width=350,
    )
    st.title("News Wave Metrics")
    choice = st.radio("Navigation", ["Lookup Stock Data", "Analyze News Sentiment"])
    st.info(
        "A powerful tool for analyzing news sentiment on both national and local stories, allowing users to correlate these stories with their own uploaded metrics, starting with stock market price data. Stay ahead of the curve and make informed decisions with SentimentSync."
    )

if choice == "Lookup Stock Data":
    ticker_input = st.text_input("Enter the Ticker Symbol:", key="ticker_input")

    if st.button("Analyze Stocks"):
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * config.YEARS_OF_NEWS)
        if ticker_input and fetch_and_store_stock_data(
            ticker_input, start_date, end_date
        ):
            st.session_state["data_fetched"] = True
            st.session_state["query_result"] = query_stock_data(ticker_input)

    if st.session_state["data_fetched"]:
        # Apply filters to the dataframe for display
        st.session_state["displayed_data"] = filter_dataframe(
            st.session_state["query_result"]
        )
        st.write("Filtered Table:")
        st.dataframe(st.session_state["displayed_data"])

        # Display moving average window inputs above the graph, in the main page area
        st.write("Graph Controls:")
        short_window = st.slider("Short-term window", 1, 50, 10, key="short_window_new")
        long_window = st.slider("Long-term window", 1, 200, 50, key="long_window_new")

        # Assuming you want to use the original (unfiltered) dataset for the graph
        if not st.session_state["query_result"].empty:
            df_for_graph = st.session_state["query_result"].copy()
            df_for_graph["Date"] = pd.to_datetime(df_for_graph["Date"])
            df_for_graph.set_index("Date", inplace=True)
            signals = moving_average_strategy(df_for_graph, short_window, long_window)
            plot_stock_data(df_for_graph, signals)

elif choice == "Analyze News Sentiment":
    search_input = st.text_input("Enter the News Topic:", key="search_input")

    if st.button("Analyze News"):
        # end_date = date.today()
        # start_date = end_date - timedelta(days=365 * 10)
        end_date_str = "01/03/2024"
        start_date_str = "01/01/2024"

        # Convert strings to datetime objects
        end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")

        # Format datetime objects
        start_date_formatted = start_date.strftime("%d/%m/%Y")
        end_date_formatted = end_date.strftime("%d/%m/%Y")
        if search_input and fetch_and_store_news_data(
            search_input, start_date_formatted, end_date_formatted
        ):
            st.session_state["news_data_fetched"] = True
            st.session_state["news_query_result"] = query_news_data(search_input)

    if st.session_state["news_data_fetched"]:
        st.session_state["displayed_news_data"] = filter_dataframe(
            st.session_state["news_query_result"]
        )
        st.write("Filtered Table:")
        st.dataframe(st.session_state["displayed_news_data"])
