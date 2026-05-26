.PHONY: install install-backend install-frontend dev stop fmt lint test

BACKEND_DIR=backend
FRONTEND_DIR=frontend
VENV=$(BACKEND_DIR)/.venv

install: install-backend install-frontend

install-backend:
	@if [ ! -d "$(VENV)" ]; then \
		if command -v python3.10 >/dev/null 2>&1; then \
			python3.10 -m venv $(VENV); \
		else \
			python3 -m venv $(VENV); \
		fi; \
	fi
	@. $(VENV)/bin/activate && pip install -r $(BACKEND_DIR)/requirements.txt

install-frontend:
	@npm install --prefix $(FRONTEND_DIR)

dev:
	@bash -c 'set -e; \
		if [ ! -d "$(VENV)" ]; then $(MAKE) install-backend; fi; \
		if [ ! -d "$(FRONTEND_DIR)/node_modules" ]; then $(MAKE) install-frontend; fi; \
		. $(VENV)/bin/activate; \
		uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir $(BACKEND_DIR) & BACK_PID=$$!; \
		npm run dev --prefix $(FRONTEND_DIR) -- --host 0.0.0.0 --port 5173 & FRONT_PID=$$!; \
		trap "kill $$BACK_PID $$FRONT_PID" INT TERM EXIT; \
		wait'

stop:
	@-pkill -f "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir $(BACKEND_DIR)" >/dev/null 2>&1 || true
	@-pkill -f "vite" >/dev/null 2>&1 || true

fmt:
	@bash -c 'set -e; \
		if [ ! -d "$(VENV)" ]; then $(MAKE) install-backend; fi; \
		if [ ! -d "$(FRONTEND_DIR)/node_modules" ]; then $(MAKE) install-frontend; fi; \
		. $(VENV)/bin/activate; \
		pip install -r $(BACKEND_DIR)/requirements-dev.txt >/dev/null; \
		ruff format $(BACKEND_DIR)/app $(BACKEND_DIR)/tests; \
		npm run format --prefix $(FRONTEND_DIR)'

lint:
	@bash -c 'set -e; \
		if [ ! -d "$(VENV)" ]; then $(MAKE) install-backend; fi; \
		if [ ! -d "$(FRONTEND_DIR)/node_modules" ]; then $(MAKE) install-frontend; fi; \
		. $(VENV)/bin/activate; \
		pip install -r $(BACKEND_DIR)/requirements-dev.txt >/dev/null; \
		ruff check $(BACKEND_DIR)/app $(BACKEND_DIR)/tests; \
		npm run lint --prefix $(FRONTEND_DIR)'

test:
	@bash -c 'set -e; \
		if [ ! -d "$(VENV)" ]; then $(MAKE) install-backend; fi; \
		if [ ! -d "$(FRONTEND_DIR)/node_modules" ]; then $(MAKE) install-frontend; fi; \
		. $(VENV)/bin/activate; \
		pip install -r $(BACKEND_DIR)/requirements-dev.txt >/dev/null; \
		PYTHONPATH=$(BACKEND_DIR) pytest -q $(BACKEND_DIR)/tests; \
		npm run test --prefix $(FRONTEND_DIR)'
