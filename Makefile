.PHONY: help install dev backend frontend test test-e2e build lint docker-up docker-down migrate clean

# Default target
help:
	@echo "AutoMeeting Development Commands"
	@echo "================================="
	@echo "make install        - Install all dependencies"
	@echo "make dev            - Start development servers"
	@echo "make backend        - Start backend only"
	@echo "make frontend       - Start frontend only"
	@echo "make test           - Run backend tests"
	@echo "make test-e2e       - Run E2E tests"
	@echo "make build          - Build for production"
	@echo "make lint           - Run linters"
	@echo "make docker-up      - Start Docker services"
	@echo "make docker-down    - Stop Docker services"
	@echo "make migrate        - Run database migration"
	@echo "make clean          - Clean generated files"

# Install dependencies
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Start development servers
dev:
	@echo "Starting backend..."
	cd backend && uvicorn app.main:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm run dev

# Start backend only
backend:
	cd backend && uvicorn app.main:app --reload --port 8000

# Start frontend only
frontend:
	cd frontend && npm run dev

# Run backend tests
test:
	cd backend && pytest tests/ -v

# Run E2E tests
test-e2e:
	cd frontend && npx playwright test

# Build for production
build:
	cd frontend && npm run build
	@echo "Build complete. Run 'make docker-up' to start services."

# Run linters
lint:
	cd backend && ruff check .
	cd frontend && npx eslint src --ext .ts,.tsx

# Start Docker services
docker-up:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Services started. Backend: http://localhost:8000, Frontend: http://localhost:5173"

# Stop Docker services
docker-down:
	docker-compose -f docker-compose.dev.yml down

# Run database migration
migrate:
	cd backend && python -m scripts.migrate_sqlite_to_postgres --migrate --target "postgresql+asyncpg://automeeting:automeeting_dev@localhost:5432/automeeting"

# Clean generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f backend/*.db
	rm -f migration_data.json
	cd frontend && rm -rf dist node_modules/.vite
	@echo "Clean complete."