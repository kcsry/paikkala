class NoCapacity(RuntimeError):
    pass


class NoRowCapacity(NoCapacity):
    pass


class MaxTicketsReached(NoCapacity):
    pass


class Unreservable(RuntimeError):
    pass
