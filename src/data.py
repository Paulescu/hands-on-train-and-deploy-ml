from typing import Optional
from pathlib import Path

import pandas as pd
import requests
import fire

from src.paths import DATA_DIR
from src.logger import get_console_logger

logger = get_console_logger(name='dataset_generation')

def download_ohlc_data_from_coinbase(
    product_id: Optional[str] = "BTC-USD",
    from_day: Optional[str] = "2022-01-01",
    to_day: Optional[str] = "2023-06-01",
) -> Path:
    """
    Downloads historical candles from Coinbase API and saves data to disk
    Reference: https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getproductcandles
    """
    # create list of days as strings
    days = pd.date_range(start=from_day, end=to_day, freq="1D")
    days = [day.strftime("%Y-%m-%d") for day in days]

    # create empty dataframe
    data = pd.DataFrame()

    # create download dir folder if it doesn't exist
    if not (DATA_DIR / 'downloads').exists():
        logger.info('Create directory for downloads')
        (DATA_DIR / 'downloads').mkdir(parents=True)
    
    for day in days:

        # download file if it doesn't exist
        file_name = DATA_DIR / 'downloads' / f'{day}.parquet'
        if file_name.exists():
            logger.info(f'File {file_name} already exists, skipping')
            data_one_day = pd.read_parquet(file_name)
        else:
            logger.info(f'Downloading data for {day}')
            data_one_day = download_data_for_one_day(product_id, day)
            data_one_day.to_parquet(file_name, index=False)
    
        # combine today's file with the rest of the data
        data = pd.concat([data, data_one_day])

    # save data to disk   
    # data.to_parquet(DATA_DIR / f"ohlc_from_{from_day}_to_{to_day}.parquet", index=False)
    data.to_parquet(DATA_DIR / f"ohlc_data.parquet", index=False)

    return DATA_DIR / f"ohlc_data.parquet"

def download_data_for_one_day(product_id: str, day: str) -> pd.DataFrame:
    """
    Downloads one day of data and returns pandas Dataframe
    """
    # create start end end date strings
    start = f'{day}T00:00:00'
    from datetime import datetime, timedelta
    end = (datetime.strptime(day, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    end = f'{end}T00:00:00'

    # call API
    URL = f'https://api.exchange.coinbase.com/products/{product_id}/candles?start={start}&end={end}&granularity=3600'
    r = requests.get(URL)
    data = r.json()

    # transform list of lists to pandas dataframe and return
    return pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])

if __name__== '__main__':
    fire.Fire(download_ohlc_data_from_coinbase)

