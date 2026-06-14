from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import Sum

if TYPE_CHECKING:
    from paikkala.models.programs import Program
    from paikkala.models.rows import Row


@dataclass
class RowReservationStatus:
    capacity: int
    reserved: int
    remaining: int
    blocked_set: set[int]
    # The concrete set of reserved seat numbers. Only the allocation path
    # (`Zone.get_reservation_status`) populates this; the batched display path
    # (`Program.get_reservation_statuses`) only needs counts, so it's optional.
    reserved_set: set[int] = field(default_factory=set)


class ZoneReservationStatus(dict):
    def __init__(self, zone: Zone, program: Program, data: dict[Row, RowReservationStatus]) -> None:
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

    def get_reservation_status(self, program: Program) -> ZoneReservationStatus:
        reserved_by_row: dict[int, set[int]] = defaultdict(set)
        for row_id, number in self.tickets.filter(program=program).values_list('row', 'number'):
            reserved_by_row[row_id].add(number)

        row_status_map = {}
        block_map = program.get_block_map(zone=self)
        for row in program.rows.filter(zone=self):
            assert row.zone_id == self.id
            row.zone = self  # We thus know this to be true.
            blocked = block_map.get(row.id, set())
            capacity = len(row.get_numbers(additional_excluded_set=blocked))
            reserved_set = reserved_by_row.get(row.id, set())
            reserved = len(reserved_set)
            row_status_map[row] = RowReservationStatus(
                capacity=capacity,
                reserved=reserved,
                remaining=capacity - reserved,
                blocked_set=blocked,
                reserved_set=reserved_set,
            )
        return ZoneReservationStatus(
            zone=self,
            program=program,
            data=row_status_map,
        )
