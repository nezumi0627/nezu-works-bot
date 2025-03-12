# install
.PHONY: install
install:
	$(info Installing Python 3.11.11 ...)
	pyenv install 3.11.11
	$(info Creating virtual environment ...)
	poetry env use 3.11.11
	$(info Installing dependencies ...)
	poetry install
	$(info Installing pre-commit hooks ...)
	pre-commit install
