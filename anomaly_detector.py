import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.stats.stattools import medcouple
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


def detect_anomalies(data, alpha=0.05, max_anomalies=None):
    """
    Detect anomalies in pandas time series data using the Seasonal Hybrid ESD algorithm.

    Parameters:
        data (pandas.Series): The time series data.
        alpha (float): The significance level for anomaly detection. Default is 0.05.
        max_anomalies (int): The maximum number of anomalies to detect. Default is None (detect all anomalies).

    Returns:
        pandas.DataFrame: A DataFrame containing the detected anomalies with the following columns:
            - index: The index of the anomaly.
            - value: The value of the anomaly.
            - expected: The expected value at the anomaly index.
            - deviation: The deviation of the anomaly from the expected value.
    """

    data.dropna(inplace=True)

    # Perform seasonal decomposition
    decomposition = seasonal_decompose(data, model="additive")

    # Calculate residuals
    residuals = data - decomposition.seasonal - decomposition.trend
    residuals.dropna(inplace=True)
    logging.info(f"Residuals: {residuals}")

    # Calculate median absolute deviation (MAD)
    mad = np.median(np.abs(residuals - np.median(residuals)))

    # Calculate modified z-scores
    modified_z_scores = 0.6745 * (residuals - np.median(residuals)) / mad

    # Calculate the median of the modified z-scores
    median_z_score = np.median(modified_z_scores)

    # Calculate the median absolute deviation of the modified z-scores
    mad_z_score = medcouple(modified_z_scores) * mad

    # Detect anomalies
    anomalies = []
    for i, z_score in enumerate(modified_z_scores):
        if z_score > median_z_score + alpha * mad_z_score:
            anomalies.append(
                {
                    "index": data.index[i],
                    "value": data[i],
                    "expected": decomposition.seasonal[i] + decomposition.trend[i],
                    "deviation": z_score * mad,
                }
            )

    # Sort anomalies by deviation in descending order
    anomalies.sort(key=lambda x: x["deviation"], reverse=True)

    # Limit the number of anomalies if max_anomalies is specified
    if max_anomalies is not None:
        anomalies = anomalies[:max_anomalies]

    return pd.DataFrame(anomalies)
