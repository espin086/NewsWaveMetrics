"""Build a comprehensive model training dataset for stock price prediction.

The dataset combines:
- Historical stock prices and trading volumes
- Technical market indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV, ROC)
- Federal Reserve economic indicators
- News sentiment scores

The resulting dataset is saved as CSV files (one per ticker) and optionally stored
in the SQLite database under the ``training_dataset`` table.

Usage::

    # Build dataset for all configured tickers
    python build_training_dataset.py

    # Build dataset for a single ticker
    python build_training_dataset.py --ticker AAPL

    # Skip saving to database
    python build_training_dataset.py --ticker AAPL --no-db

    # Skip saving to CSV
    python build_training_dataset.py --ticker AAPL --no-csv
"""

import argparse
import logging
import sqlite3

import numpy as np
import pandas as pd

import config

logging.basicConfig(
    level=config.LOGGING_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
)


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


def load_stock_data(ticker: str) -> pd.DataFrame:
    """Load historical OHLCV stock data for *ticker* from the database.

    Returns an empty DataFrame if the ticker has no data.
    """
    conn = sqlite3.connect(config.DATABASE)
    query = f"""
        SELECT date, open_price, high_price, low_price, closing_price, volume
        FROM {config.TABLE_STOCK_DATA}
        WHERE ticker = ?
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn, params=(ticker,))
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_economic_data() -> pd.DataFrame:
    """Load Federal Reserve economic indicators from the database."""
    conn = sqlite3.connect(config.DATABASE)
    query = f"""
        SELECT *
        FROM {config.TABLE_FRED_DATA}
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_news_sentiment(ticker: str) -> pd.DataFrame:
    """Load daily aggregated news sentiment for *ticker* from the database.

    Returns a DataFrame with columns ``date``, ``avg_sentiment_score``, and
    ``news_count``.  Dates with no news will be absent (handled by a left-join
    later).
    """
    search_topic = f"Stock News for {ticker}"
    conn = sqlite3.connect(config.DATABASE)
    query = f"""
        SELECT
            date,
            AVG(sentiment_score) AS avg_sentiment_score,
            COUNT(*)             AS news_count
        FROM {config.TABLE_NEWS_DATA}
        WHERE search_topic = ?
        GROUP BY date
        ORDER BY date ASC
    """
    df = pd.read_sql(query, conn, params=(search_topic,))
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    return df


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators to *df* (which must contain OHLCV columns).

    Indicators added:

    * **Simple Moving Averages (SMA)** – 5, 10, 20, 50 days
    * **Exponential Moving Averages (EMA)** – 5, 10, 20, 50 days
    * **RSI** – 14 days
    * **MACD** – (12, 26) with 9-day signal line and histogram
    * **Bollinger Bands** – 20-day, 2 standard deviations (upper, lower,
      width, %B)
    * **Average True Range (ATR)** – 14 days
    * **On-Balance Volume (OBV)**
    * **Rate of Change (ROC)** – 5 and 10 days
    * **Volume SMA** – 20 days
    * **Daily return** – percentage change in closing price
    """
    close = df["closing_price"]
    high = df["high_price"]
    low = df["low_price"]
    volume = df["volume"]

    # Simple Moving Averages
    for window in [5, 10, 20, 50]:
        df[f"sma_{window}"] = close.rolling(window=window).mean()

    # Exponential Moving Averages
    for window in [5, 10, 20, 50]:
        df[f"ema_{window}"] = close.ewm(span=window, adjust=False).mean()

    # RSI (14-day) using Wilder's smoothing (equivalent to EWM with alpha=1/14)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema_12 - ema_26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # Bollinger Bands (20-day, 2 std)
    sma_20 = close.rolling(window=20).mean()
    std_20 = close.rolling(window=20).std()
    df["bb_upper"] = sma_20 + 2 * std_20
    df["bb_lower"] = sma_20 - 2 * std_20
    df["bb_width"] = df["bb_upper"] - df["bb_lower"]
    bb_width_safe = df["bb_width"].replace(0, np.nan)
    df["bb_pct"] = (close - df["bb_lower"]) / bb_width_safe

    # Average True Range (ATR – 14 days)
    prev_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr_14"] = true_range.rolling(window=14).mean()

    # On-Balance Volume (OBV)
    # The first row has no price change, so it contributes 0 volume to OBV
    # (np.sign(NaN) = NaN; multiplying by volume gives NaN, then filled to 0).
    price_direction = np.sign(close.diff()).fillna(0)
    df["obv"] = (price_direction * volume).cumsum()

    # Rate of Change (ROC)
    for window in [5, 10]:
        df[f"roc_{window}"] = close.pct_change(periods=window) * 100

    # Volume Simple Moving Average
    df["volume_sma_20"] = volume.rolling(window=20).mean()

    # Daily return
    df["daily_return"] = close.pct_change() * 100

    return df


def add_target_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Add prediction target variables to *df*.

    * ``target_direction`` – 1 if next-day close > today's close, else 0
    * ``target_return``    – next-day percentage return (float)
    """
    next_close = df["closing_price"].shift(-1)
    # Int64 (nullable integer) is used so the last row's NaN is preserved
    # until clean_dataset() removes it; standard int cannot represent NaN.
    df["target_direction"] = (next_close > df["closing_price"]).astype("Int64")
    # closing_price is assumed non-zero for exchange-listed stocks.
    df["target_return"] = (next_close / df["closing_price"]) - 1
    return df


# ---------------------------------------------------------------------------
# Dataset assembly
# ---------------------------------------------------------------------------


def merge_datasets(
    stock_df: pd.DataFrame,
    econ_df: pd.DataFrame,
    sentiment_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge stock, economic, and sentiment data on *date*.

    * Economic data is left-joined and forward-filled to propagate
      monthly/quarterly observations across daily stock rows.
    * Sentiment data is left-joined; trading days with no news will have
      ``NaN`` values (filled during cleaning).
    """
    df = pd.merge(stock_df, econ_df, on="date", how="left")

    econ_cols = [c for c in econ_df.columns if c != "date"]
    df[econ_cols] = df[econ_cols].ffill()

    df = pd.merge(df, sentiment_df, on="date", how="left")
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean *df* for model training.

    Steps:

    1. Fill missing sentiment values with neutral defaults.
    2. Drop the last row (target unknown – no future price available).
    3. Drop rows that still lack sufficient technical indicator history
       (e.g. before 50-day SMA becomes available).
    4. Reset the index.
    """
    if "avg_sentiment_score" in df.columns:
        df["avg_sentiment_score"] = df["avg_sentiment_score"].fillna(0.0)
    if "news_count" in df.columns:
        df["news_count"] = df["news_count"].fillna(0)

    # Remove the final row where target is undefined
    df = df[df["target_direction"].notna()].copy()

    # Drop rows where core technical indicators are not yet computed
    required_indicator_cols = ["sma_50", "rsi_14", "macd", "bb_upper", "atr_14"]
    df = df.dropna(subset=required_indicator_cols)

    df = df.reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


def save_to_csv(df: pd.DataFrame, ticker: str) -> None:
    """Save *df* to a CSV file under ``config.TRAINING_DATA_PATH``."""
    config.TRAINING_DATA_PATH.mkdir(parents=True, exist_ok=True)
    output_path = config.TRAINING_DATA_PATH / f"training_dataset_{ticker}.csv"
    df.to_csv(output_path, index=False)
    logging.info("Saved training dataset for %s to %s", ticker, output_path)


def save_to_database(df: pd.DataFrame, ticker: str) -> None:
    """Append *df* (tagged with *ticker*) to the training dataset table.

    ``pandas.DataFrame.to_sql`` with ``method='multi'`` is used for reasonably
    efficient batch inserts.  For very large datasets (millions of rows) a
    dedicated ETL tool or bulk-copy approach would be faster.
    """
    conn = sqlite3.connect(config.DATABASE)
    df_with_ticker = df.copy()
    df_with_ticker.insert(0, "ticker", ticker)
    df_with_ticker["date"] = df_with_ticker["date"].astype(str)
    df_with_ticker.to_sql(
        config.TABLE_TRAINING_DATA, conn, if_exists="append", index=False, method="multi"
    )
    conn.close()
    logging.info(
        "Saved %d rows for ticker %s to database table '%s'.",
        len(df_with_ticker),
        ticker,
        config.TABLE_TRAINING_DATA,
    )


def _recreate_training_table() -> None:
    """Drop and recreate the training dataset table (used before a full rebuild)."""
    conn = sqlite3.connect(config.DATABASE)
    conn.execute(f"DROP TABLE IF EXISTS {config.TABLE_TRAINING_DATA}")
    conn.commit()
    conn.close()
    logging.info("Recreated training dataset table '%s'.", config.TABLE_TRAINING_DATA)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_training_dataset(
    ticker: str,
    save_csv: bool = True,
    save_db: bool = True,
) -> pd.DataFrame:
    """Build a model-ready training dataset for *ticker*.

    Parameters
    ----------
    ticker:
        Stock ticker symbol (e.g. ``"AAPL"``).
    save_csv:
        When *True*, write the dataset to a CSV file.
    save_db:
        When *True*, append the dataset to the SQLite training table.

    Returns
    -------
    pandas.DataFrame
        The cleaned, feature-enriched training dataset, or an empty
        DataFrame if no data was available.
    """
    logging.info("Building training dataset for ticker: %s", ticker)

    stock_df = load_stock_data(ticker)
    if stock_df.empty:
        logging.warning("No stock data found for ticker: %s. Skipping.", ticker)
        return pd.DataFrame()

    econ_df = load_economic_data()
    sentiment_df = load_news_sentiment(ticker)

    stock_df = add_technical_indicators(stock_df)
    stock_df = add_target_variables(stock_df)

    df = merge_datasets(stock_df, econ_df, sentiment_df)
    df = clean_dataset(df)

    if df.empty:
        logging.warning(
            "Dataset is empty after cleaning for ticker: %s. Skipping.", ticker
        )
        return pd.DataFrame()

    logging.info(
        "Training dataset for %s: %d rows, %d features.", ticker, len(df), len(df.columns)
    )

    if save_csv:
        save_to_csv(df, ticker)
    if save_db:
        save_to_database(df, ticker)

    return df


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def setup_argparse() -> argparse.Namespace:
    """Configure and return parsed CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Build a model training dataset for stock price prediction.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default=None,
        help=(
            "Stock ticker symbol (e.g. AAPL). "
            "Omit to build datasets for all configured tickers."
        ),
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Do not save the dataset to CSV files.",
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Do not save the dataset to the SQLite database.",
    )
    return parser.parse_args()


def main() -> None:
    """Build training datasets for one or all configured tickers."""
    args = setup_argparse()

    tickers = [args.ticker] if args.ticker else config.TICKERS
    save_csv = not args.no_csv
    save_db = not args.no_db

    if save_db:
        _recreate_training_table()

    for ticker in tickers:
        build_training_dataset(ticker, save_csv=save_csv, save_db=save_db)

    logging.info("Training dataset build complete.")


if __name__ == "__main__":
    main()
