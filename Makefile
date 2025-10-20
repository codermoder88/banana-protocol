install-all:
	poetry install --with test

lock:
	poetry lock

format:
	poetry run black --config pyproject.toml app tests
	poetry run isort --sp pyproject.toml app tests

lint:
	poetry run flake8 --toml-config pyproject.toml app tests
	poetry run mypy --config-file pyproject.toml app tests
	poetry run black --config pyproject.toml --check app tests
	poetry run isort --sp pyproject.toml --check-only app tests
	poetry run bandit -c pyproject.toml -r app tests
