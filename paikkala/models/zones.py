from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Set

from django.db import models
from django.db.models import Count, Sum

if TYPE_CHECKING:
    from paikkala.models.programs import Program
    from paikkala.models.rows import Row


@dataclass
class RowReservationStatus:
    capacity: int
    reserved: int
    remaining: int
    blocked_set: Set[int]


class ZoneReservationStatus(dict):
    def __init__(self, zone: 'Zone', program: 'Program', data: Dict['Row', RowReservationStatus]) -> None:
        super().__init__(data)
        self.program = program
        self.zone = zone

    @property
    def total_reserved(self) -> int:
        return sum(r.reserved for r in self.values())

    @property
    def total_remaining(self) -> int:
        return sum(r.remaining for r in self.values())

    @property
    def total_capacity(self) -> int:
        return sum(r.capacity for r in self.values())


class Zone(models.Model):
    room = models.ForeignKey('paikkala.Room', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(editable=False, default=0)
    ordering = models.IntegerField(default=0, help_text='Smallest first')

    class Meta:
        unique_together = (
            (
                'room',
                'name',
            ),
        )
        ordering = ('room', 'ordering', 'name')

    def __str__(self) -> str:
        return f'{self.room.name} / {self.name}'

    def cache_total_capacity(self, save: bool = False) -> None:
        self.capacity = self.rows.aggregate(capacity=Sum('capacity')).get('capacity', 0)
        if save:
            self.save(update_fields=('capacity',))

    def clean(self) -> None:
        if self.id:
            self.cache_total_capacity()

    def save(self, **kwargs: Any) -> None:
        self.clean()
        super().save(**kwargs)

    def get_reservation_status(self, program: 'Program') -> ZoneReservationStatus:
        reservation_count = dict(
            self.tickets.filter(program=program).values('row').annotate(n=Count('id')).values_list('row', 'n')
        )
        row_status_map = {}
        block_map = program.get_block_map(zone=self)
        for row in program.rows.filter(zone=self):
            blocked = block_map.get(row.id, set())
            capacity = len(row.get_numbers(additional_excluded_set=blocked))
            reserved = reservation_count.get(row.id, 0)
            row_status_map[row] = RowReservationStatus(
                capacity=capacity,
                reserved=reserved,
                remaining=capacity - reserved,
                blocked_set=blocked,
            )
        return ZoneReservationStatus(
            zone=self,
            program=program,
            data=row_status_map,
        )
