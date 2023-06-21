from typing import Dict, Union, Optional, Callable
import os

import pandas as pd
from comet_ml import Experiment
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import Lasso
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import pickle

from src.preprocessing import (
    transform_ts_data_into_features_and_target,
    get_preprocessing_pipeline
)
from src.hyperparams import find_best_hyperparams
from src.logger import get_console_logger
from src.paths import MODELS_DIR
# from src.model_factory import get_preprocessing_and_model_pipeline

logger = get_console_logger()


def get_baseline_model_error(X_test: pd.DataFrame, y_test: pd.Series) -> float:
    """Returns the baseline model error."""
    predictions = X_test['price_1_hour_ago']
    return mean_absolute_error(y_test, predictions)

def get_model_fn_from_name(model_name: str) -> Callable:
    """Returns the model function given the model name."""
    if model_name == 'lasso':
        return Lasso
    elif model_name == 'xgboost':
        return XGBRegressor
    elif model_name == 'lightgbm':
        return LGBMRegressor
    else:
        raise ValueError(f'Unknown model name: {model_name}')

def train(
    X: pd.DataFrame,
    y: pd.Series,
    model: str,
    tune_hyperparams: Optional[bool] = False,
    hyperparam_trials: Optional[int] = 10,
    ) -> None:
    """
    Train a boosting tree model using the input features `X` and targets `y`,
    possibly running hyperparameter tuning.
    """
    model_fn = get_model_fn_from_name(model)

    experiment = Experiment(
        api_key = os.environ["COMET_ML_API_KEY"],
        workspace=os.environ["COMET_ML_WORKSPACE"],
        project_name = "hands-on-train-and-deploy-tutorial",
    )
    experiment.add_tag(model)

    # split the data into train and test
    train_sample_size = int(0.9 * len(X))
    X_train, X_test = X[:train_sample_size], X[train_sample_size:]
    y_train, y_test = y[:train_sample_size], y[train_sample_size:]
    logger.info(f'Train sample size: {len(X_train)}')
    logger.info(f'Test sample size: {len(X_test)}')

    if not tune_hyperparams:
        # create the full pipeline with default hyperparameters
        logger.info('Using default hyperparameters')
        pipeline = make_pipeline(
            get_preprocessing_pipeline(),
            model_fn()
        )

    else:

        # find best hyperparameters using cross-validation
        logger.info('Finding best hyperparameters with cross-validation')
        best_preprocessing_hyperparams, best_model_hyperparams = \
            find_best_hyperparams(model_fn, hyperparam_trials, X_train, y_train,
                                  experiment)
        logger.info(f'Best preprocessing hyperparameters: {best_preprocessing_hyperparams}')
        logger.info(f'Best model hyperparameters: {best_model_hyperparams}')
        
        pipeline = make_pipeline(
            get_preprocessing_pipeline(**best_preprocessing_hyperparams),
            model_fn(**best_model_hyperparams)
        )

        experiment.add_tag('hyper-parameter-tuning')

    # train the model
    logger.info('Fitting model with default hyperparameters')
    pipeline.fit(X_train, y_train)

    # compute test MAE
    predictions = pipeline.predict(X_test)
    test_error = mean_absolute_error(y_test, predictions)
    logger.info(f'Test MAE: {test_error}')
    experiment.log_metrics({'Test_MAE': test_error})

    # save the model to disk
    logger.info('Saving model to disk')
    with open(MODELS_DIR / 'model.pkl', "wb") as f:
        pickle.dump(pipeline, f)

    # log model artifact
    # experiment.log_model('eth-eur-1h-price-predictor', str(MODELS_DIR / 'model.pkl'))
    experiment.log_model(str(model_fn), str(MODELS_DIR / 'model.pkl'))
    
    # breakpoint()

    # log model to the registry
    # experiment.register_model('eth-eur-1h-price-predictor')
    


if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--model', type=str, default='lasso')
    parser.add_argument('--tune-hyperparams', action='store_true')
    parser.add_argument('--sample-size', type=int, default=None)
    parser.add_argument('--hyperparam-trials', type=int, default=10)
    args = parser.parse_args()

    logger.info('Generating features and targets')
    features, target = transform_ts_data_into_features_and_target()

    if args.sample_size is not None:
        # reduce input size to speed up training
        features = features.head(args.sample_size)
        target = target.head(args.sample_size)
        
    logger.info('Training model')
    train(features, target,
          model=args.model,
          tune_hyperparams=args.tune_hyperparams,
          hyperparam_trials=args.hyperparam_trials
          )