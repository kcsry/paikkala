from django.db import models
from django.db.models import Sum, Count


class Zone(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(editable=False, default=0)

    def __str__(self):
        return '{name}'.format(name=self.name)

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
        return {
            row: {
                'capacity': row.capacity,
                'reserved': reservation_count.get(row.id, 0),
                'remaining': row.capacity - reservation_count.get(row.id, 0),
            }
            for row
            in program.rows.filter(zone=self)
        }
