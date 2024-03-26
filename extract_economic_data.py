from fredapi import Fred
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import config
from datetime import datetime

load_dotenv(".env")

# Get the API key from the environment variable
FRED_API_KEY = os.environ.get("FRED_API_KEY")

f = Fred(api_key = FRED_API_KEY)

def get_frequency(economic_metrics_id):
    if economic_metrics_id == "DTWEXBGS" or economic_metrics_id == "T10Y2Y" or economic_metrics_id == "DFF":
        return "d"
    elif economic_metrics_id == "GDP":
      return "q"
    else:
        return "m"

def extract_economic_data(start_date, metric_id, frequency):

    df = f.get_series(metric_id, observation_start = start_date, frequency=frequency)

    df = pd.DataFrame({'date': df.index, metric_id: df.values})

    return df

def extract_all_economic_data():
    economic_metrics_ids = config.ECONOMIC_METRICS_IDS
    observation_start = config.OBSERVATION_START

    # Extract data for the first economic metric ID and create df_all
    df_all = extract_economic_data(observation_start, economic_metrics_ids[0], get_frequency(economic_metrics_ids[0]))

    df_all.rename(columns={df_all.columns[1]: economic_metrics_ids[0]}, inplace=True)

    # Loop through the rest of the economic metric IDs starting from the second one
    for economic_metrics_id in economic_metrics_ids[1:]:

        df = extract_economic_data(observation_start, economic_metrics_id, get_frequency(economic_metrics_id))

        df.rename(columns={df.columns[1]: economic_metrics_id}, inplace=True)

        df_all = pd.merge(df_all, df, on='date', how='outer')

    df_all['date'] = df_all['date'].apply(lambda x: datetime.strptime(x.strftime('%Y-%m-%d'), "%Y-%m-%d").date())

    return df_all
