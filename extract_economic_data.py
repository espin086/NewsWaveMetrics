from fredapi import Fred
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv(".env")

# Get the API key from the environment variable
FRED_API_KEY = os.environ.get("FRED_API_KEY")

f = Fred(api_key = FRED_API_KEY)

def extract_economic_data(start_date, metric_id, frequency):

    df = f.get_series(metric_id, observation_start = start_date, frequency=frequency)

    df = pd.DataFrame({'date': df.index, metric_id: df.values})

    return df

    









