import pickle

from comet_ml import API
from sklearn.pipeline import Pipeline

from src.logger import get_console_logger

logger = get_console_logger()

def load_production_model_from_registry(
    workspace: str,
    api_key: str,
    model_name: str,
    status: str = 'Production',
) -> Pipeline:
    """Loads the production model from the remote model registry"""

    # find model version to deploy
    api = API(api_key)
    model_details = api.get_registry_model_details(workspace, model_name)['versions']
    model_versions = [md['version'] for md in model_details if md['status'] == status]
    if len(model_versions) == 0:
        logger.error('No production model found')
        raise ValueError('No production model found')
    else:
        logger.info(f'Found {status} model versions: {model_versions}')
        model_version = model_versions[0]
    
    # download model from comet ml registry to local file
    api.download_registry_model(
        workspace,
        registry_name=model_name,
        version=model_version,
        output_path='./',
        expand=True
    )
    
    # load model from local file to memory
    with open('./model.pkl', "rb") as f:
        model = pickle.load(f)
    
    return model