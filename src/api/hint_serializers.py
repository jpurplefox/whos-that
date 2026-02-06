from typing import Any, Protocol

from domain.hint import (
    ComparisonHint,
    FullyEvolvedHint,
    Hint,
    PrimaryTypeHint,
    SecondaryTypeHint,
    StatHint,
    EffectivenessHint,
)


class HintSerializer(Protocol):
    def serialize(self, hint: Hint) -> dict[str, Any]: ...


class StatHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, StatHint)
        return {"type": "stat", "stat": hint.stat.value, "value": hint.value}


class ComparisonHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, ComparisonHint)
        return {
            "type": "comparison",
            "pokemon": hint.pokemon.name,
            "comparisons": {s.value: c.value for s, c in hint.comparisons.items()},
        }


class PrimaryTypeHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, PrimaryTypeHint)
        return {"type": "primary_type", "primary_type": hint.primary_type}


class SecondaryTypeHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, SecondaryTypeHint)
        return {"type": "secondary_type", "secondary_type": hint.secondary_type}


class FullyEvolvedHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, FullyEvolvedHint)
        return {"type": "fully_evolved", "is_fully_evolved": hint.is_fully_evolved}



class EffectivenessHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, EffectivenessHint)
        return {
            "type": "effectiveness",
            "relation": hint.relation,
            "element": hint.element,
            "multiplier": hint.multiplier,
        }


class HintSerializerRegistry:
    def __init__(self) -> None:
        self._serializers: dict[type[Hint], HintSerializer] = {}

    def register(self, hint_type: type[Hint], serializer: HintSerializer) -> None:
        self._serializers[hint_type] = serializer

    def serialize(self, hint: Hint) -> dict[str, Any]:
        serializer = self._serializers.get(type(hint))
        if serializer is None:
            raise ValueError(f"No serializer registered for {type(hint).__name__}")
        return serializer.serialize(hint)


def _create_registry() -> HintSerializerRegistry:
    registry = HintSerializerRegistry()
    registry.register(StatHint, StatHintSerializer())
    registry.register(ComparisonHint, ComparisonHintSerializer())
    registry.register(PrimaryTypeHint, PrimaryTypeHintSerializer())
    registry.register(SecondaryTypeHint, SecondaryTypeHintSerializer())
    registry.register(FullyEvolvedHint, FullyEvolvedHintSerializer())
    registry.register(EffectivenessHint, EffectivenessHintSerializer())
    return registry


hint_registry = _create_registry()
