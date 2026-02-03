from typing import Any, Protocol

from domain.hint import (
    ComparisonHint,
    Hint,
    PrimaryTypeHint,
    SecondaryTypeHint,
    StatHint,
)
from domain.ports.repositories import PokemonRepository


class HintSerializer(Protocol):
    def serialize(self, hint: Hint) -> dict[str, Any]: ...
    async def deserialize(self, data: dict[str, Any]) -> Hint: ...


class StatHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, StatHint)
        return {"type": "stat", "stat": hint.stat.value, "value": hint.value}

    async def deserialize(self, data: dict[str, Any]) -> StatHint:
        return StatHint.model_validate(data)


class ComparisonHintSerializer:
    def __init__(self, pokemon_repository: PokemonRepository) -> None:
        self._pokemon_repository = pokemon_repository

    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, ComparisonHint)
        return {
            "type": "comparison",
            "pokemon_id": hint.pokemon.id,
            "comparisons": {s.value: c.value for s, c in hint.comparisons.items()},
        }

    async def deserialize(self, data: dict[str, Any]) -> ComparisonHint:
        pokemon = await self._pokemon_repository.get_by_number(data["pokemon_id"])
        data = data.copy()
        data["pokemon"] = pokemon
        return ComparisonHint.model_validate(data)


class PrimaryTypeHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, PrimaryTypeHint)
        return {"type": "primary_type", "primary_type": hint.primary_type}

    async def deserialize(self, data: dict[str, Any]) -> PrimaryTypeHint:
        return PrimaryTypeHint.model_validate(data)


class SecondaryTypeHintSerializer:
    def serialize(self, hint: Hint) -> dict[str, Any]:
        assert isinstance(hint, SecondaryTypeHint)
        return {"type": "secondary_type", "secondary_type": hint.secondary_type}

    async def deserialize(self, data: dict[str, Any]) -> SecondaryTypeHint:
        return SecondaryTypeHint.model_validate(data)


class HintSerializerRegistry:
    def __init__(self, pokemon_repository: PokemonRepository) -> None:
        self._serializers: dict[type[Hint], HintSerializer] = {}
        self._deserializers: dict[str, HintSerializer] = {}
        self._register_all(pokemon_repository)

    def _register_all(self, pokemon_repository: PokemonRepository) -> None:
        self._register(StatHint, "stat", StatHintSerializer())
        self._register(ComparisonHint, "comparison", ComparisonHintSerializer(pokemon_repository))
        self._register(PrimaryTypeHint, "primary_type", PrimaryTypeHintSerializer())
        self._register(SecondaryTypeHint, "secondary_type", SecondaryTypeHintSerializer())

    def _register(self, hint_type: type[Hint], type_name: str, serializer: HintSerializer) -> None:
        self._serializers[hint_type] = serializer
        self._deserializers[type_name] = serializer

    def serialize(self, hint: Hint) -> dict[str, Any]:
        serializer = self._serializers.get(type(hint))
        if serializer is None:
            raise ValueError(f"No serializer registered for {type(hint).__name__}")
        return serializer.serialize(hint)

    async def deserialize(self, data: dict[str, Any]) -> Hint:
        type_name = data.get("type")
        if type_name is None:
            raise ValueError("Missing 'type' field in hint data")

        serializer = self._deserializers.get(type_name)
        if serializer is None:
            raise ValueError(f"No deserializer registered for type '{type_name}'")

        return await serializer.deserialize(data)
