from litestar import Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.openapi.datastructures import ResponseSpec
from litestar.params import Dependency

from api.dependencies import get_consult_pokedex, get_get_game, get_guess, get_optional_user, get_pokemon_repository, get_start_game
from api.schemas import ConsultRequest, CreateGameRequest, DifficultyRequest, GameResponse, GuessRequest, HintTypeRequest, PokemonResponse
from domain.difficulty import DifficultyLevel
from domain.ports.repositories import PokemonRepository
from domain.exceptions import (
    AlreadyConsultedThisTurn,
    GameAccessDenied,
    GameNotFound,
    GameOver,
    HintAlreadyRevealed,
    HintNotAvailable,
    NotEnoughBattery,
    PokemonNotFound,
)
from domain.game import Game
from domain.hint import Hint
from domain.user import User
from api.hint_serializers import hint_registry
from structlog_config import get_logger
from services.consult_pokedex import ConsultPokedex, HintType
from services.get_game import GetGame
from services.guess import Guess
from services.start_game import StartGame

logger = get_logger()


def _serialize_hint(hint: Hint) -> dict[str, object]:
    return hint_registry.serialize(hint)


def _serialize_hints(game: Game) -> list[dict[str, object]]:
    return [_serialize_hint(h) for h in game.hints]


def _convert_difficulty(difficulty: DifficultyRequest) -> DifficultyLevel:
    match difficulty:
        case DifficultyRequest.EASY:
            return DifficultyLevel.EASY
        case DifficultyRequest.MEDIUM:
            return DifficultyLevel.MEDIUM
        case DifficultyRequest.HARD:
            return DifficultyLevel.HARD


@post("/games")
async def create_game(
    data: CreateGameRequest,
    start_game: StartGame = Dependency(skip_validation=True),
    optional_user: User | None = Dependency(skip_validation=True),
) -> GameResponse:
    user_id = optional_user.id if optional_user else None

    difficulty = _convert_difficulty(data.difficulty)
    game = await start_game.execute(difficulty, user_id=user_id)
    logger.info(
        "game_started",
        game_id=game.id,
        pokemon_id=game.pokemon.id,
        pokemon_name=game.pokemon.name,
        difficulty=data.difficulty.value,
        user_id=user_id,
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


def _convert_hint_type(hint_type: HintTypeRequest) -> HintType:
    match hint_type:
        case HintTypeRequest.STAT:
            return HintType.STAT
        case HintTypeRequest.PRIMARY_TYPE:
            return HintType.PRIMARY_TYPE
        case HintTypeRequest.SECONDARY_TYPE:
            return HintType.SECONDARY_TYPE
        case HintTypeRequest.FULLY_EVOLVED:
            return HintType.FULLY_EVOLVED


@post(
    "/games/{game_id:str}/consult",
    responses={
        400: ResponseSpec(data_container=None, description="Not enough battery, already consulted this turn, or hint already revealed"),
        404: ResponseSpec(data_container=None, description="Game not found"),
    },
)
async def consult(
    game_id: str,
    data: ConsultRequest,
    consult_pokedex: ConsultPokedex = Dependency(skip_validation=True),
) -> GameResponse:
    hint_type = _convert_hint_type(data.hint_type)
    try:
        game = await consult_pokedex.execute(game_id, hint_type)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")
    except NotEnoughBattery:
        raise HTTPException(status_code=400, detail="Not enough battery")
    except AlreadyConsultedThisTurn:
        raise HTTPException(status_code=400, detail="Already consulted this turn")
    except HintAlreadyRevealed:
        raise HTTPException(status_code=400, detail="Hint already revealed")
    except HintNotAvailable:
        raise HTTPException(status_code=400, detail="Hint not available")
    except GameOver:
        raise HTTPException(status_code=400, detail="Game is over")

    logger.info(
        "pokedex_consulted",
        game_id=game.id,
        hint_type=data.hint_type.value,
        battery_remaining=game.battery,
        turn_number=len(game.attempts) + 1,
        hints=_serialize_hints(game),
    )
    return GameResponse.from_game(game)


@post(
    "/games/{game_id:str}/guess",
    responses={
        400: ResponseSpec(data_container=None, description="Game is over or pokemon not found"),
        403: ResponseSpec(data_container=None, description="Access denied"),
        404: ResponseSpec(data_container=None, description="Game not found"),
    },
)
async def guess(
    game_id: str,
    data: GuessRequest,
    guess_use_case: Guess = Dependency(skip_validation=True),
    optional_user: User | None = Dependency(skip_validation=True),
) -> GameResponse:
    user_id = optional_user.id if optional_user else None
    try:
        game = await guess_use_case.execute(game_id, data.pokemon_name, user_id)
    except GameNotFound:
        raise HTTPException(status_code=404, detail="Game not found")
    except GameAccessDenied:
        raise HTTPException(status_code=403, detail="Access denied")
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


@get("/pokemon")
async def list_pokemon(
    pokemon_repository: PokemonRepository = Dependency(skip_validation=True),
) -> list[PokemonResponse]:
    pokemon_list = await pokemon_repository.get_all()
    return [PokemonResponse.from_pokemon(p) for p in pokemon_list]


router = Router(
    path="/",
    route_handlers=[list_pokemon, create_game, get_game, consult, guess],
    dependencies={
        "start_game": Provide(get_start_game),
        "guess_use_case": Provide(get_guess),
        "get_game_use_case": Provide(get_get_game),
        "consult_pokedex": Provide(get_consult_pokedex),
        "pokemon_repository": Provide(get_pokemon_repository),
        "optional_user": Provide(get_optional_user),
    },
)
