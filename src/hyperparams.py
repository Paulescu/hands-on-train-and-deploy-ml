from typing import Dict, Tuple, Callable, Union
import os

from comet_ml import Experiment
import optuna
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Lasso
from lightgbm import LGBMRegressor

# from src.model_factory import get_preprocessing_and_model_pipeline
from src.preprocessing import get_preprocessing_pipeline
from src.logger import get_console_logger

logger = get_console_logger()

def sample_hyperparams(
    model_fn: Callable,
    trial: optuna.trial.Trial,
) -> Dict[str, Union[str, int, float]]:

    if model_fn == Lasso:
        return {
            'alpha': trial.suggest_float('alpha', 0.01, 1.0, log=True)
        }
    elif model_fn == LGBMRegressor:
        return {
            "metric": 'mae',
            "verbose": -1,
            "num_leaves": trial.suggest_int("num_leaves", 2, 256),
            "feature_fraction": trial.suggest_float("feature_fraction", 0.2, 1.0),
            "bagging_fraction": trial.suggest_float("bagging_fraction", 0.2, 1.0),
            "min_child_samples": trial.suggest_int("min_child_samples", 3, 100),   
        }
    else:
        raise NotImplementedError('TODO: implement other models')

def find_best_hyperparams(
    model_fn: Callable,
    hyperparam_trials: int,
    X: pd.DataFrame,
    y: pd.Series,
    experiment: Experiment,
) -> Tuple[Dict, Dict]:
    """"""
    assert model_fn in {Lasso, LGBMRegressor}

    def objective(trial: optuna.trial.Trial) -> float:
        """
        Error function we want to minimize (or maximize) using hyperparameter tuning.
        """
        # sample hyper-parameters
        preprocessing_hyperparams = {
            'pp_rsi_window': trial.suggest_int('pp_rsi_window', 5, 20),
        }
        model_hyperparams = sample_hyperparams(model_fn, trial)
        
        # evaluate the model using TimeSeriesSplit cross-validation
        tss = TimeSeriesSplit(n_splits=3)
        scores = []
        logger.info(f'{trial.number=}')
        for split_number, (train_index, val_index) in enumerate(tss.split(X)):

            # split data for training and validation
            X_train, X_val = X.iloc[train_index], X.iloc[val_index]
            y_train, y_val = y.iloc[train_index], y.iloc[val_index]
            
            logger.info(f'{split_number=}')
            logger.info(f'{len(X_train)=}')
            logger.info(f'{len(X_val)=}')

            # train the model
            pipeline = make_pipeline(
                get_preprocessing_pipeline(**preprocessing_hyperparams),
                model_fn(**model_hyperparams)
            )
            pipeline.fit(X_train, y_train)
            
            # evaluate the model
            y_pred = pipeline.predict(X_val)
            mae = mean_absolute_error(y_val, y_pred)
            scores.append(mae)
            
            logger.info(f'{mae=}')

        score = np.array(scores).mean()

        # Return the mean score
        return score
    
    logger.info('Starting hyper-parameter search...')
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=hyperparam_trials)

    # Get the best hyperparameters and their values
    best_params = study.best_params
    best_value = study.best_value
    
    # split best_params into preprocessing and model hyper-parameters
    best_preprocessing_hyperparams = \
        {key: value for key, value in best_params.items() 
         if key.startswith('pp_')}
    
    best_model_hyperparams = {
        key: value for key, value in best_params.items() 
        if not key.startswith('pp_')}

    logger.info("Best Parameters:")
    for key, value in best_params.items():
        logger.info(f"{key}: {value}")
    logger.info(f"Best MAE: {best_value}")

    experiment.log_metric('Cross_validation_MAE', best_value)

    return best_preprocessing_hyperparams, best_model_hyperparams

