SHELL := /bin/bash

PYPI_TOKEN := ${PYPI_TOKEN}

lint:
	@uv run ruff format ./src
	@uv run ruff check ./src --fix
	@uv run mypy ./src

clean:
	@rm -rf dist

build: lint clean
	@uv build

publish-test:
	@twine upload --repository-url https://test.pypi.org/legacy/ -u __token__ -p $(PYPI_TOKEN) dist/* 

publish: build
	@twine upload -u __token__ -p $(PYPI_TOKEN) dist/*
