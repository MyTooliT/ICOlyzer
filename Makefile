# -- Variables -----------------------------------------------------------------

ifeq ($(OS), Windows_NT)
	# Disable Prysk Pytest plugin
	export PYTEST_DISABLE_PLUGIN_AUTOLOAD := ""
endif

PACKAGE := icolyzer

# -- Rules ---------------------------------------------------------------------

.PHONY: all check test

all: check test

check:
	flake8 .
	mypy $(PACKAGE)
	pylint $(PACKAGE)

test:
	pytest .
