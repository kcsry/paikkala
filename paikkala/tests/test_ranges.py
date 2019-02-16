from paikkala.utils.ranges import parse_number_set


def test_parse_number_set():
    assert parse_number_set('1-5') == {1, 2, 3, 4, 5}
    assert parse_number_set('1-6,!5') == {1, 2, 3, 4, 6}
