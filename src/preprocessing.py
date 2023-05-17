from typing import List, Tuple, Optional
from pathlib import Path

import pandas as pd
import numpy as np
import fire

from src.paths import DATA_DIR

def transform_ts_data_into_features_and_target(
    # ts_data: pd.DataFrame,
    path_to_input: Optional[Path] = DATA_DIR / 'ohlc_data.parquet',
    input_seq_len: Optional[int] = 24,
    step_size: Optional[int] = 1
) -> pd.DataFrame:
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

if __name__ == '__main__':
    
    fire.Fire(transform_ts_data_into_features_and_target)