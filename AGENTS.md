# AGENTS.md

## Commands

```bash
make install       # poetry install
make test          # pytest -q (53 tests, all must pass)
make test-v        # pytest -v
make test-cov      # pytest --cov=src --cov-report=term-missing
make lint          # ruff check src/ tests/
make format        # ruff format src/ tests/
make check         # lint + test (no typecheck)
make db-upgrade    # alembic upgrade head
make db-reset      # rm data/axenda.db && alembic upgrade head && scrape
make scrape        # run all scrapers
make bot           # start Telegram bot
make chat          # interactive LLM chat CLI
```

- **Python >=3.12**, managed with **Poetry** (not pip/uv).
- Run `make check` before committing. The repo has no CI, pre-commit hooks, or Docker.
- MyPy is configured (`strict = true`) but has pre-existing errors; it is **not** part of CI. Only lint + test are required.

## Architecture (Clean Architecture)

```
src/axenda/
  domain/          # Pure models, repos (abstract), value objects — NO infra imports
  application/     # Use cases (SearchEventsUseCase) — orchestrates LLM + repos
  infrastructure/  # SQLAlchemy ORM, Ollama client, scrapers, config
  interfaces/      # Telegram bot handlers, future API
```

- **Domain must not import from infrastructure.** If you need a new abstract port, add it to `domain/repositories.py`.
- New scraper? Subclass `infrastructure/scraper/base.py` and register in `registry.py`.
- New LLM tool? Define it in `infrastructure/llm/tools.py` and add handler in `application/search_events.py:_execute_tool`.

## Database

- SQLite via `sqlite+aiosqlite:///data/axenda.db` (async). The DB file lives at `data/axenda.db` and is gitignored.
- Alembic env (`alembic/env.py`) auto-converts the async URL to sync for migrations. If you change the URL scheme, update the `replace()` call there.
- Tests use in-memory SQLite — no real DB needed.

## Environment

Copy `.env.example` to `.env` and fill in values. The `.env` file is gitignored.
Key variables: `TELEGRAM_BOT_TOKEN`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`.

## Ollama dependency

The bot, `scripts/chat.py`, and `scripts/test_llm.py` require a **running local Ollama** server (`ollama serve`). The default model is `llama3.2:3b`. Tests that mock the LLM client do not need Ollama.

## Scraper

- The Gijon Drupal scraper (`gijon_opendata.py`) has a hardcoded `_min_date = datetime(2026, 1, 1, tzinfo=UTC)`. Events before that date are silently dropped. Update this if you need older data.
- Normalized city name for Gijón is `"gijon"` (lowercase, no accent). Use `_normalize_city()` from `axenda.domain.text` when comparing.

## Tests

- `asyncio_mode = "auto"` — async test functions are auto-detected; no `@pytest.mark.asyncio` needed.
- `53 tests` in 7 modules. Must pass with `make test`.

## Entry points

| Command | Module |
|---------|--------|
| `poetry run bot` | `axenda.interfaces.telegram.bot:main` |
| `poetry run scrape` | `scripts.run_scrapers:main` |
| `make bot` | `python -m axenda.interfaces.telegram.bot` |

## Style

- Ruff lint selects: `E, F, I, N, W, UP` (no docstring/formatting rules).
- Line length: 100.
- Formatter: `ruff format` (line length 100).
- Spanish comments and user-facing strings; English code identifiers.
