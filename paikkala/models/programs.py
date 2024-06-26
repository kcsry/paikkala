from __future__ import annotations

import datetime
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Set, Tuple

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import Q, QuerySet
from django.utils.timezone import now

from paikkala.excs import (
    BatchSizeOverflow,
    ContactRequired,
    MaxTicketsPerUserReached,
    MaxTicketsReached,
    NoCapacity,
    Unreservable,
    UserRequired,
)

if TYPE_CHECKING:
    from paikkala.models.rows import Row
    from paikkala.models.tickets import Ticket
    from paikkala.models.zones import Zone


class ProgramQuerySet(models.QuerySet):
    def reservable(self, at: Optional[datetime.datetime] = None) -> 'ProgramQuerySet':
        if not at:
            at = now()
        return self.filter(reservation_start__lte=at, reservation_end__gte=at)

    def valid(self, at: Optional[datetime.datetime] = None) -> 'ProgramQuerySet':
        if not at:
            at = now()
        return self.filter(Q(invalid_after__isnull=True) | Q(invalid_after__gt=at))


class Program(models.Model):
    event_name = models.CharField(
        max_length=64,
        help_text='Used to form a longer name for the program.',
    )
    name = models.CharField(
        max_length=64,
    )
    description = models.TextField(blank=True)
    reservation_start = models.DateTimeField(blank=True, null=True)
    reservation_end = models.DateTimeField(blank=True, null=True)
    invalid_after = models.DateTimeField(
        blank=True,
        null=True,
        help_text='the time after which tickets for this program are considered out-of-date, e.g. for hiding from UI',
    )
    room = models.ForeignKey('paikkala.Room', on_delete=models.PROTECT)
    rows = models.ManyToManyField('paikkala.Row')
    max_tickets = models.IntegerField()
    require_user = models.BooleanField(default=False)
    max_tickets_per_user = models.IntegerField(default=1000)
    max_tickets_per_batch = models.IntegerField(default=50)
    automatic_max_tickets = models.BooleanField(
        default=False,
        help_text='Recompute the maximum tickets field automatically based on row capacity',
    )

    numbered_seats = models.BooleanField(
        default=True,
        help_text='Are seats numbered and should the numbers be shown to the user?',
    )
    require_contact = models.BooleanField(
        default=False,
        help_text='Require contact information (name, email, phone number) from the user?',
    )

    objects = ProgramQuerySet.as_manager()

    def __str__(self) -> str:
        return self.long_name

    def clean(self) -> None:
        if self.automatic_max_tickets and self.id:
            self.max_tickets = self.compute_max_tickets()

    def compute_max_tickets(self) -> int:
        number_map = dict(self.get_rows_and_numbers())
        return sum((len(number_set) for number_set in number_map.values()), 0)

    @property
    def long_name(self) -> str:
        if self.event_name:
            return f'{self.event_name}: {self.name}'
        return f'{self.name}'

    @property
    def zones(self) -> QuerySet:
        from paikkala.models import Zone

        return Zone.objects.filter(rows__in=self.rows.all()).distinct()

    def get_block_map(self, zone: Optional['Zone'] = None) -> Dict[int, Set[int]]:
        """
        Get a dict mapping row IDs to a set of blocked Numbers per row.

        :param zone: Optional zone to filter for.
        :return: Dict of row ID <-> excluded numbers set
        """
        blocks_by_row_id: Dict[int, Set[int]] = defaultdict(set)
        qs = self.blocks.filter(row__zone=zone) if zone else self.blocks.all()
        for block in qs:
            blocks_by_row_id[block.row_id] |= block.get_excluded_set()
        return dict(blocks_by_row_id)

    def get_rows_and_numbers(self, zone: None = None) -> Iterator[Tuple['Row', List[int]]]:
        """
        Iterate over Row objects and Numbers available in them,
        taking into account row blocks and per-program blocks.

        This is the most efficient way of acquiring this information.

        :param zone: Optional zone to filter for.
        :return: Generator over (row, numbers) pairs.
        """
        row_qs = (self.rows.filter(zone=zone) if zone else self.rows.all()).prefetch_related('zone')
        block_map = self.get_block_map(zone=zone)
        for row in row_qs:
            yield (row, row.get_numbers(additional_excluded_set=block_map.get(row.id, set())))

    def is_reservable(self) -> bool:
        if not (self.reservation_start and self.reservation_end):
            return False
        return self.reservation_start <= now() <= self.reservation_end

    def check_reservable(self) -> None:
        if not self.is_reservable():
            raise Unreservable(f'{self} is not reservable at this time')
        if self.remaining_tickets <= 0:
            raise MaxTicketsReached(f'{self} has no remaining tickets.')

    @property
    def remaining_tickets(self) -> int:
        return self.max_tickets - self.tickets.count()

    def reserve(  # noqa: C901
        self,
        *,
        zone: Optional['Zone'],
        count: int,
        user: Optional[AbstractBaseUser] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        allow_scatter: bool = False,
        attempt_sequential: bool = True,
    ) -> Iterator['Ticket']:
        """
        Reserve `count` tickets from the zone `zone`.

        Unless `allow_scatter` is set, the tickets will all be allocated
        from a single Row.  If this is not possible, `NoCapacity` will be raised.

        This method is a generator, so please be sure to fully iterate it
        (i.e. `list(p.reserve())`).  Also, it'd be prudent to run it within a transaction.

        :param zone: The zone to use, or None for any zone available
        :param count:
        :param user:
        :param allow_scatter: Whether to allow allocating tickets from scattered rows. \
                              Overrides `attempt_sequential` to False.
        :param attempt_sequential: Attempt allocation of sequential seats from each row.
        :return:
        """

        # Trivial sanity checks
        if user and user.is_anonymous:
            user = None

        if not user and self.require_user:
            raise UserRequired(f'{self} does not allow anonymous ticketing')

        if self.require_contact and not (name and email and phone):
            raise ContactRequired(f'{self} requires contact information for tickets')

        if count <= 0:  # pragma: no cover
            raise ValueError('Gotta reserve at least one ticket')

        if count > self.max_tickets_per_batch:
            raise BatchSizeOverflow(
                f'Can only reserve {self.max_tickets_per_batch} tickets per batch for {self}, {count} attempted'
            )
        self.check_reservable()

        # User and program quota checks
        if allow_scatter:
            attempt_sequential = False

        total_reserved = sum(z.get_reservation_status(self).total_reserved for z in self.zones)
        if total_reserved + count > self.max_tickets:
            raise MaxTicketsReached(
                f'Reserving {count} more tickets would overdraw {self}\'s ticket limit {self.max_tickets}'
            )

        if user and self.tickets.filter(user=user).count() + count > self.max_tickets_per_user:
            raise MaxTicketsPerUserReached(
                f'{user} reserving {count} more tickets would overdraw '
                f'{self}\'s per-user ticket limit {self.max_tickets_per_user}'
            )

        def _reserve_inner(count: int, zone: 'Zone', allow_partial: bool) -> Iterator['Ticket']:
            reservation_status = zone.get_reservation_status(self)
            new_reservations: list[tuple[Row, int]] = []
            reserve_count = count  # Count remaining to reserve
            for row, row_status in sorted(reservation_status.items(), key=lambda pair: pair[1].remaining):
                # Add a reservation if:
                # 1. we can get all requested seats in a single row; or
                # 2. scatter is allowed (in which case get as many as we can); or
                # 3. the seats are not numbered (in which case also get as many as we can)
                if row_status.remaining >= reserve_count or allow_scatter or not self.numbered_seats:
                    row_count = min(reserve_count, row_status.remaining)
                    new_reservations.append((row, row_count))
                    reserve_count -= row_count
                if reserve_count <= 0:
                    break

            if reserve_count > 0 and not allow_partial:
                if allow_scatter:
                    raise NoCapacity(f'Could not allocate {reserve_count} of {count} requested tickets in zone {zone}')
                raise NoCapacity(
                    f'Could not allocate {reserve_count} of {count} requested tickets in zone {zone} (try scatter?)'
                )

            for row, row_count in new_reservations:
                yield from row.reserve(
                    program=self,
                    count=row_count,
                    user=user,
                    name=name,
                    email=email,
                    phone=phone,
                    attempt_sequential=attempt_sequential and not allow_scatter,
                    excluded_numbers=reservation_status[row].blocked_set,
                )

        # Single zone: trivial case, scatter is handled in _reserve_inner
        if zone is not None:
            yield from _reserve_inner(count, zone, False)

        # Multiple zones, no scatter: loop through zones, accept the first one that gave us the full ticket amount
        elif not allow_scatter:
            tickets = None
            for try_zone in self.zones.all():
                try:
                    tickets = list(_reserve_inner(count, try_zone, False))
                    break
                except NoCapacity:
                    continue
            if not tickets:
                raise NoCapacity(f'Unable to allocate {count} tickets from any single zone (no scatter)')
            yield from tickets

        # Multiple zones with scatter: loop through zones, attempting to get the full ticket amount in total
        else:
            reserved: list[Ticket] = []
            for try_zone in self.zones.all():
                chunk = list(_reserve_inner(count - len(reserved), try_zone, True))
                reserved += chunk
                if len(reserved) >= count:
                    assert len(reserved) == count
                    break
            if len(reserved) < count:
                raise NoCapacity('Unable to allocate {count} tickets total from any zone with scatter')
            yield from reserved
