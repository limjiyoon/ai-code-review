init:
	@command -v uv >/dev/null 2>&1 || (echo "uv not installed. Installing..." && curl -sSf https://uv.astral.sh/uv/install.sh | sh && echo "uv is installed!")
	uv sync
	uv run pre-commit install

format:
	@echo "Formatting code..."
	uvx ruff format

format-check:
	uvx ruff format --diff

lint:
	@echo "Linting code..."
	uv run pyright --project src
	uvx ruff check src --fix

test:
	@echo "Running tests..."
	uv run pytest tests/${target} -vv -cov=config_manager --cov-config=.coveragerc --cov-report=html --cov-report=term-missing --cov-fail-under=100
	coverage-badge -fo coverage.svg
