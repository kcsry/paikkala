class NoCapacity(RuntimeError):
    pass


class NoRowCapacity(NoCapacity):
    pass


class MaxTicketsReached(NoCapacity):
    pass


class MaxTicketsPerUserReached(NoCapacity):
    pass


class BatchSizeOverflow(NoCapacity):
    pass


class Unreservable(RuntimeError):
    pass


class UserRequired(ValueError):
    pass


class ContactRequired(ValueError):
    pass
