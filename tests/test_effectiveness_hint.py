import pytest

from domain.hint import EffectivenessHint, Hint
from domain.pokemon import Pokemon
from domain.type_effectiveness import EffectivenessRelation


@pytest.fixture
def bulbasaur() -> Pokemon:
    """Dual-type Grass/Poison Pokemon."""
    return Pokemon(
        id=1,
        name="bulbasaur",
        hp=45,
        attack=49,
        defense=49,
        sp_attack=65,
        sp_defense=65,
        speed=45,
        image_url="https://example.com/bulbasaur.png",
        primary_type="grass",
        secondary_type="poison",
        evolves_from=None,
        evolves_to=[2],
    )


@pytest.fixture
def pikachu() -> Pokemon:
    return Pokemon(
        id=25,
        name="pikachu",
        hp=35,
        attack=55,
        defense=40,
        sp_attack=50,
        sp_defense=50,
        speed=90,
        image_url="https://example.com/pikachu.png",
        primary_type="electric",
        secondary_type=None,
        evolves_from=None,
        evolves_to=[26],
    )


class TestEffectivenessHint:
    def test_create_effectiveness_hint(self, pikachu: Pokemon) -> None:
        """Test creating an effectiveness hint."""
        hint = EffectivenessHint.create(
            pokemon=pikachu,
            relation="weakness",
            element="fire",
            multiplier=2.0,
        )
        
        assert hint.relation == "weakness"
        assert hint.element == "fire"
        assert hint.multiplier == 2.0
        assert hint.hint_type_name == "effectiveness"

    def test_is_already_revealed_same_hint(self) -> None:
        """Test that the same hint is detected as already revealed."""
        hint1 = EffectivenessHint(relation="weakness", element="fire", multiplier=2.0)
        hint2 = EffectivenessHint(relation="weakness", element="fire", multiplier=2.0)
        
        assert hint1.is_already_revealed([hint2])

    def test_is_already_revealed_different_element(self) -> None:
        """Test that hints with different elements are not considered revealed."""
        hint1 = EffectivenessHint(relation="weakness", element="fire", multiplier=2.0)
        hint2 = EffectivenessHint(relation="weakness", element="water", multiplier=2.0)
        
        assert not hint1.is_already_revealed([hint2])

    def test_is_already_revealed_different_relation(self) -> None:
        """Test that hints with different relations are not considered revealed."""
        hint1 = EffectivenessHint(relation="weakness", element="fire", multiplier=2.0)
        hint2 = EffectivenessHint(relation="resistance", element="fire", multiplier=0.5)
        
        assert not hint1.is_already_revealed([hint2])

    def test_unrevealed_effectiveness_all_available(self, pikachu: Pokemon) -> None:
        """Test getting available attributes when none are revealed."""
        available = EffectivenessHint.unrevealed_effectiveness(pikachu, [])
        
        # Pikachu (Electric) should have weaknesses, resistances, but no immunities
        assert len(available) > 0
        
        # Should have ground weakness
        ground_attrs = [a for a in available if a.element == "ground"]
        assert len(ground_attrs) == 1
        assert ground_attrs[0].relation == EffectivenessRelation.WEAKNESS

    def test_unrevealed_effectiveness_filters_revealed(self, pikachu: Pokemon) -> None:
        """Test that revealed attributes are filtered out."""
        revealed_hint = EffectivenessHint(
            relation="weakness", element="ground", multiplier=2.0
        )
        
        available = EffectivenessHint.unrevealed_effectiveness(pikachu, [revealed_hint])
        
        # Ground weakness should not be available
        ground_attrs = [a for a in available if a.element == "ground"]
        assert len(ground_attrs) == 0

    def test_unrevealed_effectiveness_dual_type(self, bulbasaur: Pokemon) -> None:
        """Test available attributes for dual-type Pokemon."""
        available = EffectivenessHint.unrevealed_effectiveness(bulbasaur, [])
        
        # Bulbasaur (Grass/Poison) should have various effectiveness
        assert len(available) > 0
        
        # Check for expected weaknesses
        fire_attrs = [a for a in available if a.element == "fire"]
        assert len(fire_attrs) == 1
        assert fire_attrs[0].relation == EffectivenessRelation.WEAKNESS

    def test_is_available_with_unrevealed_attributes(self, pikachu: Pokemon) -> None:
        """Test that is_available returns True when attributes remain."""
        assert EffectivenessHint.is_available(pikachu, [])

    def test_is_available_after_individual_exhausted(self, pikachu: Pokemon) -> None:
        """Test that is_available returns True when all individual attributes are revealed but completion is not."""
        all_attributes = EffectivenessHint.unrevealed_effectiveness(pikachu, [])
        revealed_hints: list[Hint] = [
            EffectivenessHint(
                relation=attr.relation.value,
                element=attr.element,
                multiplier=attr.multiplier,
            )
            for attr in all_attributes
        ]
        assert EffectivenessHint.is_available(pikachu, revealed_hints) is True

    def test_is_available_returns_false_when_exhausted(self, pikachu: Pokemon) -> None:
        """Test that is_available returns False when all attributes and completion are revealed."""
        all_attributes = EffectivenessHint.unrevealed_effectiveness(pikachu, [])
        revealed_hints: list[Hint] = [
            EffectivenessHint(
                relation=attr.relation.value,
                element=attr.element,
                multiplier=attr.multiplier,
            )
            for attr in all_attributes
        ]
        revealed_hints.append(EffectivenessHint())
        assert EffectivenessHint.is_available(pikachu, revealed_hints) is False

    def test_completion_hint_is_already_revealed(self) -> None:
        """Test that a completion hint detects itself as already revealed."""
        completion = EffectivenessHint()
        assert completion.is_already_revealed([EffectivenessHint()])

    def test_completion_hint_not_confused_with_individual(self) -> None:
        """Test that a completion hint is not confused with individual hints."""
        completion = EffectivenessHint()
        individual = EffectivenessHint(relation="weakness", element="ground", multiplier=2.0)
        assert not completion.is_already_revealed([individual])
        assert not individual.is_already_revealed([completion])

    def test_unrevealed_effectiveness_exhausted(self, pikachu: Pokemon) -> None:
        """Test when all attributes are revealed."""
        # Get all possible attributes
        all_attributes = EffectivenessHint.unrevealed_effectiveness(pikachu, [])
        
        # Create hints for all attributes
        revealed_hints: list[Hint] = [
            EffectivenessHint(
                relation=attr.relation.value,
                element=attr.element,
                multiplier=attr.multiplier,
            )
            for attr in all_attributes
        ]
        
        # Now available should be empty
        available = EffectivenessHint.unrevealed_effectiveness(pikachu, revealed_hints)
        assert len(available) == 0
