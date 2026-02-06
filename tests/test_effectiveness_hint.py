import pytest

from domain.hint import EffectivenessHint, Hint
from domain.hint_factory import EffectivenessHintCreator
from domain.pokemon import Pokemon
from domain.type_effectiveness import EffectivenessRelation, TypeEffectiveness


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

    def test_unrevealed_effectiveness_all_available(
        self, pikachu: Pokemon, type_effectiveness: TypeEffectiveness
    ) -> None:
        """Test getting available attributes when none are revealed."""
        creator = EffectivenessHintCreator(type_effectiveness)
        available = creator._unrevealed_effectiveness(pikachu, [])

        assert len(available) > 0

        ground_attrs = [a for a in available if a.element == "ground"]
        assert len(ground_attrs) == 1
        assert ground_attrs[0].relation == EffectivenessRelation.WEAKNESS

    def test_unrevealed_effectiveness_filters_revealed(
        self, pikachu: Pokemon, type_effectiveness: TypeEffectiveness
    ) -> None:
        """Test that revealed attributes are filtered out."""
        revealed_hint = EffectivenessHint(
            relation="weakness", element="ground", multiplier=2.0
        )

        creator = EffectivenessHintCreator(type_effectiveness)
        available = creator._unrevealed_effectiveness(pikachu, [revealed_hint])

        ground_attrs = [a for a in available if a.element == "ground"]
        assert len(ground_attrs) == 0

    def test_unrevealed_effectiveness_dual_type(
        self, bulbasaur: Pokemon, type_effectiveness: TypeEffectiveness
    ) -> None:
        """Test available attributes for dual-type Pokemon."""
        creator = EffectivenessHintCreator(type_effectiveness)
        available = creator._unrevealed_effectiveness(bulbasaur, [])

        assert len(available) > 0

        fire_attrs = [a for a in available if a.element == "fire"]
        assert len(fire_attrs) == 1
        assert fire_attrs[0].relation == EffectivenessRelation.WEAKNESS

    def test_is_available_with_unrevealed_attributes(
        self, pikachu: Pokemon, type_effectiveness: TypeEffectiveness
    ) -> None:
        """Test that is_available returns True when attributes remain."""
        creator = EffectivenessHintCreator(type_effectiveness)
        assert creator.is_available(pikachu, [])

    def test_is_available_after_individual_exhausted(
        self, pikachu: Pokemon, type_effectiveness: TypeEffectiveness
    ) -> None:
        """Test that is_available returns True when all individual attributes are revealed but completion is not."""
        creator = EffectivenessHintCreator(type_effectiveness)
        all_attributes = creator._unrevealed_effectiveness(pikachu, [])
        revealed_hints: list[Hint] = [
            EffectivenessHint(
                relation=attr.relation.value,
                element=attr.element,
                multiplier=attr.multiplier,
            )
            for attr in all_attributes
        ]
        assert creator.is_available(pikachu, revealed_hints) is True

    def test_is_available_returns_false_when_exhausted(
        self, pikachu: Pokemon, type_effectiveness: TypeEffectiveness
    ) -> None:
        """Test that is_available returns False when all attributes and completion are revealed."""
        creator = EffectivenessHintCreator(type_effectiveness)
        all_attributes = creator._unrevealed_effectiveness(pikachu, [])
        revealed_hints: list[Hint] = [
            EffectivenessHint(
                relation=attr.relation.value,
                element=attr.element,
                multiplier=attr.multiplier,
            )
            for attr in all_attributes
        ]
        revealed_hints.append(EffectivenessHint())
        assert creator.is_available(pikachu, revealed_hints) is False

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

    def test_unrevealed_effectiveness_exhausted(
        self, pikachu: Pokemon, type_effectiveness: TypeEffectiveness
    ) -> None:
        """Test when all attributes are revealed."""
        creator = EffectivenessHintCreator(type_effectiveness)
        all_attributes = creator._unrevealed_effectiveness(pikachu, [])

        revealed_hints: list[Hint] = [
            EffectivenessHint(
                relation=attr.relation.value,
                element=attr.element,
                multiplier=attr.multiplier,
            )
            for attr in all_attributes
        ]

        available = creator._unrevealed_effectiveness(pikachu, revealed_hints)
        assert len(available) == 0
