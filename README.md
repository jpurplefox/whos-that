# Who's That Pokemon?

A Pokemon guessing game. The player must guess which Pokemon it is based on hints.

## Requirements

- Python 3.13+

## Installation

```bash
# Clone the repository
git clone https://github.com/jpurplefox/whos-that.git
cd whos-that

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (optional):

```env
MAX_ATTEMPTS=4
MAX_POKEMON_NUMBER=151
POKEAPI_BASE_URL=https://pokeapi.co/api/v2/pokemon
HTTP_TIMEOUT=10.0
```

## Running

```bash
cd src
uvicorn api.app:app --reload
```

The API will be available at `http://localhost:8000`

## Tests

```bash
# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src --cov-report=term-missing

# Run mypy
python -m mypy src/
```
