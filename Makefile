# A-Maze-ing - common tasks.
# `make install` creates a local virtualenv (.venv); every other rule uses it
# when it exists and falls back to the system python3 otherwise.

VENV   := .venv
PYTHON := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,python3)
CONFIG := config.txt

MYPY_FLAGS := --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test build

install:
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements.txt

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	find . -type d \( -name __pycache__ -o -name .mypy_cache \
		-o -name .pytest_cache -o -name '*.egg-info' \) \
		-not -path './$(VENV)/*' -prune -exec rm -rf {} +
	rm -rf build dist

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

test:
	$(PYTHON) -m pytest -q

# Rebuild the reusable package and copy it to the repository root.
build:
	rm -rf build dist mazegen-*.tar.gz mazegen-*.whl
	$(PYTHON) -m build
	cp dist/mazegen-* .
