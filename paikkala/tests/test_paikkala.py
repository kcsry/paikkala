import pytest

from paikkala.excs import NoCapacity, MaxTicketsReached, Unreservable
from paikkala.models import Program


@pytest.mark.django_db
def test_is_reservable(jussi_program):
    assert jussi_program.is_reservable()
    assert jussi_program in Program.objects.reservable()
    jussi_program.reservation_end = None
    assert not jussi_program.is_reservable()
    with pytest.raises(Unreservable):
        list(jussi_program.reserve(zone=jussi_program.zones.first(), count=1))


@pytest.mark.django_db
def test_reserve_non_scatter(jussi_program):
    zone = jussi_program.zones.get(name='Aitio 1 (vasen)')
    assert zone.capacity == 9
    with pytest.raises(NoCapacity):
        list(jussi_program.reserve(zone=zone, count=10))
    tickets = list(jussi_program.reserve(zone=zone, count=5))
    row = tickets[0].row
    rstat = zone.get_reservation_status(program=jussi_program)
    assert rstat[row]['reserved'] == 5


@pytest.mark.django_db
def test_reserve_limit(jussi_program):
    zone = jussi_program.zones.get(name='Permanto')
    with pytest.raises(MaxTicketsReached):
        list(jussi_program.reserve(zone=zone, count=jussi_program.max_tickets + 10))


@pytest.mark.django_db
def test_reserve_scatter(jussi_program):
    jussi_program.max_tickets = 1000
    zone = jussi_program.zones.get(name='Permanto')
    assert zone.capacity == 650
    n_to_reserve = 494
    with pytest.raises(NoCapacity):
        list(jussi_program.reserve(zone=zone, count=n_to_reserve))
    tickets = list(jussi_program.reserve(zone=zone, count=n_to_reserve, allow_scatter=True))
    assert len(tickets) == n_to_reserve
    rstat = zone.get_reservation_status(program=jussi_program)
    assert sum(r['reserved'] for r in rstat.values()) == n_to_reserve  # Reservations line up
    assert sum(r['remaining'] for r in rstat.values()) == zone.capacity - n_to_reserve  # Free slots line up
    assert any(r['reserved'] and r['capacity'] for r in rstat.values())  # Check that we have semi-reserved rows
