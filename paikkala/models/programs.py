from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from paikkala.excs import MaxTicketsReached, NoCapacity, NoRowCapacity, Unreservable


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
    name = models.CharField(
        max_length=64,
        help_text='please be specific; this is not qualified by event name or similar',
    )
    reservation_start = models.DateTimeField(blank=True, null=True)
    reservation_end = models.DateTimeField(blank=True, null=True)
    invalid_after = models.DateTimeField(
        blank=True,
        null=True,
        help_text='the time after which tickets for this program are considered out-of-date, e.g. for hiding from UI',
    )
    rows = models.ManyToManyField('paikkala.Row')
    max_tickets = models.IntegerField()

    objects = ProgramQuerySet.as_manager()

    def __str__(self):
        return '{name}'.format(name=self.name)

    @property
    def zones(self):
        from paikkala.models import Zone
        return Zone.objects.filter(rows__in=self.rows.all()).distinct()

    def is_reservable(self):
        if not (self.reservation_start and self.reservation_end):
            return False
        return (self.reservation_start <= now() <= self.reservation_end)

    def reserve(self, zone, count, user=None, allow_scatter=False):
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
        :return:
        """
        if count <= 0:  # pragma: no cover
            raise ValueError('Gotta reserve at least one ticket')
        if not self.is_reservable():
            raise Unreservable('{} is not reservable at this time'.format(self))
        reservation_status = zone.get_reservation_status(program=self)
        total_reserved = sum(r['reserved'] for r in reservation_status.values())
        if total_reserved + count > self.max_tickets:
            raise MaxTicketsReached('Reserving {} more tickets would overdraw {}\'s ticket limit {}'.format(
                count,
                self,
                self.max_tickets,
            ))
        new_reservations = []
        reserve_count = count  # Count remaining to reserve
        for row, row_status in sorted(reservation_status.items(), key=lambda pair: pair[1]['remaining']):
            if row_status['remaining'] >= reserve_count or allow_scatter:
                row_count = min(reserve_count, row_status['remaining'])
                new_reservations.append((row, row_count))
                reserve_count -= row_count
            if reserve_count <= 0:
                break
        if reserve_count > 0:  # Oops, ran out of rows with tickets left unscattered
            raise NoCapacity('Could not allocate {} of {} requested tickets in zone {}'.format(
                reserve_count,
                count,
                zone,
            ))
        if not new_reservations:
            raise NoRowCapacity('No single row in zone {} has {} tickets left (try scatter?)'.format(zone, count))

        for row, row_count in new_reservations:
            yield from row.reserve(program=self, count=row_count, user=user)
