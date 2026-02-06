from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_POKEMON_JSON = Path(__file__).parent / "data" / "pokemon.json"
_DEFAULT_BALANCE_JSON = Path(__file__).parent / "data" / "balance.json"
_DEFAULT_TYPE_CHART_JSON = Path(__file__).parent / "data" / "type_chart.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    max_pokemon_number: int = 151
    pokemon_json_path: Path = _DEFAULT_POKEMON_JSON
    balance_json_path: Path = _DEFAULT_BALANCE_JSON
    type_chart_json_path: Path = _DEFAULT_TYPE_CHART_JSON
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 1.0
    database_url: str = ""
    cors_allowed_origins: list[str] = ["*"]
    use_connection_pool: bool = True

    # JWT
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 168  # 1 week

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
