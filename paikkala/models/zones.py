from django.db import models
from django.db.models import Count, Sum

from paikkala.utils.blocks import get_per_program_blocks


class ZoneReservationStatus(dict):
    def __init__(self, zone, program, data):
        super(ZoneReservationStatus, self).__init__(data)
        self.program = program
        self.zone = zone

    @property
    def total_reserved(self):
        return sum(r['reserved'] for r in self.values())

    @property
    def total_remaining(self):
        return sum(r['remaining'] for r in self.values())

    @property
    def total_capacity(self):
        return sum(r['capacity'] for r in self.values())


class Zone(models.Model):
    room = models.ForeignKey('paikkala.Room', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(editable=False, default=0)

    def __str__(self):
        return '{room} / {name}'.format(room=self.room.name, name=self.name)

    def cache_total_capacity(self, save=False):
        self.capacity = self.rows.aggregate(capacity=Sum('capacity')).get('capacity', 0)
        if save:
            self.save(update_fields=('capacity',))

    def clean(self):
        if self.id:
            self.cache_total_capacity()

    def save(self, **kwargs):
        self.clean()
        super().save(**kwargs)

    def get_reservation_status(self, program):
        reservation_count = dict(
            self.tickets.filter(program=program).values('row').annotate(n=Count('id')).values_list('row', 'n')
        )
        data = {}
        block_map = get_per_program_blocks(program=program, zone=self)
        for row in program.rows.filter(zone=self):
            blocked = block_map[row.id]
            capacity = len(row.get_numbers(additional_excluded_set=blocked))
            reserved = reservation_count.get(row.id, 0)
            data[row] = {
                'capacity': capacity,
                'reserved': reserved,
                'remaining': capacity - reserved,
                'blocked_set': blocked,
            }
        return ZoneReservationStatus(
            zone=self,
            program=program,
            data=data,
        )
