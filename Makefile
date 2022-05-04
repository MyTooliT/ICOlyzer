all: check test

check:
	flake8 .
	mypy .

test:
	pytest
