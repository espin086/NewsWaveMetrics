import logging
import sqlite3
import config

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
                    (title TEXT,
                    top_image TEXT,
                    Videos TEXT,
                    url TEXT,
                    date TEXT,
                    short_description TEXT,
                    text TEXT,
                    source TEXT,
                    sentiment TEXT
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