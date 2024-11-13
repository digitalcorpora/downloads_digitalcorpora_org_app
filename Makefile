PYLINT_FILES=$(shell /bin/ls *.py  | grep -v bottle.py | grep -v app_wsgi.py)
PYLINT_THRESHOLD=9.5

################################################################
# Manage the virtual environment
A   = . venv/bin/activate
REQ = venv/pyvenv.cfg
PYTHON=$(A) ; python3.9
PIP_INSTALL=$(PYTHON) -m pip install --no-warn-script-location
venv/pyvenv.cfg:
	python3.9 -m venv venv

venv:
	python3.9 -m venv venv

################################################################
#
all:
	@echo verify syntax and then restart
	make pylint
	make touch

check:
	make pylint
	make pytest

touch:
	touch tmp/restart.txt

pylint: $(REQ)
	$(PYTHON) -m pylint --rcfile .pylintrc --fail-under=$(PYLINT_THRESHOLD) --verbose $(PYLINT_FILES)

pytest: $(REQ)
	$(PYTHON) -m pytest .

pytest-debug: $(REQ)
	$(PYTHON) -m pytest -v --log-cli-level=DEBUG

coverage:
	$(PYTHON) -m pip install pytest pytest_cov
	$(PYTHON) -m pytest -v --cov=. --cov-report=xml tests


freeze:
	$(PYTHON) -m pip freeze > requirements.txt

################################################################
# Installations are used by the CI pipeline:
# Generic:
install-python-dependencies: $(REQ)
	$(PYTHON) -m pip install --upgrade pip
	if [ -r requirements.txt ]; then $(PIP_INSTALL) -r requirements.txt ; else echo no requirements.txt ; fi

# Includes ubuntu dependencies
install-ubuntu: $(REQ)
	echo on GitHub, we use this action instead: https://github.com/marketplace/actions/setup-ffmpeg
	$(PYTHON) -m pip install --upgrade pip
	if [ -r requirements-ubuntu.txt ]; then $(PIP_INSTALL) -r requirements-ubuntu.txt ; else echo no requirements-ubuntu.txt ; fi
	if [ -r requirements.txt ];        then $(PIP_INSTALL) -r requirements.txt ; else echo no requirements.txt ; fi

install-macos-python: $(REQ)
	brew update
	brew upgrade
	brew install python3

# Includes MacOS dependencies managed through Brew
install-macos: $(REQ)
	brew update
	brew upgrade
	$(PYTHON) -m pip install --upgrade pip
	if [ -r requirements-macos.txt ]; then $(PIP_INSTALL) -r requirements-macos.txt ; else echo no requirements-ubuntu.txt ; fi
	if [ -r requirements.txt ];       then $(PIP_INSTALL) -r requirements.txt ; else echo no requirements.txt ; fi

clean:
	find . -name '*~' -exec rm {} \;
