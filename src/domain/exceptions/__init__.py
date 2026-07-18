"""Domain exceptions package."""


class DomainException(Exception):
    """Asosiy domain xatosi."""

    pass


class InvalidScheduleException(DomainException):
    """Noto'g'ri jadval xatosi."""

    pass


class AlreadyCheckedInError(DomainException):
    """Check-in allaqachon yaratilgan."""

    pass


class InvalidEntityError(DomainException):
    """Entity invarianti buzilgan."""

    pass
