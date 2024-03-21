import logging
import sqlite3
import config
from sentiment_analysis import analyze_sentiment

def create_stock_table():
    """Create the database if it doesn't exist."""
    logging.info("Checking and creating database if not present.")
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    try:
        c.execute(
            f"""CREATE TABLE IF NOT EXISTS {config.TABLE_STOCK_DATA}
                    (date TEXT,
                    ticker TEXT,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    closing_price REAL,
                    volume REAL,
                    PRIMARY KEY (date, ticker)
                    )"""
        )
        conn.commit()
        logging.info(
            "Successfully created or ensured the table %s exists.",
            config.TABLE_STOCK_DATA,
        )
    except Exception as e:
        logging.error("Failed to create table: %s", e)
    finally:
        conn.close()

def create_news_table():
    """Create the database if it doesn't exist."""
    logging.info("Checking and creating database if not present.")
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    try:
        c.execute(
            f"""CREATE TABLE IF NOT EXISTS {config.TABLE_NEWS_DATA}
                    (search_topic TEXT,
                    title TEXT,
                    top_image TEXT,
                    videos TEXT,
                    url TEXT,
                    date TEXT,
                    short_description TEXT,
                    text TEXT,
                    source TEXT,
                    sentiment TEXT,
                    sentiment_score REAL,
                    PRIMARY KEY (title, date)
                    )"""
        )
        conn.commit()
        logging.info(
            "Successfully created or ensured the table %s exists.",
            config.TABLE_NEWS_DATA,
        )
    except Exception as e:
        logging.error("Failed to create table: %s", e)
    finally:
        conn.close()

def create_fred_table():
    """Create the database if it doesn't exist."""
    logging.info("Checking and creating database if not present.")
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    try:
        c.execute(
            f"""CREATE TABLE IF NOT EXISTS {config.TABLE_FRED_DATA}
                    (date TEXT,
                    exchange_rates REAL,
                    treasury_yields REAL,
                    fed_funds_rate REAL,
                    consumer_price_index REAL,
                    GDP  REAL,
                    industrial_production REAL,
                    unemployment_rate REAL,
                    consumer_sentiment REAL,
                    producer_price_index REAL,
                    PRIMARY KEY (date)
                    )"""
        )
        conn.commit()
        logging.info(
            "Successfully created or ensured the table %s exists.",
            config.TABLE_FRED_DATA,
        )
    except Exception as e:
        logging.error("Failed to create table: %s", e)
    finally:
        conn.close()

def upload_stock_to_db(df):
    """Check if the primary key exists in the database and upload data if not."""
    logging.info("Starting upload to database.")
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    for _, row in df.iterrows():
        try:
            date_value = row.get("Date", "")
            ticker_value = row.get("Ticker", "")

            # Check if the primary key (date, ticker) exists in the database
            c.execute(
                f"SELECT * FROM {config.TABLE_STOCK_DATA} WHERE date=? AND ticker=?",
                (date_value, ticker_value),
            )
            result = c.fetchone()

            if result:
                logging.warning(
                    "%s %s already in the database, skipping...", date_value, ticker_value
                )
            else:
                # Insert new row into the database
                c.execute(
                    f"INSERT OR REPLACE INTO {config.TABLE_STOCK_DATA} (date, ticker, open_price, high_price, low_price, closing_price, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        date_value,
                        ticker_value,
                        row.get("Open", ""),
                        row.get("High", ""),
                        row.get("Low", ""),
                        row.get("Close", ""),
                        row.get("Volume", ""),
                    ),
                )
                conn.commit()
                logging.info(
                    "UPLOADED: %s %s uploaded to the database", date_value, ticker_value
                )
        except Exception as e:
            logging.error("Skipping row due to error: %s", e)

    conn.close()

def upload_news_to_db(json_list, search_topic):
    """Check if the primary key exists in the database and upload data if not."""
    logging.info("Starting upload to database.")
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    for item in json_list:
        try:
            date = item["date"]
            title = item["title"]
            
            c.execute(
                f"SELECT * FROM {config.TABLE_NEWS_DATA} WHERE date=? AND title=?",
                (date, title),
            )
            results = c.fetchall()

            if results:
                for result in results:
                    if result[0] != search_topic:
                        logging.info("Updating search topic for %s", title)
                        c.execute(
                            f"UPDATE {config.TABLE_NEWS_DATA} SET search_topic=? WHERE date=? AND title=?",
                            (search_topic, date, title)
                        )
                        conn.commit()
                    else:
                        logging.warning(
                            "%s %s already in the database with the same search topic, skipping...", date, title
                        )
            else:
                logging.info("Generating Sentiment Analysis for %s", title)
                sentiment, sentiment_score  = analyze_sentiment(
                    item.get("text", "")
                )
                logging.info("Sentiment generated for %s", title)
                
                c.execute(
                    f"INSERT INTO {config.TABLE_NEWS_DATA} (search_topic, title, top_image, videos, url, date, short_description, text, source, sentiment, sentiment_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        search_topic,
                        title,
                        item.get("top_image", ""),
                        item.get("videos", ""),
                        item.get("url", ""),
                        date,
                        item.get("short_description", ""),
                        item.get("text", ""),
                        item.get("source", ""),
                        str(sentiment),
                        sentiment_score,
                    ),
                )
                conn.commit()
                logging.info(
                    "UPLOADED: %s uploaded to the database", title
                )
        except KeyError as e:
            logging.error("Skipping item due to missing key: %s", e)
        except Exception as e:
            logging.error("Skipping item due to error: %s", e)

    conn.close()

def upload_fred_to_db(df):
    """Check if the primary key exists in the database and upload data if not."""
    logging.info("Starting upload to database.")
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    for _, row in df.iterrows():
        try:
            date_value = row.get("Date", "")

            # Check if the primary key (date, ticker) exists in the database
            c.execute(
                f"SELECT * FROM {config.TABLE_FRED_DATA} WHERE date=?",
                (date_value),
            )
            result = c.fetchone()

            if result:
                logging.warning(
                    "%s %s already in the database, skipping...", date_value
                )
            else:
                # Insert new row into the database
                c.execute(
                    f"INSERT OR REPLACE INTO {config.TABLE_FRED_DATA} (date, exchange_rates, treasury_yields, fed_funds_rate, consumer_price_index, GDP, industrial_production, unemployment_rate, consumer_sentiment, producer_price_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        date_value,
                        row.get("exchange_rates", ""),
                        row.get("treasury_yields", ""),
                        row.get("fed_funds_rate", ""),
                        row.get("consumer_price_index", ""),
                        row.get("GDP", ""),
                        row.get("industrial_production", ""),
                        row.get("unemployment_rate", ""),
                        row.get("consumer_sentiment", ""),
                        row.get("producer_price_index", ""),
                    ),
                )
                conn.commit()
                logging.info(
                    "UPLOADED: %s %s uploaded to the database", date_value
                )
        except Exception as e:
            logging.error("Skipping row due to error: %s", e)

    conn.close()