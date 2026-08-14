.PHONY: help setup lint format type check

SHELL := /bin/bash
PYTHON := python3.11

help:  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ──────────────── Virtual Environment  ────────────────

setup:  ## Create venv and install all dependencies
	uv venv --python $(PYTHON)
	uv sync --group dev --extra train --extra dashboard
	.venv/bin/pre-commit install
	@echo ""
	@echo "Setup complete. Activate your venv with:"
	@echo "  source .venv/bin/activate"

# ──────────────── Code quality ────────────────

lint:  ## Run ruff linter
	ruff check src tests scripts

format:  ## Auto-format and fix lint issues
	ruff format src tests scripts
	ruff check --fix src tests scripts

type:  ## Run mypy type checker
	mypy src

check: lint type test  ## Run all checks (mirrors CI)
