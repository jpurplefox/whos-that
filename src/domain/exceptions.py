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


class HintAlreadyRevealed(DomainException):
    pass


class GameOver(DomainException):
    pass


class HintNotAvailable(DomainException):
    pass


class UserNotFound(DomainException):
    pass


class InvalidToken(DomainException):
    pass
