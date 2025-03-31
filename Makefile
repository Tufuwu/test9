.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
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
	rm -rf tests/testcontent/downloaded/*
	rm -rf tests/testcontent/generated/*

lint: ## check style with flake8
	flake8 ricecooker tests

test: clean-test ## run tests quickly with the default Python
	pytest


test-all: clean-test ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	pip install coverage pytest
	coverage run --source ricecooker -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docsclean:
	$(MAKE) -C docs clean
	rm -f docs/_build/*

docs: ## generate Sphinx HTML documentation
	pip install -r docs/requirements.txt
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	# $(BROWSER) docs/build/html/index.html

latexdocs:
	pip install -r docs/requirements.txt
	$(MAKE) -C docs clean
	$(MAKE) -C docs latex

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean ## package and upload a release
	pip install twine
	python setup.py sdist
	twine upload dist/*

install: clean ## install the package to the active Python's site-packages
	python setup.py install
