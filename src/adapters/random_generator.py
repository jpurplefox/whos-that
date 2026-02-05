import random


class SystemRandomGenerator:
    def randint(self, min_value: int, max_value: int) -> int:
        return random.randint(min_value, max_value)
