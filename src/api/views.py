from litestar import Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.openapi.datastructures import ResponseSpec
from litestar.params import Dependency

from api.dependencies import get_consult_pokedex, get_get_game, get_guess, get_start_game
from api.schemas import GameResponse, GuessRequest
from domain.exceptions import (
    AlreadyConsultedThisTurn,
    GameNotFound,
    GameOver,
    NoStatsAvailable,
    NotEnoughBattery,
    PokemonNotFound,
)
from domain.game import ComparisonHint, Game, Hint, StatHint
from structlog_config import get_logger
from services.consult_pokedex import ConsultPokedex
from services.get_game import GetGame
from services.guess import Guess
from services.start_game import StartGame

logger = get_logger()


def _serialize_hint(hint: Hint) -> dict[str, object]:
    if isinstance(hint, StatHint):
        return {"type": "stat", "stat": hint.stat.value, "value": hint.value}
    if isinstance(hint, ComparisonHint):
        return {
            "type": "comparison",
            "pokemon": hint.pokemon.name,
            "comparisons": {s.value: c.value for s, c in hint.comparisons.items()},
        }
    return {"type": type(hint).__name__}


def _serialize_hints(game: Game) -> list[dict[str, object]]:
    return [_serialize_hint(h) for h in game.hints]


@post("/games")
async def create_game(
    start_game: StartGame = Dependency(skip_validation=True),
) -> GameResponse:
    game = await start_game.execute()
    logger.info(
        "game_started",
        game_id=game.id,
        pokemon_id=game.pokemon.id,
        pokemon_name=game.pokemon.name,
        hints=_serialize_hints(game),
    )
    return GameResponse.from_game(game)


@get(
    "/games/{game_id:str}",
    responses={404: ResponseSpec(data_container=None, description="Game not found")},
)
async def get_game(
    game_id: str,
    get_game_use_case: GetGame = Dependency(skip_validation=True),
) -> GameResponse:
    try:
        game = await get_game_use_case.execute(game_id)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameResponse.from_game(game)


@post(
    "/games/{game_id:str}/consult",
    responses={
        400: ResponseSpec(data_container=None, description="Not enough battery, already consulted this turn, or no stats available"),
        404: ResponseSpec(data_container=None, description="Game not found"),
    },
)
async def consult(
    game_id: str,
    consult_pokedex: ConsultPokedex = Dependency(skip_validation=True),
) -> GameResponse:
    try:
        game = await consult_pokedex.execute(game_id)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")
    except NotEnoughBattery:
        raise HTTPException(status_code=400, detail="Not enough battery")
    except AlreadyConsultedThisTurn:
        raise HTTPException(status_code=400, detail="Already consulted this turn")
    except NoStatsAvailable:
        raise HTTPException(status_code=400, detail="No stats available")
    except GameOver:
        raise HTTPException(status_code=400, detail="Game is over")

    logger.info(
        "pokedex_consulted",
        game_id=game.id,
        battery_remaining=game.battery,
        turn_number=len(game.attempts) + 1,
        hints=_serialize_hints(game),
    )
    return GameResponse.from_game(game)


@post(
    "/games/{game_id:str}/guess",
    responses={
        400: ResponseSpec(data_container=None, description="Game is over or pokemon not found"),
        404: ResponseSpec(data_container=None, description="Game not found"),
    },
)
async def guess(
    game_id: str,
    data: GuessRequest,
    guess_use_case: Guess = Dependency(skip_validation=True),
) -> GameResponse:
    try:
        game = await guess_use_case.execute(game_id, data.pokemon_name)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")
    except GameOver:
        raise HTTPException(status_code=400, detail="Game is over")
    except PokemonNotFound:
        raise HTTPException(status_code=400, detail="Pokemon not found")

    logger.info(
        "guess_made",
        game_id=game.id,
        guessed_pokemon=data.pokemon_name,
        target_pokemon=game.pokemon.name,
        is_correct=game.is_won,
        attempt_number=len(game.attempts),
        attempts_remaining=game.attempts_remaining,
        battery_remaining=game.battery,
        hints=_serialize_hints(game),
    )
    if game.is_over:
        logger.info(
            "game_over",
            game_id=game.id,
            result="won" if game.is_won else "lost",
            total_attempts=len(game.attempts),
            pokemon_id=game.pokemon.id,
            pokemon_name=game.pokemon.name,
        )
    return GameResponse.from_game(game)


router = Router(
    path="/",
    route_handlers=[create_game, get_game, consult, guess],
    dependencies={
        "start_game": Provide(get_start_game),
        "guess_use_case": Provide(get_guess),
        "get_game_use_case": Provide(get_get_game),
        "consult_pokedex": Provide(get_consult_pokedex),
    },
)
