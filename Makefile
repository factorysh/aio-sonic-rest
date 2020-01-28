PYTHON_VERSION = $(shell python3 -V | cut -d ' ' -f 2 - | cut -d '.' -f 1,2 -)


install: venv/lib/python${PYTHON_VERSION}/site-packages/asonic/__init__.py

venv/bin/python:
	python3 -m venv venv
	venv/bin/pip install -U pip wheel

venv/lib/python${PYTHON_VERSION}/site-packages/asonic/__init__.py: venv/bin/python
	venv/bin/pip install .[tests]


sonic:
	docker-compose up -d

down:
	docker-compose down

ps:
	docker-compose ps

test: install sonic
	venv/bin/pytest

clean:
	rm -rf data venv
