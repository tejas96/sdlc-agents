# Makefile for SDLC Agents API development
# Usage: make <target> [ARGS="..." / PYTEST_ARGS="..." / HOST=... / PORT=... / RELOAD=...]

PYTHON ?= python
SRC_PATHS := alembic app tests manage.py
PYTEST_ARGS ?=
ARGS ?=

.PHONY: help format test run prestart manage lint clean

help:
	@printf "Available targets:\n"
	@printf "  format    - run isort then black on source paths\n"
	@printf "  test      - run pytest (pass PYTEST_ARGS)\n"
	@printf "  lint      - run ruff (auto-fix) then mypy for type checks\n"
	@printf "  prestart  - run manage.py prestart (waits for DB, migrates, seeds)\n"
	@printf "  run       - run the app via manage.py run (pass ARGS or HOST/PORT/RELOAD)\n"
	@printf "  manage    - wrapper to invoke manage.py via python (pass ARGS)\n"
	@printf "  clean     - clean __pycache__ and .pytest_cache\n"

# Format: isort then black to keep consistent import ordering
format:
	@echo "🔧 Running isort on: $(SRC_PATHS)"
	@$(PYTHON) -m isort $(SRC_PATHS)
	@echo "🧹 Running black on: $(SRC_PATHS)"
	@$(PYTHON) -m black $(SRC_PATHS)

# Run tests with optional extra args
test:
	@echo "🧪 Running pytest"
	@$(PYTHON) -m pytest --cov=app --cov-report=term-missing $(PYTEST_ARGS)

# Linting: run ruff (auto-fix where possible) then mypy for type checks
lint:
	@echo "🔎 Running ruff (auto-fix) on: $(SRC_PATHS)"
	@$(PYTHON) -m ruff check $(SRC_PATHS) --fix || echo "⚠️  ruff reported issues"
	@echo "🔎 Running mypy on 'app'"
	@$(PYTHON) -m mypy app || echo "⚠️  mypy reported type issues"

# Run the app via manage.py run. Accepts ARGS or HOST/PORT/RELOAD variables.
run:
	@echo "🚀 Starting app via manage.py run"
	@$(PYTHON) manage.py run --port 8000 --reload --log-level debug
 d
# Wrapper to invoke manage.py with any args
manage:
	@$(PYTHON) manage.py $(ARGS)

clean:
	@echo "🧹 Cleaning __pycache__ and .pytest_cache"
	@find . -name "__pycache__" -type d -print0 | xargs -0 rm -rf || true
	@rm -rf .pytest_cache || true

migrate:
	@echo "🔄 Running migrations"
	@$(PYTHON) manage.py upgrade
