from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    max_attempts: int = 4
    max_pokemon_number: int = 151
    pokeapi_base_url: str = "https://pokeapi.co/api/v2/pokemon"
    http_timeout: float = 10.0
    pokedex_max_battery: int = 100
    pokedex_stat_cost: int = 40
    pokedex_battery_recovery: int = 10
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 1.0
