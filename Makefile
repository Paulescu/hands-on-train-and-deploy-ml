.PHONY: init data train deploy

init:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install

data:
	poetry run python src/data.py

train:
	poetry run python src/train.py

deploy:
	poetry run python src/deploy.py --local-pickle model.pkl