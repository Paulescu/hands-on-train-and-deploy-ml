.PHONY: init data baseline train deploy prepare-deployment test-endpoint

DEPLOYMENT_DIR = deployment_dir

up_run = /Users/user/.local/bin/
init:
	curl -sSL https://install.python-poetry.org | python3 -
	up_run poetry install
	
data:
	poetry run python src/data.py

baseline:
	python3 -m  poetry run python src/baseline_model.py

train:
	python3 -m poetry run python src/train.py

prepare-deployment:
	rm -rf $(DEPLOYMENT_DIR) && mkdir $(DEPLOYMENT_DIR)
	# /Users/user/.local/bin/poetry update cerebrium
	/Users/user/.local/bin/poetry export -f requirements.txt --output $(DEPLOYMENT_DIR)/requirements.txt --without-hashes
	cp -r src/predict.py $(DEPLOYMENT_DIR)/main.py
	cp -r src $(DEPLOYMENT_DIR)/src/
	python -m pip install cerebrium --upgrade # otherwise cerebrium deploy might fail
	# /Users/user/.local/bin/poetry update cerebrium@latest
	
deploy:
	cd $(DEPLOYMENT_DIR) && /Users/user/.local/bin/poetry run cerebrium deploy --api-key $(CEREBRIUM_API_KEY) --hardware CPU eth-price-1-hour-predictor --memory 3

test-endpoint:
	python3 -m poetry run python src/test_endpoint.py