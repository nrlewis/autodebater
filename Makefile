.PHONY: clean clean-build clean-pyc clean-test coverage dist docs help install lint 

.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

dist: 
	poetry build

lint:
	poetry run pylint src tests #$$(git ls-files '*.py')

test-all: ## run tests on every Python version with tox
	PYTHONPATH=src tox

test:
	poetry run  pytest -m 'not integration'  -vv 

integration:
	poetry run pytest -m 'integration'  -vv

coverage: ## check code coverage quickly with the default Python
	poetry run coverage run --source autodebater -m pytest -m 'not integration'
	poetry run coverage report

coveralls:
	poetry run coveralls

quick_check:
	poetry run autodebater judged-debate "marty friedman is the greatest guitarist alive"
