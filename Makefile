.PHONY: setup dev test lint e2e seed reset benchmark down
setup:
	cd backend && python3.12 -m venv .venv && .venv/bin/pip install -e '.[dev]'
	cd frontend && npm install
dev:
	docker compose up --build
test:
	cd backend && .venv/bin/pytest -q
	cd frontend && npm test
lint:
	cd backend && .venv/bin/ruff check app tests && .venv/bin/mypy app
	cd frontend && npm run lint && npm run build && npm run format:check
e2e:
	cd frontend && npx playwright test
seed:
	cd backend && .venv/bin/python -m app.seed
reset: seed
benchmark:
	cd backend && .venv/bin/python ../scripts/benchmark.py
down:
	docker compose down

