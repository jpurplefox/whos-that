class DomainException(Exception):
    pass


class NoAttemptsRemaining(DomainException):
    pass


class PokemonNotFound(DomainException):
    pass


class GameNotFound(DomainException):
    pass
