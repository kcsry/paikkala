from collections import defaultdict

from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from paikkala.excs import (
    BatchSizeOverflow, ContactRequired, MaxTicketsPerUserReached, MaxTicketsReached, NoCapacity, NoRowCapacity,
    Unreservable, UserRequired
)


class ProgramQuerySet(models.QuerySet):
    def reservable(self, at=None):
        if not at:
            at = now()
        return self.filter(reservation_start__lte=at, reservation_end__gte=at)

    def valid(self, at=None):
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

    def __str__(self):
        return self.long_name

    def clean(self):
        if self.automatic_max_tickets and self.id:
            self.max_tickets = self.compute_max_tickets()

    def compute_max_tickets(self):
        number_map = dict(self.get_rows_and_numbers())
        return sum((len(number_set) for number_set in number_map.values()), 0)

    @property
    def long_name(self):
        if self.event_name:
            return f'{self.event_name}: {self.name}'
        return f'{self.name}'

    @property
    def zones(self):
        from paikkala.models import Zone
        return Zone.objects.filter(rows__in=self.rows.all()).distinct()

    def get_block_map(self, zone=None):
        """
        Get a dict mapping row IDs to a set of blocked Numbers per row.

        :param zone: Optional zone to filter for.
        :return: Dict of row ID <-> excluded numbers set
        """
        blocks_by_row_id = defaultdict(set)
        qs = (self.blocks.filter(row__zone=zone) if zone else self.blocks.all())
        for block in qs:
            blocks_by_row_id[block.row_id] |= block.get_excluded_set()
        return blocks_by_row_id

    def get_rows_and_numbers(self, zone=None):
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

    def is_reservable(self):
        if not (self.reservation_start and self.reservation_end):
            return False
        return (self.reservation_start <= now() <= self.reservation_end)

    def check_reservable(self):
        if not self.is_reservable():
            raise Unreservable(f'{self} is not reservable at this time')
        if self.remaining_tickets <= 0:
            raise MaxTicketsReached(f'{self} has no remaining tickets.')

    @property
    def remaining_tickets(self):
        return self.max_tickets - self.tickets.count()

    def reserve(self, zone, count, user=None, name=None, email=None, phone=None, contact=None, allow_scatter=False,
                attempt_sequential=True):
        """
        Reserve `count` tickets from the zone `zone`.

        Unless `allow_scatter` is set, the tickets will all be allocated
        from a single Row.  If this is not possible, `NoCapacity` will be raised.

        This method is a generator, so please be sure to fully iterate it
        (i.e. `list(p.reserve())`).  Also, it'd be prudent to run it within a transaction.

        :param zone:
        :param count:
        :param user:
        :param allow_scatter: Whether to allow allocating tickets from scattered rows.
        :param attempt_sequential: Attempt allocation of sequential seats from each row.
        :return:
        """
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
                'Can only reserve {limit} tickets per batch for {program}, {n} attempted'.format(
                    limit=self.max_tickets_per_batch,
                    n=count,
                    program=self,
                )
            )
        self.check_reservable()
        reservation_status = zone.get_reservation_status(program=self)
        total_reserved = reservation_status.total_reserved
        if total_reserved + count > self.max_tickets:
            raise MaxTicketsReached(
                'Reserving {n} more tickets would overdraw {program}\'s ticket limit {limit}'.format(
                    n=count,
                    program=self,
                    limit=self.max_tickets,
                )
            )
        if user and self.tickets.filter(user=user).count() + count > self.max_tickets_per_user:
            raise MaxTicketsPerUserReached(
                '{user} reserving {n} more tickets would overdraw {program}\'s per-user ticket limit {limit}'.format(
                    user=user,
                    n=count,
                    program=self,
                    limit=self.max_tickets_per_user,
                )
            )
        new_reservations = []
        reserve_count = count  # Count remaining to reserve
        for row, row_status in sorted(reservation_status.items(), key=lambda pair: pair[1]['remaining']):
            if row_status['remaining'] >= reserve_count or allow_scatter or not self.numbered_seats:
                row_count = min(reserve_count, row_status['remaining'])
                new_reservations.append((row, row_count))
                reserve_count -= row_count
            if reserve_count <= 0:
                break
        if reserve_count > 0:  # Oops, ran out of rows with tickets left unscattered
            raise NoCapacity('Could not allocate {remaining} of {n} requested tickets in zone {zone}'.format(
                remaining=reserve_count,
                n=count,
                zone=zone,
            ))
        if not new_reservations:
            raise NoRowCapacity('No single row in zone {zone} has {n} tickets left (try scatter?)'.format(
                zone=zone,
                n=count,
            ))

        for row, row_count in new_reservations:
            yield from row.reserve(
                program=self,
                count=row_count,
                user=user,
                name=name,
                email=email,
                phone=phone,
                attempt_sequential=attempt_sequential,
                excluded_numbers=reservation_status[row]['blocked_set'],
            )
