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

test:
	poetry run pytest

docker-up:
	docker-compose -f docker-compose.yml up --build

docker-down:
	docker-compose -f docker-compose.yml down

docker-clean:
	docker-compose -f docker-compose.yml down -v

docker-logs:
	docker-compose -f docker-compose.yml logs -f

# Health Check
health:
	curl -f http://localhost:8000/health || echo "Health check failed"
