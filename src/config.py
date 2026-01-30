from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_POKEMON_JSON = Path(__file__).parent / "data" / "pokemon.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    max_attempts: int = 4
    max_pokemon_number: int = 151
    pokemon_json_path: Path = _DEFAULT_POKEMON_JSON
    pokedex_max_battery: int = 100
    pokedex_stat_cost: int = 40
    pokedex_battery_recovery: int = 10
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 1.0
    database_url: str = ""
    cors_allowed_origins: list[str] = ["*"]
    use_connection_pool: bool = True
