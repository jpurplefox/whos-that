# Who's That Pokemon?

A Pokemon guessing game. The player must guess which Pokemon it is based on hints.

## Requirements

- Docker and Docker Compose

## Getting Started

```bash
git clone https://github.com/jpurplefox/whos-that.git
cd whos-that
```

## Architecture

The project follows a hexagonal (ports & adapters) architecture:

```
src/
├── domain/           # Core business logic
│   ├── ports/        # Interfaces (protocols) for external dependencies
│   ├── game.py       # Game entity and rules
│   ├── hint.py       # Hint types and logic
│   └── ...
├── services/         # Application use cases
│   ├── start_game.py
│   ├── guess.py
│   ├── authenticate.py
│   └── ...
├── adapters/         # Implementations of ports
│   ├── postgres_game_repository.py
│   ├── in_memory_game_repository.py
│   └── ...
├── auth/             # Authentication implementations
│   ├── google_oauth.py
│   └── jwt_service.py
└── api/              # HTTP layer (Litestar)
    ├── views.py
    ├── schemas.py
    └── dependencies.py
```

## Configuration

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/whos_that
USE_CONNECTION_POOL=true

# JWT Authentication
JWT_SECRET=your-secret-key-at-least-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=168

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Game settings
MAX_POKEMON_NUMBER=151

# Optional
SENTRY_DSN=https://your-key@o12345.ingest.sentry.io/12345
CORS_ALLOWED_ORIGINS=["http://localhost:3000"]
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

## Disclaimer

This is a fan-made project for educational and non-commercial purposes.
All Pokemon-related content, including names, images, and data, is the property
of Nintendo, The Pokemon Company, and Game Freak.
Pokemon data is sourced from [PokeAPI](https://pokeapi.co/).
This project is not affiliated with or endorsed by any of these companies.
