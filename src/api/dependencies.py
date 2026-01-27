import inspect
from typing import TypeVar, Callable, Awaitable, Union

from api.containers import Container
from services.consult_pokedex import ConsultPokedex
from services.get_game import GetGame
from services.guess import Guess
from services.start_game import StartGame

container = Container()

T = TypeVar("T")

async def _resolve(provider: Callable[..., Union[T, Awaitable[T]]]) -> T:
    result = provider()                     
    if inspect.isawaitable(result):         
        return await result
    return result

async def get_start_game() -> StartGame:
    return await _resolve(container.start_game)


async def get_guess() -> Guess:
    return await _resolve(container.guess)


async def get_get_game() -> GetGame:
    return await _resolve(container.get_game)


async def get_consult_pokedex() -> ConsultPokedex:
    return await _resolve(container.consult_pokedex)
