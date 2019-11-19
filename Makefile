###
#
# Copyright © 2019 Jan Frömberg (http://www.gerdi-project.de)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

ROOT_DIR:=./
SRC_DIR:=./
VENV_BIN_DIR:="venv/bin"

VIRTUALENV:=$(shell which virtualenv)

REQUIREMENTS_DIR:="."
REQUIREMENTS_LOCAL:="$(REQUIREMENTS_DIR)/requirements_local.txt"
REQUIREMENTS_DOCKER:="$(REQUIREMENTS_DIR)/requirements.txt"

PIP:="$(VENV_BIN_DIR)/pip"
FLAKE8:="$(VENV_BIN_DIR)/flake8"
ISORT:="$(VENV_BIN_DIR)/isort"
AUTOPEP8:="$(VENV_BIN_DIR)/autopep8"

CMD_FROM_VENV:=". $(VENV_BIN_DIR)/activate; which"
PYTHON=$(shell "$(CMD_FROM_VENV)" "python")

# Make will use these given recipes instead of file executables
# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
.PHONY: hello venv freeze qa check fix clean migrations superuser runlocal test

hello:
	@echo ""
	@echo "You can use a command from the list: check, fix, clean, runlocal, dockerrun, ..."
	@echo "-> See Makefile for more information."
	@echo ""

# DEVELOPMENT

define create-venv
virtualenv venv -p python3
endef

venv:
	@$(create-venv)
	@$(PIP) install -r $(REQUIREMENTS_LOCAL)

freeze: venv
	@$(PIP) freeze > $(REQUIREMENTS_LOCAL)

# quality assurance
qa: check fix

check: venv
	@$(FLAKE8) --max-line-length 120 api hcc_py
	@$(ISORT) -rc -c api hcc_py

fix: venv
	@$(ISORT) -rc api hcc_py
	@$(AUTOPEP8) --in-place --aggressive --recursive api hcc_py

clean:
	@rm -rf .cache
	@rm -rf htmlcov coverage.xml .coverage
	@find . -name *.pyc -delete
	#@find . -name db.sqlite3 -delete
	@find . -type d -name __pycache__ -delete
	@rm -rf venv
	@rm -rf .tox

# TOOLS/SCRIPTS

migrations: venv
	@$(PYTHON) $(SRC_DIR)/manage.py makemigrations $(app) --settings hcc_py.settings_local

migrate: venv
	@$(PYTHON) $(SRC_DIR)/manage.py migrate $(app) $(migration) --settings hcc_py.settings_local

superuser: venv
	@$(PYTHON) $(SRC_DIR)/manage.py createsuperuser --settings hcc_py.settings_local

# LOCAL

runlocal: venv
	@$(PYTHON) $(SRC_DIR)/manage.py runserver --settings hcc_py.settings_local

# DOCKER

docker:
	@docker build -t harvest/hccenter:latest .

dockerrun:
	@docker build -t harvest/hccenter:latest .
	@docker run --name=gerdi_hcc -it -p 8080:80 harvest/hccenter:latest

# TEST

test: venv
	@$(PYTHON) $(SRC_DIR)/manage.py test --settings hcc_py.settings_local
