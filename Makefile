.PHONY: help install train seed test run-backend run-frontend docker-up docker-down clean

help:
	@echo "AeroOptima - Predictive Air Traffic Delay & Gate Scheduling Optimizer"
	@echo ""
	@echo "make install       Install backend & frontend dependencies"
	@echo "make train         Train ML delay prediction models (offline pipeline)"
	@echo "make seed          Seed SQLite database with demo airport scenario"
	@echo "make test          Run pytest suite (unit, ML, optimizer, API tests)"
	@echo "make run-backend   Start FastAPI uvicorn server on port 8000"
	@echo "make run-frontend  Start Vite React dev server on port 5173"
	@echo "make docker-up     Start multi-container Docker deployment"
	@echo "make docker-down   Stop Docker containers"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

train:
	cd backend && python -m app.ml.train

seed:
	cd backend && python -m app.database.seed

test:
	cd backend && python -m pytest ../tests -v

run-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	rm -rf backend/__pycache__ backend/app/**/__pycache__ .pytest_cache
