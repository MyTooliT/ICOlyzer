# -- Variables -----------------------------------------------------------------

ifeq ($(OS), Windows_NT)
	OPERATING_SYSTEM := windows
else
	OS_NAME := $(shell uname -s)
	ifeq ($(OS_NAME), Linux)
		OPERATING_SYSTEM := linux
	else
		OPERATING_SYSTEM := mac
	endif
endif

# -- Rules ---------------------------------------------------------------------

all: check test

check:
	flake8 .
	mypy icolyzer

test: pytest-$(OPERATING_SYSTEM)

pytest-linux: pytest-mac
pytest-mac:
	pytest .
pytest-windows:
	pytest -p no:prysk .
