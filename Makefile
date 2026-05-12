PORT ?= 8000

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

install:
	uv sync

collectstatic:
	uv run manage.py collectstatic

migrate:
	uv run manage.py migrate

start:
	uv run manage.py runserver $(PORT)

stop:
	@lsof -t -i :$(PORT) | xargs kill -9 || true

restart: stop start

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

lang-files:
	uv run manage.py makemessages -l ru
	uv run manage.py compilemessages
