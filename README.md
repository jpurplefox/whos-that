# Who's That Pokemon?

A Pokemon guessing game. The player must guess which Pokemon it is based on hints.

## Requirements

- Docker and Docker Compose

## Getting Started

```bash
git clone https://github.com/jpurplefox/whos-that.git
cd whos-that
```

## Configuration

Create a `.env` file in the project root (optional):

```env
MAX_ATTEMPTS=4
MAX_POKEMON_NUMBER=151
POKEAPI_BASE_URL=https://pokeapi.co/api/v2/pokemon
HTTP_TIMEOUT=10.0
SENTRY_DSN=https://your-key@o12345.ingest.sentry.io/12345
```

## Running

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.
Changes in `src/` are picked up automatically (hot reload).

## Tests

```bash
docker compose run --rm app python -m pytest
docker compose run --rm app python -m pytest --cov=src --cov-report=term-missing
docker compose run --rm app python -m mypy src/
```
