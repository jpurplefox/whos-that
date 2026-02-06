from pathlib import Path

import pytest

from domain.pokemon import Pokemon
from domain.type_effectiveness import (
    EffectivenessAttribute,
    EffectivenessRelation,
    TypeEffectiveness,
    load_type_chart,
)

_TYPE_CHART_PATH = Path(__file__).parent.parent / "src" / "data" / "type_chart.json"


@pytest.fixture
def type_effectiveness() -> TypeEffectiveness:
    return TypeEffectiveness(load_type_chart(_TYPE_CHART_PATH))


@pytest.fixture
def gyarados() -> Pokemon:
    """Dual-type Water/Flying Pokemon."""
    return Pokemon(
        id=130,
        name="gyarados",
        hp=95,
        attack=125,
        defense=79,
        sp_attack=60,
        sp_defense=100,
        speed=81,
        image_url="https://example.com/gyarados.png",
        primary_type="water",
        secondary_type="flying",
        evolves_from=129,
        evolves_to=[],
    )


@pytest.fixture
def pikachu() -> Pokemon:
    """Single-type Electric Pokemon."""
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


class TestTypeEffectiveness:
    def test_single_type_weakness(self, type_effectiveness: TypeEffectiveness, pikachu: Pokemon) -> None:
        """Electric type is weak to Ground (2x)."""
        attributes = type_effectiveness.calculate_effectiveness(
            pikachu.primary_type, pikachu.secondary_type
        )

        ground_weakness = [
            attr
            for attr in attributes
            if attr.element == "ground" and attr.relation == EffectivenessRelation.WEAKNESS
        ]

        assert len(ground_weakness) == 1
        assert ground_weakness[0].multiplier == 2.0

    def test_single_type_resistance(self, type_effectiveness: TypeEffectiveness, pikachu: Pokemon) -> None:
        """Electric type resists Electric, Flying, Steel (0.5x)."""
        attributes = type_effectiveness.calculate_effectiveness(
            pikachu.primary_type, pikachu.secondary_type
        )

        resistances = [
            attr.element
            for attr in attributes
            if attr.relation == EffectivenessRelation.RESISTANCE
        ]

        assert "electric" in resistances
        assert "flying" in resistances
        assert "steel" in resistances

    def test_dual_type_stacking_weakness(self, type_effectiveness: TypeEffectiveness, gyarados: Pokemon) -> None:
        """Gyarados (Water/Flying) is 4x weak to Electric (2x * 2x)."""
        attributes = type_effectiveness.calculate_effectiveness(
            gyarados.primary_type, gyarados.secondary_type
        )

        electric_weakness = [
            attr
            for attr in attributes
            if attr.element == "electric"
        ]

        assert len(electric_weakness) == 1
        assert electric_weakness[0].relation == EffectivenessRelation.WEAKNESS
        assert electric_weakness[0].multiplier == 4.0

    def test_dual_type_immunity(self, type_effectiveness: TypeEffectiveness, gyarados: Pokemon) -> None:
        """Gyarados (Water/Flying) is immune to Ground (Flying immunity)."""
        attributes = type_effectiveness.calculate_effectiveness(
            gyarados.primary_type, gyarados.secondary_type
        )

        ground_immunity = [
            attr
            for attr in attributes
            if attr.element == "ground"
        ]

        assert len(ground_immunity) == 1
        assert ground_immunity[0].relation == EffectivenessRelation.IMMUNITY
        assert ground_immunity[0].multiplier == 0.0

    def test_dual_type_resistance(self, type_effectiveness: TypeEffectiveness, gyarados: Pokemon) -> None:
        """Gyarados: Fighting is neutral vs Water but 0.5x vs Flying = 0.5x (resistance)."""
        attributes = type_effectiveness.calculate_effectiveness(
            gyarados.primary_type, gyarados.secondary_type
        )

        fighting_attributes = [
            attr
            for attr in attributes
            if attr.element == "fighting"
        ]

        assert len(fighting_attributes) == 1
        assert fighting_attributes[0].relation == EffectivenessRelation.RESISTANCE
        assert fighting_attributes[0].multiplier == 0.5

    def test_neutral_effectiveness_excluded(self, type_effectiveness: TypeEffectiveness, pikachu: Pokemon) -> None:
        """Normal effectiveness (1.0x) should not be in the results."""
        attributes = type_effectiveness.calculate_effectiveness(
            pikachu.primary_type, pikachu.secondary_type
        )

        for attr in attributes:
            assert attr.multiplier != 1.0

    def test_effectiveness_attribute_equality(self) -> None:
        """Test EffectivenessAttribute equality and hashing."""
        attr1 = EffectivenessAttribute(
            relation=EffectivenessRelation.WEAKNESS,
            element="electric",
            multiplier=2.0,
        )
        attr2 = EffectivenessAttribute(
            relation=EffectivenessRelation.WEAKNESS,
            element="electric",
            multiplier=2.0,
        )
        attr3 = EffectivenessAttribute(
            relation=EffectivenessRelation.WEAKNESS,
            element="fire",
            multiplier=2.0,
        )
        
        assert attr1 == attr2
        assert attr1 != attr3
        assert hash(attr1) == hash(attr2)
        assert hash(attr1) != hash(attr3)
