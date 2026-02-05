from domain.stat import Stat
from domain.ports.random_generator import RandomGenerator


class RandomStatSelector:
    def __init__(self, random_generator: RandomGenerator):
        self.random_generator = random_generator

    def select(self) -> Stat:
        stats = list(Stat)
        index = self.random_generator.randint(0, len(stats) - 1)
        return stats[index]
