from typing import Dict, Union, Optional
import os

import pandas as pd
from comet_ml import Experiment
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression
# from xgboost import XGBRegressor
# from lightgbm import LGBMRegressor

import pickle

from src.preprocessing import (
    transform_ts_data_into_features_and_target,
    get_preprocessing_pipeline
)
from src.logger import get_console_logger
from src.paths import MODELS_DIR

logger = get_console_logger()


def get_baseline_model_error(X_test: pd.DataFrame, y_test: pd.Series) -> float:
    """Returns the baseline model error."""
    predictions = X_test['price_1_hour_ago']
    return mean_absolute_error(y_test, predictions)


# def get_full_pipeline(
#     bb_window: int = 20,
#     bb_window_dev: int = 2,
#     rsi_window: int = 14,
# ) -> Pipeline:
#     """Returns the full pipeline."""
#     # raise Exception("This function is deprecated. Use get_preprocessing_and_model_pipeline instead.")
#     return make_pipeline(
#         get_preprocessing_pipeline(
#             bb_window=bb_window,
#             bb_window_dev=bb_window_dev,
#             rsi_window=rsi_window
#         ),
#         # XGBRegressor()
#         LinearRegression()
#     )


def get_preprocessing_and_model_pipeline(
    preprocessing_hyperparams: Dict[str, Union[int, float, str]],
    model_hyperparams: Dict[str, Union[int, float, str]],
) -> Pipeline:
    """Returns the preprocessing and model pipeline."""
    return make_pipeline(
        get_preprocessing_pipeline(**preprocessing_hyperparams),
        LinearRegression(**model_hyperparams)
    )

def train(
    X: pd.DataFrame,
    y: pd.Series,
    tune_hyperparams: Optional[bool] = False) -> None:
    """
    Train a boosting tree model using the input features `X` and targets `y`,
    possibly running hyperparameter tuning.
    """
    experiment = Experiment(
        api_key = os.environ["COMET_ML_API_KEY"],
        project_name = "hands-on-train-and-deploy-ml-model",
        workspace="paulescu"
    )

    # split the data into train and test
    train_sample_size = int(0.9 * len(X))
    X_train, X_test = X[:train_sample_size], X[train_sample_size:]
    y_train, y_test = y[:train_sample_size], y[train_sample_size:]
    logger.info(f'Train sample size: {len(X_train)}')
    logger.info(f'Test sample size: {len(X_test)}')

    # X_train = X_train[['price_1_hour_ago']]
    # X_test = X_test[['price_1_hour_ago']]
    # breakpoint()

    # baseline model performance
    baseline_mae = get_baseline_model_error(X_test, y_test)
    logger.info(f'Baseline model error: {baseline_mae}')
    experiment.log_metrics({'baseline_MAE': baseline_mae})

    # create the full pipeline with default hyperparameters
    pipeline = get_preprocessing_and_model_pipeline(
        preprocessing_hyperparams={},
        model_hyperparams={}
    )

    if not tune_hyperparams:
        # fit the pipeline
        logger.info('Fitting model with default hyperparameters')
        pipeline.fit(X_train, y_train)
    else:
        # run hyperparameter tuning
        # TODO
        raise NotImplementedError('Hyperparameter tuning is not implemented yet')

    # breakpoint()

    # compute test error and log it
    predictions = pipeline.predict(X_test)
    test_error = mean_absolute_error(y_test, predictions)
    logger.info(f'Test error: {test_error}')
    experiment.log_metrics({'test_MAE': test_error})

    # save the model to disk
    logger.info('Saving model to disk')
    with open(MODELS_DIR / 'model.pkl', "wb") as f:
        pickle.dump(pipeline, f)
        # from time import sleep
        # sleep(5)

    # log model artifact
    experiment.log_model('linear_model', str(MODELS_DIR / 'model.pkl'))

    # log model to the registry
    experiment.register_model('linear_model')

    # breakpoint()


    
if __name__ == '__main__':

    logger.info('Generating features and targets')
    features, target = transform_ts_data_into_features_and_target()

    logger.info('Training model')
    train(features, target)