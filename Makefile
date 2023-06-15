.PHONY: init data train deploy prepare-deployment requirements test-endpoint

DEPLOYMENT_DIR = deployment_dir

init:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install
	poetry run pip install comet-ml==3.33.4 # hack to fix comet-ml vs cerebrium conflict 
	
data:
	poetry run python src/data.py

train:
	poetry run python src/train.py

requirements:
	poetry run pip freeze > requirements.txt

prepare-deployment:
	rm -rf $(DEPLOYMENT_DIR) && mkdir $(DEPLOYMENT_DIR)
	# poetry export -f requirements.txt --output $(DEPLOYMENT_DIR)/requirements.txt --without-hashes
	poetry run pip freeze > $(DEPLOYMENT_DIR)/requirements.txt
	cp -r src/predict.py $(DEPLOYMENT_DIR)/main.py
	cp -r src $(DEPLOYMENT_DIR)/src/
	pip install cerebrium --upgrade # otherwise cerebrium deploy fails
	
deploy: prepare-deployment
	cd $(DEPLOYMENT_DIR) && poetry run cerebrium deploy eth-price-1-hour-predictor $(CEREBRIUM_API_KEY) --hardware CPU

test-endpoint:
	poetry run python src/test_endpoint.py