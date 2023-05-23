from typing import Optional

import fire
import pandas as pd
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
import pickle

from src.preprocessing import (
    transform_ts_data_into_features_and_target,
    get_preprocessing_pipeline
)
from src.logger import get_console_logger
from src.paths import MODELS_DIR

logger = get_console_logger(name='model_training')

def get_baseline_model_error(X_test: pd.DataFrame, y_test: pd.Series) -> float:
    """Returns the baseline model error."""
    predictions = X_test['price_1_hour_ago']
    return mean_absolute_error(y_test, predictions)


def get_full_pipeline(
    bb_window: int = 20,
    bb_window_dev: int = 2,
    rsi_window: int = 14,

    # TODO
    xgboost_params: dict = {}
) -> Pipeline:
    """Returns the full pipeline."""
    return make_pipeline(
        # get_preprocessing_pipeline(
        #     bb_window=bb_window,
        #     bb_window_dev=bb_window_dev,
        #     rsi_window=rsi_window
        # ),
        XGBRegressor()
    )

def train(
    X: pd.DataFrame,
    y: pd.Series,
    tune_hyperparams: Optional[bool] = False) -> None:
    """
    Train a boosting tree model using the input features `X` and targets `y`,
    possibly running hyperparameter tuning.
    """
    
    # split the data into train and test
    train_sample_size = int(0.9 * len(X))
    X_train, X_test = X[:train_sample_size], X[train_sample_size:]
    y_train, y_test = y[:train_sample_size], y[train_sample_size:]
    logger.info(f'Train sample size: {len(X_train)}')
    logger.info(f'Test sample size: {len(X_test)}')

    X_train = X_train[['price_1_hour_ago']]
    X_test = X_test[['price_1_hour_ago']]

    # baseline model performance
    logger.info(f'Baseline model error: {get_baseline_model_error(X_test, y_test)}')

    # pp = get_preprocessing_pipeline()
    # X_train_ = pp.fit_transform(X_train, y_train)
    # breakpoint()

    # create the full pipeline
    pipeline = get_full_pipeline()

    if not tune_hyperparams:
        # fit the pipeline
        pipeline.fit(X_train, y_train)

        # compute test error and log it
        predictions = pipeline.predict(X_test)
        test_error = mean_absolute_error(y_test, predictions)
        logger.info(f'Test error: {test_error}')

    else:
        # run hyperparameter tuning
        # TODO
        pass

    # check if the model is good enough, if so push it to the registry
    # TODO

    # save the model to disk
    with open(MODELS_DIR / 'model.pkl', "wb") as f:
        pickle.dump(pipeline, f)
    
    
if __name__ == '__main__':

    logger.info('Generating features and targets')
    features, target = transform_ts_data_into_features_and_target()

    logger.info('Training model')
    train(features, target)