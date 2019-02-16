import pytest


@pytest.mark.django_db
def test_excluded_numbers(lattia_program):
    zone = lattia_program.zones[0]
    tickets = list(lattia_program.reserve(zone=zone, count=7))
    assert [t.number for t in tickets] == [1, 2, 6, 7, 8, 9, 10]


@pytest.mark.django_db
def test_per_program_blocks(lattia_program):
    zone = lattia_program.zones[0]
    lattia_program.blocks.create(
        row=zone.rows.get(),
        excluded_numbers='6-8,!8',
    )
    tickets = list(lattia_program.reserve(zone=zone, count=5))
    assert [t.number for t in tickets] == [1, 2, 8, 9, 10]
