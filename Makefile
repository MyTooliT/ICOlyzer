# -- Variables -----------------------------------------------------------------

ifeq ($(OS), Windows_NT)
	# Disable Prysk Pytest plugin
	export PYTEST_DISABLE_PLUGIN_AUTOLOAD := ""
endif

# -- Rules ---------------------------------------------------------------------

all: check test

check:
	flake8 .
	mypy icolyzer

test:
	pytest .
