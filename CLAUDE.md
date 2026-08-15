# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Curriculum-Automation is a lead-gen/scraping backend: given a company domain, it scrapes the site, extracts and classifies relevant links/emails, and persists companies and contacts to a Supabase Postgres database. Only the `backend` has code so far; `frontend/` exists but is empty.

## Setup & commands

The Python project (and its `uv` environment) lives at `backend/` — `pyproject.toml`, `uv.lock`, `.python-version` (3.14) and `.venv` are all there. The actual code is one level down, in `backend/src/`, which is the importable `src` package (see "Import convention" below).

```bash
cd backend
uv sync                        # install dependencies
uv run python -m src.main      # current entrypoint is a placeholder ("Hello from src!"); no FastAPI app is wired up yet
```

Dependencies: `fastapi`, `uvicorn`, `sqlmodel`, `asyncpg`, `python-dotenv` (see `backend/pyproject.toml`). Note `bs4` (used by `ParserAdapter`) and `httpx` (used by `ScraperAdapter`) are imported in the code but are **not** listed in `pyproject.toml` — `uv sync` won't install them; add them if you touch those adapters.

There is currently no test suite (no `tests/` directory, no pytest config) and no linter/formatter config (no ruff/mypy config anywhere in the repo) — don't assume either exists when planning work.

Two `.env` files carry runtime config and are not committed: `backend/src/infrastructure/database/.env` (must define `DATABASE_URL` for the Supabase/Postgres connection — `connection.py` raises at import time if it's missing) and `backend/src/infrastructure/adapters/.env`.

## Import convention

There are no `__init__.py` files anywhere in `backend/`; the codebase relies on implicit namespace packages. Every internal import is absolute, e.g. `from src.domain.entities.company import Company`. For those to resolve, `backend/` (the parent of `src/`, and now also where `pyproject.toml`/`.venv` live) must be on `sys.path` — which happens automatically when an entrypoint is run **as a module from `backend/`**, e.g. `uv run python -m src.main` or `uv run python -m src.infrastructure.database.migrate`. Running a file as a plain script (`uv run python src/main.py`) does *not* add `backend/` to `sys.path` and will break these imports — always use `-m` from `backend/`, don't add manual `sys.path` hacks per file.

## Architecture: Clean/Hexagonal

Dependency rule points inward: `infrastructure` → `application` → `domain`. Domain has zero framework/I-O dependencies.

- **`domain/entities`** — rich entities (`Company`, `Contact`) that validate themselves in property setters (name-mangled private state, raise `ValueError` on invalid input). Distinct from the same-named classes in `infrastructure/database/models.py`, which are SQLModel table schemas, not domain entities.
- **`domain/services`** — pure business-logic services with no I/O. `CompanyDomainService` cleans/filters/normalizes scraped links (anchors, mailto/javascript, relative URLs, same-domain filtering, de-duping). `ContactDomainService` is currently an empty stub.
- **`application/uses_cases`** — orchestrate one use case by composing ports + domain services. `GetRelevantLinks` is the reference flow: `ScraperPort.get_html` → `ParserPort.parse_html/extract_links` → `CompanyDomainService.clean_links` → `LinkClassifierPort.classify_relevant`. `GetRelevantEmails` is currently an empty stub.
- **`application/uses_cases/ports`** — `Protocol`-based interfaces use cases depend on instead of infrastructure concretes: `ScraperPort` (`scraper_port.py`), `ParserPort` (`parser_port.py`), `LinkClassifierPort` (`link_classify_relenvant_port.py`), each imported directly by the use case that needs it.
- **`infrastructure/adapters`** — concrete port implementations. `ScraperAdapter` (httpx) validates URLs against SSRF (`validate_public_url` blocks private/local networks, non-http(s) schemes, embedded credentials) and passively detects "poison pills" (captcha/paywall/login/rate-limit/Cloudflare responses) before returning HTML. `ParserAdapter` extracts `<a href>` links via BeautifulSoup. `links_relevant_classify_adapter.py` (the `LinkClassifierPort` impl, presumably AI-based) is currently an empty stub.
- **`infrastructure/database`** — `models.py` holds SQLModel table classes; `connection.py` builds the async SQLAlchemy engine/session against `DATABASE_URL` and exposes `init_db()`/`get_db()`; `migrate.py` is a standalone script that currently calls `recreate_db()`, which is not defined anywhere in `connection.py` — it will fail as-is (pre-existing gap, not an import path issue).
- **`infrastructure/repository`** — `IRepositoryCompany`/`IRepositoryContact` are ABCs whose abstract methods are annotated in their docstrings with `UC-xx` identifiers tracing back to use cases (intended to be documented in `casos_de_uso.txt` at the repo root, which is currently empty). `repository_contact.py` already has a partial `IRepositoryContact` implementation using SQLModel's sync `Session`; `repository_company.py` is still an empty stub.

When picking up work in this backend, expect several files to be intentional stubs (empty or near-empty) rather than bugs — check git history/status before "fixing" what may just be unimplemented scaffolding.

## Persistence

Supabase Postgres, accessed via `asyncpg` + SQLModel/SQLAlchemy's async engine. A local Supabase CLI project config lives at `supabase/config.toml`.

## Reference skills

`.agents/skills/` contains vendored skill docs (`supabase`, `supabase-postgres-best-practices`, `fastapi-expert`, `postgres`, `web-scraping`), pulled via `skills-lock.json` from `supabase/agent-skills`. These are best-practice references for agents to consult, not application code.
