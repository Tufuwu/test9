PYTHON_VERSION=python3
CLI_VERSION=$(shell grep '^__version__' globus_cli/version.py | cut -d '"' -f2)

.venv:
	virtualenv --python=$(PYTHON_VERSION) .venv
	.venv/bin/pip install -U pip setuptools
	.venv/bin/pip install -e '.[development]'

.PHONY: localdev
localdev: .venv


.PHONY: lint test reference
lint:
	tox -e lint
reference:
	tox -e reference
test:
	tox

.PHONY: showvars release
showvars:
	@echo "CLI_VERSION=$(CLI_VERSION)"
release:
	git tag -s "$(CLI_VERSION)" -m "v$(CLI_VERSION)"
	tox -e publish-release

.PHONY: clean
clean:
	rm -rf .venv .tox dist build *.egg-info
