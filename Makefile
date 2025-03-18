.PHONY: setup setup-backend setup-frontend run-backend run-backend-docker run-frontend start-dev start-prod start-docker lint-backend lint-frontend test-backend test-frontend docker-up docker-down docker-build docker-rebuild clean

# Development environment setup
setup: setup-backend setup-frontend

setup-backend:
	chmod +x setup.sh
	./setup.sh

setup-frontend:
	cd src && npm install

# Running services
run-backend:
	cd docautomation_backend && source venv/bin/activate && python manage.py runserver

run-backend-docker:
	docker-compose up backend

run-frontend:
	cd src && npm run dev

# Start scripts
start-dev:
	chmod +x scripts/start-dev.sh
	./scripts/start-dev.sh

start-prod:
	chmod +x scripts/start-prod.sh
	./scripts/start-prod.sh

start-docker:
	chmod +x scripts/start-docker.sh
	./scripts/start-docker.sh

# Code quality checks
lint-backend:
	cd docautomation_backend && flake8 .

lint-frontend:
	cd src && npm run lint

# Tests
test-backend:
	cd docautomation_backend && python manage.py test

test-frontend:
	cd src && npm test

# Docker commands
docker-up:
	docker-compose up

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf docautomation_backend/static/
	rm -rf dist
	rm -rf node_modules
	rm -rf .pytest_cache

help:
	@echo "Available commands:"
	@echo "setup              - Set up development environment (backend and frontend)"
	@echo "setup-backend      - Set up backend development environment"
	@echo "setup-frontend     - Set up frontend development environment"
	@echo "run-backend        - Run backend server"
	@echo "run-backend-docker - Run backend server in Docker"
	@echo "run-frontend       - Run frontend server"
	@echo "start-dev          - Start both backend and frontend in development mode with browser"
	@echo "start-prod         - Start in production mode with built frontend"
	@echo "start-docker       - Start using Docker and open browser"
	@echo "lint-backend       - Run linting on backend"
	@echo "lint-frontend      - Run linting on frontend"
	@echo "test-backend       - Run backend tests"
	@echo "test-frontend      - Run frontend tests"
	@echo "docker-up          - Start all services with Docker"
	@echo "docker-down        - Stop all Docker services"
	@echo "docker-build       - Build Docker images"
	@echo "docker-rebuild     - Rebuild and restart Docker containers (fix most issues)"
	@echo "clean              - Clean generated files"
