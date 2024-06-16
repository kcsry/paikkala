from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser

from paikkala.excs import (
    BatchSizeOverflow,
    MaxTicketsPerUserReached,
    MaxTicketsReached,
    NoCapacity,
    Unreservable,
    UserRequired,
)
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
def test_reserve_non_scatter_single_zone(jussi_program):
    zone = jussi_program.zones.get(name='Aitio 1 (vasen)')
    assert zone.capacity == 9
    with pytest.raises(NoCapacity):
        list(jussi_program.reserve(zone=zone, count=10))
    tickets = list(jussi_program.reserve(zone=zone, count=5))
    row = tickets[0].row
    rstat = zone.get_reservation_status(program=jussi_program)
    assert rstat[row].reserved == 5


@pytest.mark.django_db
def test_reserve_non_scatter_multi_zone(jussi_program):
    jussi_program.max_tickets = 1_000
    max_zone_capacity = max(z.get_reservation_status(jussi_program).total_capacity for z in jussi_program.zones)
    n_to_reserve = 21
    with pytest.raises(NoCapacity, match=r'from any single zone \(no scatter\)'):
        list(jussi_program.reserve(zone=None, count=max_zone_capacity + 1, allow_scatter=False))
    tickets = list(jussi_program.reserve(zone=None, count=n_to_reserve, allow_scatter=False))
    assert len(tickets) == n_to_reserve
    assert all(t.zone == tickets[0].zone for t in tickets)


@pytest.mark.django_db
def test_reserve_limit(jussi_program):
    zone = jussi_program.zones.get(name='Permanto')
    with pytest.raises(MaxTicketsReached):
        list(jussi_program.reserve(zone=zone, count=jussi_program.max_tickets + 10))


@pytest.mark.django_db
def test_reserve_scatter_single_zone(jussi_program):
    jussi_program.max_tickets = 1_000
    zone = jussi_program.zones.get(name='Permanto')
    assert zone.capacity == 650
    n_to_reserve = 494
    with pytest.raises(NoCapacity):
        list(jussi_program.reserve(zone=zone, count=zone.capacity + 1, allow_scatter=True))
    tickets = list(jussi_program.reserve(zone=zone, count=n_to_reserve, allow_scatter=True))
    assert len(tickets) == n_to_reserve
    rstat = zone.get_reservation_status(program=jussi_program)
    assert sum(r.reserved for r in rstat.values()) == n_to_reserve  # Reservations line up
    assert sum(r.remaining for r in rstat.values()) == zone.capacity - n_to_reserve  # Free slots line up
    assert any(r.reserved and r.capacity for r in rstat.values())  # Check that we have semi-reserved rows


@pytest.mark.django_db
def test_reserve_scatter_multi_zone(scatter_program):
    scatter_program.max_tickets = 1_000_000
    assert scatter_program.is_reservable()

    rstat_before = {z: z.get_reservation_status(scatter_program) for z in scatter_program.zones}
    total_reserved_before = sum(rs.total_reserved for rs in rstat_before.values())

    n_to_reserve = sum(z.rows.count() for z in scatter_program.zones)
    tickets = list(scatter_program.reserve(zone=None, count=n_to_reserve, allow_scatter=True))

    rstat_after = {z: z.get_reservation_status(scatter_program) for z in scatter_program.zones}
    total_reserved_after = sum(rs.total_reserved for rs in rstat_after.values())

    assert len(tickets) == n_to_reserve
    assert total_reserved_after == total_reserved_before + n_to_reserve


@pytest.mark.django_db
def test_reserve_scatter_multi_zone_fail(scatter_program):
    with pytest.raises(NoCapacity):
        list(scatter_program.reserve(zone=None, count=1_000, allow_scatter=True))


@pytest.mark.django_db
def test_reserve_user_required(jussi_program):
    jussi_program.require_user = True
    jussi_program.save()
    anon = AnonymousUser()
    zone = jussi_program.zones.get(name='Permanto')

    with pytest.raises(UserRequired):
        list(jussi_program.reserve(zone=zone, count=1, user=anon))

    with pytest.raises(UserRequired):
        list(jussi_program.reserve(zone=zone, count=1, user=None))


@pytest.mark.django_db
def test_reserve_user_limits(jussi_program, random_user):
    jussi_program.require_user = True
    jussi_program.max_tickets_per_user = 2
    jussi_program.save()
    zone = jussi_program.zones.get(name='Permanto')

    assert len(list(jussi_program.reserve(zone=zone, count=2, user=random_user))) == 2

    with pytest.raises(MaxTicketsPerUserReached):
        list(jussi_program.reserve(zone=zone, count=1, user=random_user))


@pytest.mark.django_db
def test_reserve_batch_limits(jussi_program, random_user):
    jussi_program.max_tickets_per_batch = 5
    jussi_program.save()
    zone = jussi_program.zones.get(name='Permanto')

    with pytest.raises(BatchSizeOverflow):
        list(jussi_program.reserve(zone=zone, count=7, user=random_user))


@pytest.mark.django_db
def test_automatic_max_tickets(jussi_program):
    jussi_program.automatic_max_tickets = True
    jussi_program.clean()  # As called by admin, etc.
    jussi_program.save()
    assert jussi_program.max_tickets == sum(jussi_program.rows.values_list('capacity', flat=True))


@pytest.mark.django_db
@pytest.mark.parametrize('attempt_sequential', (False, True))
def test_attempt_sequential(lattia_program, attempt_sequential):
    zone = lattia_program.zones[0]
    tickets = list(lattia_program.reserve(zone=zone, count=3, attempt_sequential=attempt_sequential))
    assert [t.number for t in tickets] == ([1, 2, 6] if not attempt_sequential else [6, 7, 8])
