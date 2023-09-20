import pandas as pd
from pathlib import Path
import pytest
from unittest.mock import patch, Mock
from src.paths import DATA_DIR
from src.paths import SRC_DIR


# Import the function to be tested

from src.data import download_ohlc_data_from_coinbase 

# Define a fixture for mocking requests
@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            [1642651200, 38645.52, 38719.99, 38673.24, 38702.27, 1234.56],
            # Add more data points as needed
        ]
        yield mock_get

# Define a fixture for mocking the DATA_DIR
@pytest.fixture
def mock_data_dir(DATA_DIR= DATA_DIR):
        return DATA_DIR

# Test the download_ohlc_data_from_coinbase function
def test_download_ohlc_data_from_coinbase(mock_requests_get, mock_data_dir):
    product_id = "BTC-USD"
    from_day = "2022-01-01"
    to_day = "2022-01-02"

    # Call the function
    result = download_ohlc_data_from_coinbase(product_id, from_day, to_day)

    # Assert that the function returns a Path object
    assert isinstance(result, Path)

    # Assert that the expected file is created in the mock data directory
    expected_file = mock_data_dir / 'downloads' / '2022-01-01.parquet'
    assert expected_file.exists()

    # You can add more assertions as needed to validate the behavior of the function
    # For example, you can assert that the downloaded data is correctly processed and saved to the Parquet file.

if __name__ == '__main__':
    pytest.main(['-v', __file__])
