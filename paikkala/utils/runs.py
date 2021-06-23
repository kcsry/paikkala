from typing import Callable, Iterable, List, TypeVar


def following_integer(current_run: List[int], new_value: int) -> bool:
    return new_value == current_run[-1] + 1


T = TypeVar('T')


def find_runs(iterable: Iterable[T], predicate: Callable[[List[T], T], bool]) -> List[List[T]]:
    """
    Find "runs" in the iterable by grouping them with the given predicate.

    :param iterable: Iterable of things.
    :param predicate: Predicate function receiving the current run (a list of things from `iterable`),
                      and a new value we're processing from `iterable`.  Should return true if the new
                      value belongs in the run, and false otherwise.
    :return: The input, grouped into runs.
    """
    runs: List[List[T]] = []
    run = None
    for value in iterable:
        if run is not None and predicate(run, value):
            run.append(value)
        else:
            run = [value]
            runs.append(run)
    return runs
