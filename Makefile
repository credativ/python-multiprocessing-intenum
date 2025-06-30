all: lint test

lint: src/multiprocessing_intenum/_version.py
	ruff check src tests
	ruff format --check src tests
	mypy src
	mypy tests

test: src/multiprocessing_intenum/_version.py
	python3 -m unittest

.coverage: src/multiprocessing_intenum/_version.py
	coverage run --source=src --module unittest
	coverage combine

coverage: .coverage
	coverage report --show-missing

coverage.xml: .coverage
	coverage xml

dist:
	uv build

src/multiprocessing_intenum/_version.py:
	$(MAKE) dist

clean:
	rm -f src/multiprocessing_intenum/_version.py
	rm -rf __pycache__ src/*/__pycache__ tests/__pycache__
	rm -rf dist
	rm -rf src/*.egg-info
	rm -rf .coverage
	rm -f .coverage.*

.PHONY: all clean coverage lint test dist
