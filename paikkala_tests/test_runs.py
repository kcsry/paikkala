from paikkala.utils.runs import find_runs, following_integer


def test_runs():
    data = [1, 2, 6, 7, 8, 9, 11, 12, 14, 15, 16]
    assert find_runs(data, following_integer) == [
        [1, 2],
        [6, 7, 8, 9],
        [11, 12],
        [14, 15, 16],
    ]
