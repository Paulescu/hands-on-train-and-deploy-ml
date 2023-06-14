from typing import List, Tuple, Optional, Union
from pathlib import Path

import pandas as pd
import numpy as np
import fire
import ta
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline, Pipeline

from src.paths import DATA_DIR
from src.logger import get_console_logger
# from src import config

logger = get_console_logger()

def transform_ts_data_into_features_and_target(
    # ts_data: pd.DataFrame,
    path_to_input: Optional[Path] = DATA_DIR / 'ohlc_data.parquet',
    input_seq_len: Optional[int] = 24,
    step_size: Optional[int] = 1
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Slices and transposes data from time-series format into a (features, target)
    format that we can use to train Supervised ML models
    """
    # load parquet file
    ts_data = pd.read_parquet(path_to_input)
    ts_data = ts_data[['time', 'close']]
    ts_data.sort_values(by=['time'], inplace=True)

    # output features and targets
    features = pd.DataFrame()
    targets = pd.DataFrame()
    
    # pre-compute cutoff indices to split dataframe rows
    indices = get_cutoff_indices_features_and_target(
        ts_data,
        input_seq_len,
        step_size
    )

    # slice and transpose data into numpy arrays for features and targets
    n_examples = len(indices)
    x = np.ndarray(shape=(n_examples, input_seq_len), dtype=np.float32)
    y = np.ndarray(shape=(n_examples), dtype=np.float32)
    times = []
    for i, idx in enumerate(indices):
        x[i, :] = ts_data.iloc[idx[0]:idx[1]]['close'].values
        y[i] = ts_data.iloc[idx[1]:idx[2]]['close'].values
        times.append(ts_data.iloc[idx[1]]['time'])

    # numpy -> pandas
    features = pd.DataFrame(
        x,
        columns=[f'price_{i+1}_hour_ago' for i in reversed(range(input_seq_len))]
    )

    # add back column with the time
    # features['time'] = times

    # numpy -> pandas
    targets = pd.DataFrame(y, columns=[f'target_price_next_hour'])

    return features, targets['target_price_next_hour']

def get_cutoff_indices_features_and_target(
    data: pd.DataFrame,
    input_seq_len: int,
    step_size: int
    ) -> List[Tuple[int, int, int]]:

    stop_position = len(data) - 1
        
    # Start the first sub-sequence at index position 0
    subseq_first_idx = 0
    subseq_mid_idx = input_seq_len
    subseq_last_idx = input_seq_len + 1
    indices = []
    
    while subseq_last_idx <= stop_position:
        indices.append((subseq_first_idx, subseq_mid_idx, subseq_last_idx))
        subseq_first_idx += step_size
        subseq_mid_idx += step_size
        subseq_last_idx += step_size

    return indices

def get_price_columns(X: pd.DataFrame) -> List[str]:
    """Get the columns of the input DataFrame that contain the price data."""
    return [col for col in X.columns if 'price' in col]
class BollingerBands(BaseEstimator, TransformerMixin):
    """
    Adds Bollinger Bands to the input DataFrame from the `close` prices

    New columns are:
        - 'bb_upper'
        - 'bb_lower'
    """
    def __init__(self, window: int = 20, window_dev: int = 2):
        self.window = window
        self.window_dev = window_dev
    
    def fit(self,
            X: pd.DataFrame,
            y: Optional[Union[pd.DataFrame, pd.Series]] = None) -> "BollingerBands":
        """In this scenario, the fit method isn't doing anything. But it must be implemented. This is a scenario of an estimator without parameters."""
        return self

    def _add_indicator(self, row: pd.Series) -> float:

        # Calculate the moving average
        sma = talib.SMA(row, timeperiod=self.window)

        # Calculate the standard deviation
        std = talib.STDDEV(row, timeperiod=self.window)

        # Calculate the upper and lower Bollinger Bands
        upper_band = sma + self.window_dev * std
        lower_band = sma - self.window_dev * std
        
        return pd.Series([upper_band[-1], lower_band[-1]])

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Compute the Bollinger Bands and add them to the input DataFrame."""
        logger.info('Adding Bollinger Bands to the input DataFrame')
        df = X[get_price_columns(X)].apply(self._add_indicator, axis=1)
        df.columns = ['bb_upper', 'bb_lower']
        X = pd.concat([X, df], axis=1)
        return X

    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Inverse the log of every cell of the DataFrame."""
        X.drop(columns=['bb_upper', 'bb_lower'], inplace=True)
        return X


class RSI(BaseEstimator, TransformerMixin):
    """
    Adds RSI to the input DataFrame from the `close` prices

    New columns are:
        - 'rsi'
    """
    def __init__(self, window: int = 14):
        self.window = window
    
    def fit(self,
            X: pd.DataFrame,
            y: Optional[Union[pd.DataFrame, pd.Series]] = None) -> "RSI":
        """In this scenario, the fit method isn't doing anything. But it must be implemented. This is a scenario of an estimator without parameters."""
        return self

    def _add_indicator(self, row: pd.Series) -> float:
    
        # OLD code using talib
        # import talib
        # return pd.Series([talib.RSI(row, timeperiod=self.window)[-1]])
        return pd.Series([ta.momentum.rsi(row, window=self.window)[-1]])

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Compute the RSI and add it to the input DataFrame."""
        logger.info('Adding RSI to the input DataFrame')
        df = X[get_price_columns(X)].apply(self._add_indicator, axis=1)
        df.columns = ['rsi']
        X = pd.concat([X, df], axis=1)
        return X

    def inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Inverse the log of every cell of the DataFrame."""
        X.drop(columns=['rsi'], inplace=True)
        return X

def get_preprocessing_pipeline(
    bb_window: int = 20,
    bb_window_dev: int = 2,
    rsi_window: int = 14
) -> Pipeline:
    """Returns the preprocessing pipeline."""
    return make_pipeline(
        # BollingerBands(bb_window, bb_window_dev),
        RSI(rsi_window)
    )

if __name__ == '__main__':
    
    features, target = fire.Fire(transform_ts_data_into_features_and_target)
    
    preprocessing_pipeline = get_preprocessing_pipeline()

    preprocessing_pipeline.fit(features)
    X = preprocessing_pipeline.transform(features)
    print(X.head())