import pytest

from adapters.in_memory_game_repository import InMemoryGameRepository


@pytest.fixture
def game_repository():
    return InMemoryGameRepository()
