.PHONY: help install run test docker-build docker-run docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the application locally"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make docker-up    - Start all services with docker-compose"
	@echo "  make docker-down  - Stop all services"
	@echo "  make clean        - Clean temporary files"

install:
	pip install -r requirements.txt

run:
	streamlit run app.py --server.port=8501

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=components --cov=app --cov-report=term

docker-build:
	docker build -t aura-kg-frontend .

docker-run:
	docker run -p 8501:8501 --name aura-kg-frontend aura-kg-frontend

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
