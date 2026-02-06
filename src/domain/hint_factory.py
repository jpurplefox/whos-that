from typing import Protocol

from domain.exceptions import HintAlreadyRevealed
from domain.hint import FullyEvolvedHint, Hint, PrimaryTypeHint, SecondaryTypeHint, StatHint
from domain.pokemon import Pokemon
from domain.ports.random_generator import RandomGenerator


class HintCreator(Protocol):
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint: ...


class StatHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        available = StatHint.available_stats(hints)
        if not available:
            raise HintAlreadyRevealed("All stats already revealed")
        index = random_generator.randint(0, len(available) - 1)
        return StatHint.create(pokemon, available[index])


class PrimaryTypeHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return PrimaryTypeHint.create(pokemon)


class SecondaryTypeHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return SecondaryTypeHint.create(pokemon)


class FullyEvolvedHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        return FullyEvolvedHint.create(pokemon)




class EffectivenessHintCreator:
    def create(
        self, pokemon: Pokemon, hints: list[Hint], random_generator: RandomGenerator
    ) -> Hint:
        from domain.hint import EffectivenessHint

        available = EffectivenessHint.unrevealed_effectiveness(pokemon, hints)
        if available:
            index = random_generator.randint(0, len(available) - 1)
            selected = available[index]
            return EffectivenessHint.create(
                pokemon,
                relation=selected.relation.value,
                element=selected.element,
                multiplier=selected.multiplier,
            )

        if EffectivenessHint.is_available(pokemon, hints):
            return EffectivenessHint()

        raise HintAlreadyRevealed("All effectiveness attributes already revealed")

class HintCreatorRegistry:
    def __init__(self) -> None:
        self._creators: dict[str, HintCreator] = {}

    def register(self, type_name: str, creator: HintCreator) -> None:
        self._creators[type_name] = creator

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


def _create_registry() -> HintCreatorRegistry:
    registry = HintCreatorRegistry()
    registry.register("stat", StatHintCreator())
    registry.register("primary_type", PrimaryTypeHintCreator())
    registry.register("secondary_type", SecondaryTypeHintCreator())
    registry.register("fully_evolved", FullyEvolvedHintCreator())
    registry.register("effectiveness", EffectivenessHintCreator())
    return registry


hint_registry = _create_registry()
