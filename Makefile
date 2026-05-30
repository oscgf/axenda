.PHONY: install db-upgrade db-reset scrape chat bot test lint format check

install:
	poetry install

db-upgrade:
	poetry run alembic upgrade head

db-reset:
	rm -f data/axenda.db
	poetry run alembic upgrade head
	poetry run python scripts/run_scrapers.py

scrape:
	poetry run python scripts/run_scrapers.py

chat:
	poetry run python scripts/chat.py

bot:
	poetry run python -m axenda.interfaces.telegram.bot

test:
	poetry run pytest -q

test-v:
	poetry run pytest -v

test-cov:
	poetry run pytest --cov=src --cov-report=term-missing

lint:
	poetry run ruff check src/ tests/

format:
	poetry run ruff format src/ tests/

check: lint test

db-summary:
	poetry run python scripts/db_summary.py

db-types:
	poetry run python scripts/db_event_types.py

db-upcoming:
	poetry run python scripts/db_upcoming.py

db-venues:
	poetry run python scripts/db_top_venues.py

db-months:
	poetry run python scripts/db_by_month.py

db-music:
	poetry run python scripts/db_music.py
