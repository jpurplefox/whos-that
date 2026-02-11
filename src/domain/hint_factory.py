from typing import Protocol

from domain.exceptions import HintAlreadyRevealed
from domain.hint import EffectivenessHint, FullyEvolvedHint, Hint, MovesHint, PrimaryTypeHint, SecondaryTypeHint, StatHint
from domain.pokemon import Pokemon
from domain.ports.random_generator import RandomGenerator
from domain.type_effectiveness import EffectivenessAttribute, TypeEffectiveness


class HintCreator(Protocol):
    def is_available(self, pokemon: Pokemon, hints: list[Hint]) -> bool: ...

    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint: ...


class StatHintCreator:
    def is_available(self, pokemon: Pokemon, hints: list[Hint]) -> bool:
        return len(StatHint.available_stats(hints)) > 0

    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        available = StatHint.available_stats(hints)
        if not available:
            raise HintAlreadyRevealed("All stats already revealed")
        index = random_generator.randint(0, len(available) - 1)
        return StatHint.create(pokemon, available[index])


class PrimaryTypeHintCreator:
    def is_available(self, pokemon: Pokemon, hints: list[Hint]) -> bool:
        return not any(isinstance(h, PrimaryTypeHint) for h in hints)

    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return PrimaryTypeHint.create(pokemon)


class SecondaryTypeHintCreator:
    def is_available(self, pokemon: Pokemon, hints: list[Hint]) -> bool:
        return not any(isinstance(h, SecondaryTypeHint) for h in hints)

    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return SecondaryTypeHint.create(pokemon)


class FullyEvolvedHintCreator:
    def is_available(self, pokemon: Pokemon, hints: list[Hint]) -> bool:
        return not any(isinstance(h, FullyEvolvedHint) for h in hints)

    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return FullyEvolvedHint.create(pokemon)


class EffectivenessHintCreator:
    def __init__(self, type_effectiveness: TypeEffectiveness) -> None:
        self._type_effectiveness = type_effectiveness

    def is_available(self, pokemon: Pokemon, hints: list[Hint]) -> bool:
        if self._unrevealed_effectiveness(pokemon, hints):
            return True
        return not self._is_completion_revealed(hints)

    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        available = self._unrevealed_effectiveness(pokemon, hints)
        if available:
            index = random_generator.randint(0, len(available) - 1)
            selected = available[index]
            return EffectivenessHint.create(
                pokemon,
                relation=selected.relation.value,
                element=selected.element,
                multiplier=selected.multiplier,
            )

        if not self._is_completion_revealed(hints):
            return EffectivenessHint()

        raise HintAlreadyRevealed("All effectiveness attributes already revealed")

    def _unrevealed_effectiveness(
        self, pokemon: Pokemon, hints: list[Hint]
    ) -> list[EffectivenessAttribute]:
        all_attributes = self._type_effectiveness.calculate_effectiveness(
            pokemon.primary_type, pokemon.secondary_type
        )
        revealed = {
            (h.relation, h.element, h.multiplier)
            for h in hints
            if isinstance(h, EffectivenessHint)
        }
        return [
            attr
            for attr in all_attributes
            if (attr.relation.value, attr.element, attr.multiplier) not in revealed
        ]

    @staticmethod
    def _is_completion_revealed(hints: list[Hint]) -> bool:
        return any(
            isinstance(h, EffectivenessHint) and h.element is None
            for h in hints
        )


class MovesHintCreator:
    def is_available(self, pokemon: Pokemon, hints: list[Hint]) -> bool:
        if self._unrevealed_moves(pokemon, hints):
            return True
        return not self._is_completion_revealed(hints)

    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        available = self._unrevealed_moves(pokemon, hints)
        if available:
            index = random_generator.randint(0, len(available) - 1)
            return MovesHint.create(pokemon, available[index])
        if not self._is_completion_revealed(hints):
            return MovesHint()
        raise HintAlreadyRevealed("All moves already revealed")

    def _unrevealed_moves(self, pokemon: Pokemon, hints: list[Hint]) -> list[str]:
        revealed = {h.move for h in hints if isinstance(h, MovesHint) and h.move is not None}
        return [m for m in pokemon.moves if m not in revealed]

    @staticmethod
    def _is_completion_revealed(hints: list[Hint]) -> bool:
        return any(isinstance(h, MovesHint) and h.move is None for h in hints)


class HintCreatorRegistry:
    def __init__(self) -> None:
        self._creators: dict[str, HintCreator] = {}

    @property
    def type_names(self) -> list[str]:
        return list(self._creators.keys())

    def register(self, type_name: str, creator: HintCreator) -> None:
        self._creators[type_name] = creator

    def is_available(self, type_name: str, pokemon: Pokemon, hints: list[Hint]) -> bool:
        creator = self._creators.get(type_name)
        if creator is None:
            raise ValueError(f"No creator registered for type '{type_name}'")
        return creator.is_available(pokemon, hints)

    def create(
        self,
        type_name: str,
        pokemon: Pokemon,
        hints: list[Hint],
        random_generator: RandomGenerator,
    ) -> Hint:
        creator = self._creators.get(type_name)
        if creator is None:
            raise ValueError(f"No creator registered for type '{type_name}'")
        return creator.create(pokemon, hints, random_generator)


def create_hint_registry(type_effectiveness: TypeEffectiveness) -> HintCreatorRegistry:
    registry = HintCreatorRegistry()
    registry.register("stat", StatHintCreator())
    registry.register("primary_type", PrimaryTypeHintCreator())
    registry.register("secondary_type", SecondaryTypeHintCreator())
    registry.register("fully_evolved", FullyEvolvedHintCreator())
    registry.register("effectiveness", EffectivenessHintCreator(type_effectiveness))
    registry.register("moves", MovesHintCreator())
    return registry
