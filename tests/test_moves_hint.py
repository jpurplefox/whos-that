import pytest

from domain.exceptions import HintAlreadyRevealed
from domain.hint import Hint, MovesHint
from domain.hint_factory import MovesHintCreator
from domain.pokemon import Pokemon


class FakeRandomGenerator:
    def __init__(self, value: int = 0):
        self.value = value

    def randint(self, min_value: int, max_value: int) -> int:
        return self.value


class TestMovesHint:
    def test_create_moves_hint(self, pikachu: Pokemon) -> None:
        hint = MovesHint.create(pikachu, "thunderbolt")

        assert hint.move == "thunderbolt"
        assert hint.hint_type_name == "moves"

    def test_is_already_revealed_same_move(self) -> None:
        hint1 = MovesHint(move="thunderbolt")
        hint2 = MovesHint(move="thunderbolt")

        assert hint1.is_already_revealed([hint2])

    def test_is_already_revealed_different_move(self) -> None:
        hint1 = MovesHint(move="thunderbolt")
        hint2 = MovesHint(move="quick-attack")

        assert not hint1.is_already_revealed([hint2])

    def test_unrevealed_moves_all_available(self, pikachu: Pokemon) -> None:
        creator = MovesHintCreator()
        available = creator._unrevealed_moves(pikachu, [])

        assert available == pikachu.moves

    def test_unrevealed_moves_filters_revealed(self, pikachu: Pokemon) -> None:
        revealed_hint = MovesHint(move="thunder-shock")

        creator = MovesHintCreator()
        available = creator._unrevealed_moves(pikachu, [revealed_hint])

        assert "thunder-shock" not in available
        assert len(available) == len(pikachu.moves) - 1

    def test_is_available_with_unrevealed_moves(self, pikachu: Pokemon) -> None:
        creator = MovesHintCreator()
        assert creator.is_available(pikachu, [])

    def test_is_available_after_individual_exhausted(self, pikachu: Pokemon) -> None:
        """is_available returns True when all individual moves are revealed but completion is not."""
        revealed_hints: list[Hint] = [
            MovesHint(move=move) for move in pikachu.moves
        ]
        creator = MovesHintCreator()
        assert creator.is_available(pikachu, revealed_hints) is True

    def test_is_available_returns_false_when_exhausted(self, pikachu: Pokemon) -> None:
        """is_available returns False when all moves and completion are revealed."""
        revealed_hints: list[Hint] = [
            MovesHint(move=move) for move in pikachu.moves
        ]
        revealed_hints.append(MovesHint())
        creator = MovesHintCreator()
        assert creator.is_available(pikachu, revealed_hints) is False

    def test_completion_hint_is_already_revealed(self) -> None:
        completion = MovesHint()
        assert completion.is_already_revealed([MovesHint()])

    def test_completion_hint_not_confused_with_individual(self) -> None:
        completion = MovesHint()
        individual = MovesHint(move="thunderbolt")
        assert not completion.is_already_revealed([individual])
        assert not individual.is_already_revealed([completion])

    def test_unrevealed_moves_exhausted(self, pikachu: Pokemon) -> None:
        revealed_hints: list[Hint] = [
            MovesHint(move=move) for move in pikachu.moves
        ]
        creator = MovesHintCreator()
        available = creator._unrevealed_moves(pikachu, revealed_hints)
        assert len(available) == 0

    def test_create_returns_random_unrevealed_move(self, pikachu: Pokemon) -> None:
        creator = MovesHintCreator()
        random_gen = FakeRandomGenerator(value=2)
        hint = creator.create(pikachu, [], random_gen)

        assert isinstance(hint, MovesHint)
        assert hint.move == pikachu.moves[2]

    def test_create_returns_completion_when_all_moves_revealed(
        self, pikachu: Pokemon
    ) -> None:
        revealed_hints: list[Hint] = [
            MovesHint(move=move) for move in pikachu.moves
        ]
        creator = MovesHintCreator()
        random_gen = FakeRandomGenerator()
        hint = creator.create(pikachu, revealed_hints, random_gen)

        assert isinstance(hint, MovesHint)
        assert hint.move is None

    def test_create_raises_when_fully_exhausted(self, pikachu: Pokemon) -> None:
        revealed_hints: list[Hint] = [
            MovesHint(move=move) for move in pikachu.moves
        ]
        revealed_hints.append(MovesHint())
        creator = MovesHintCreator()
        random_gen = FakeRandomGenerator()

        with pytest.raises(HintAlreadyRevealed):
            creator.create(pikachu, revealed_hints, random_gen)

    def test_pokemon_with_no_moves(self) -> None:
        pokemon = Pokemon(
            id=999,
            name="no-moves",
            hp=50,
            attack=50,
            defense=50,
            sp_attack=50,
            sp_defense=50,
            speed=50,
            image_url="https://example.com/no-moves.png",
            primary_type="normal",
            moves=[],
        )
        creator = MovesHintCreator()

        # No individual moves available, but completion hint is available
        assert creator.is_available(pokemon, [])

        random_gen = FakeRandomGenerator()
        hint = creator.create(pokemon, [], random_gen)
        assert isinstance(hint, MovesHint)
        assert hint.move is None
