.PHONY: help install run dev test lint format clean docker-up docker-down check

help:
	@echo "Homeopathy AI - Available Commands"
	@echo "=================================="
	@echo "make install      - Install dependencies"
	@echo "make run          - Run the server"
	@echo "make dev          - Run in development mode with auto-reload"
	@echo "make test         - Run tests"
	@echo "make lint         - Run linting"
	@echo "make format       - Format code"
	@echo "make clean        - Clean up cache and temp files"
	@echo "make check        - Verify setup"
	@echo "make docker-up    - Start Docker services"
	@echo "make docker-down  - Stop Docker services"

install:
	pip install -r requirements.txt

run:
	python -m uvicorn main:app --host 0.0.0.0 --port 8000

dev:
	python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	black .
	isort .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

check:
	python check_setup.py

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
