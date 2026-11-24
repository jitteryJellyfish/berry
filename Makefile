.DEFAULT_GOAL := help

help:
	@echo "Berry - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make setup       - Create the development environment with uv"
	@echo "  make clean_setup - Clean generated files, then create the development environment"
	@echo "  make install     - Install runtime dependencies"
	@echo "  make test        - Run pytest with coverage and parallel workers"
	@echo "  make lint        - Check code with Ruff"
	@echo "  make format      - Format code with Ruff"
	@echo "  make typecheck   - Run mypy"
	@echo "  make quality     - Run lint, format, and type checks"
	@echo "  make pre-commit  - Run configured pre-commit hooks"
	@echo "  make build       - Build source and wheel distributions"
	@echo "  make clean       - Remove generated files and caches"

setup:
	uv sync --group dev

clean_setup: clean setup

install:
	uv sync

pre-commit:
	uv run pre-commit run --all-files

test:
	uv run pytest -q --cov=berry -n auto

lint:
	uv run ruff check berry

format:
	uv run ruff format berry

format-check:
	uv run ruff format --check berry

typecheck:
	uv run mypy berry

quality: lint format-check typecheck

build:
	uv build

clean:
	find berry -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" \) -prune -exec rm -rf {} +
	find berry -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist

.PHONY: help setup clean_setup install pre-commit test lint format format-check typecheck quality build clean
