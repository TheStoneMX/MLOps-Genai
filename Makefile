.PHONY: venv clean clean-build clean-pyc clean-test clean-docs clean-data lint tests tests-basic tests-e2e cov cov-basic docs dist install jupyter pre-commit format cruft

.SILENT: clean-build clean-pyc clean-test clean-docs clean-data clean-ruff

PYTHON=python3
PIP=pip3
POETRY=poetry

venv:
	$(PIP) install --no-cache-dir --upgrade pip wheel poetry==1.8.0
	$(POETRY) config virtualenvs.create false
	$(POETRY) lock --no-update
	$(POETRY) install --all-extras

api:
	uvicorn alxn_test.api:app --reload

docker_api:
	uvicorn alxn_test.api:app --host 0.0.0.0 --port 8000

clean: clean-build clean-pyc clean-test clean-docs clean-data clean-ruff

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .ipynb_checkpoints
	rm -fr *.log
	rm -fr *.log.*
	rm -f test_result.xml
	rm -f .testmondata

clean-docs:
	rm -f docs/source/modules.rst
	rm -f docs/source/alxn_test*.rst
	rm -f docs/source/*.md
	rm -rf docs/build

clean-data:
	find data -type f \( ! -name ".gitkeep" \) -exec rm -f {} +
	find data -type d \( ! -wholename "data" \) -exec rm -fr {} +

clean-ruff:
	rm -rf .ruff_cache

dist: clean
	$(POETRY) build -f wheel

lint:
	ruff alxn_test tests

tests:
	pytest -v tests

tests-basic:
	pytest -v tests/unit tests/integration

tests-e2e:
	pytest -v tests/e2e

cov:
	coverage run --source alxn_test -m pytest tests --junit-xml=test_result.xml
	coverage report -m
	coverage html
	coverage xml

cov-basic:
	coverage run --omit=alxn_test/scripts/*,*/__init__.py,alxn_test/__main__.py --source alxn_test -m pytest tests/unit tests/integration --junit-xml=test_result.xml
	coverage report -m
	coverage html
	coverage xml

docs: clean-docs
	sphinx-apidoc -o docs/source alxn_test
	cp RELEASE_NOTES.md docs/source/release_notes.md
	sphinx-build -b html -c docs/source -W docs/source docs/build -D autodoc_member_order="bysource"

install:
	$(POETRY) install

jupyter:
	export PYTHONPATH=$(shell pwd) && jupyter notebook --allow-root

pre-commit:
	pre-commit run --all-files

format:
	black -l 100 .
	ruff -s --fix --exit-zero .
	docformatter -r -i --wrap-summaries 100 --wrap-descriptions 90 .
