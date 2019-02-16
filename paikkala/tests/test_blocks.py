import pytest

from paikkala.excs import NoCapacity, MaxTicketsReached
from paikkala.models import Program


@pytest.mark.django_db
def test_excluded_numbers(lattia_program):
    zone = lattia_program.zones[0]
    tickets = list(lattia_program.reserve(zone=zone, count=7))
    assert [t.number for t in tickets] == [1, 2, 6, 7, 8, 9, 10]


@pytest.mark.django_db
def test_per_program_blocks(lattia_program):
    lattia_program.automatic_max_tickets = True
    lattia_program.clean()
    lattia_program.save()
    assert lattia_program.max_tickets == 7

    assert isinstance(lattia_program, Program)
    zone = lattia_program.zones[0]
    lattia_program.blocks.create(
        row=zone.rows.get(),
        excluded_numbers='6-8,!8',
    )
    lattia_program.clean()
    lattia_program.save()
    assert lattia_program.max_tickets == 5

    tickets = list(lattia_program.reserve(zone=zone, count=5))
    assert [t.number for t in tickets] == [1, 2, 8, 9, 10]

    with pytest.raises(MaxTicketsReached):
        list(lattia_program.reserve(zone=zone, count=5))

    with pytest.raises(NoCapacity):
        lattia_program.max_tickets = 100  # avert MaxTicketsReached
        list(lattia_program.reserve(zone=zone, count=5))
