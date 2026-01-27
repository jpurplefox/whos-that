class DomainException(Exception):
    pass


class PokemonNotFound(DomainException):
    pass


class GameNotFound(DomainException):
    pass


class NotEnoughBattery(DomainException):
    pass


class AlreadyConsultedThisTurn(DomainException):
    pass


class NoStatsAvailable(DomainException):
    pass


class GameOver(DomainException):
    pass
