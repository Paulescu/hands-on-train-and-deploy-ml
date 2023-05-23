from typing import Optional
import os

import fire
from cerebrium import deploy, model_type

from src.logger import get_console_logger
from src.paths import MODELS_DIR

logger = get_console_logger(name='model_deployment')

try:
    CEREBRIUM_API_KEY = os.environ['CEREBRIUM_API_KEY']
except KeyError:
    logger.error('CEREBRIUM_API_KEY environment variable not set.')
    raise

def deploy(
    local_pickle: Optional[str] = None,
    from_model_registry: bool = False,
):
    """"""
    logger.info('Deploying model...')

    if from_model_registry:
        logger.info('Loading model from model registry...')
        raise NotImplementedError('TODO')

    elif local_pickle:
        logger.info('Deploying model from local pickle...')
        model_pickle_file = MODELS_DIR / local_pickle
        # TODO: not working. I am just following the docs here
        # https://docs.cerebrium.ai/quickstarts/scikit
        endpoint = deploy((model_type.SKLEARN, model_pickle_file), "sk-test-model" , CEREBRIUM_API_KEY)
    else:
        raise ValueError('Must specify either --local-pickle or --from-model-registry.')

    logger.info('Model deployed.')

if __name__ == '__main__':
    fire.Fire(deploy)