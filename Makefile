PORT ?= 8000

lint:
	uv run ruff check task_manager

lint-fix:
	uv run ruff check task_manager --fix

install:
	uv sync

collectstatic:
	uv run manage.py collectstatic

migrate:
	uv run manage.py migrate

start:
	uv run manage.py runserver $(PORT)

render-start:
	gunicorn task_manager.wsgi

build:
	./build.sh

test:
	uv run manage.py test

test-cov:
	uv run coverage run manage.py test

test-clean:
	rm -rf htmlcov/
	rm -f .coverage
