.PHONY: help install dev test lint format clean docker-up docker-down docker-build db-init db-migrate server worker dashboard rag-service health-check

help:
	@echo "DDN AI Test Analysis System - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install Python dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start all services locally"
	@echo "  make dev-api          Start API server (port 5000)"
	@echo "  make dev-worker       Start Celery worker"
	@echo "  make dev-dashboard    Start dashboard (port 5173)"
	@echo "  make dev-rag          Start RAG service (port 5006)"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test             Run all tests"
	@echo "  make test-fast        Run tests without coverage"
	@echo "  make lint             Run linters (pylint, black)"
	@echo "  make format           Format code with Black"
	@echo "  make type-check       Run type checking (mypy)"
	@echo ""
	@echo "Database:"
	@echo "  make db-init          Initialize database schema"
	@echo "  make db-migrate       Run Alembic migrations"
	@echo "  make db-seed          Load sample data"
	@echo "  make db-reset         Drop and recreate database"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start all containers"
	@echo "  make docker-down      Stop all containers"
	@echo "  make docker-restart   Restart services"
	@echo "  make docker-logs      View container logs"
	@echo ""
	@echo "Other:"
	@echo "  make clean            Remove generated files"
	@echo "  make health-check     Check service health"
	@echo ""

# Setup & Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Development - Individual Services
dev-api:
	cd implementation && python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000

dev-worker:
	cd implementation && celery -A agents.celery_app worker --loglevel=info

dev-dashboard:
	cd dashboard && npm run dev

dev-rag:
	cd implementation && python services/rag_service.py

# Development - All Services
dev:
	@echo "Starting all services..."
	@echo "API: http://localhost:5000"
	@echo "Dashboard: http://localhost:5173"
	@echo "RAG Service: http://localhost:5006"
	@echo "Langfuse: http://localhost:3000"
	@echo ""
	docker-compose up -d
	sleep 2
	$(MAKE) db-init
	@echo "Services started. Run: make health-check"

# Testing
test:
	pytest tests/ -v --cov=implementation --cov-report=html

test-fast:
	pytest tests/ -v

test-integration:
	pytest tests/integration/ -v

test-unit:
	pytest tests/unit/ -v

# Code Quality
lint:
	pylint implementation/ --disable=all --enable=E,F
	black --check implementation/ tests/

format:
	black implementation/ tests/

type-check:
	mypy implementation/ --ignore-missing-imports

# Database
db-init:
	cd implementation && python create_database.py

db-migrate:
	cd implementation && alembic upgrade head

db-seed:
	cd implementation && python seed_database.py

db-reset:
	cd implementation && python -c "from models.base import Base; from sqlalchemy import create_engine; engine = create_engine('postgresql://'); Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-restart:
	docker-compose restart

docker-logs:
	docker-compose logs -f

docker-status:
	docker-compose ps

# Health Checks
health-check:
	@echo "Checking service health..."
	@curl -s http://localhost:5000/health || echo "API: DOWN"
	@curl -s http://localhost:5006/health || echo "RAG Service: DOWN"
	@curl -s http://localhost:5173 > /dev/null && echo "Dashboard: UP" || echo "Dashboard: DOWN"
	@docker ps -q | wc -l
	@echo "Docker containers running"

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf build/ dist/ *.egg-info/
