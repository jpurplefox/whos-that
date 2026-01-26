import pytest

from repositories.in_memory_game_repository import InMemoryGameRepository


@pytest.fixture
def game_repository():
    return InMemoryGameRepository()
