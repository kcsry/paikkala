from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Set

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import models

from paikkala.utils.ranges import parse_number_set, validate_number_set
from paikkala.utils.runs import find_runs, following_integer

if TYPE_CHECKING:
    from paikkala.models.programs import Program
    from paikkala.models.tickets import Ticket


class Row(models.Model):
    zone = models.ForeignKey('paikkala.Zone', related_name='rows', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    start_number = models.IntegerField()
    end_number = models.IntegerField()
    capacity = models.IntegerField(editable=False, default=0)
    excluded_numbers = models.CharField(
        blank=True,
        max_length=128,
        validators=[validate_number_set],
        help_text='seat numbers to consider not part of the row; comma-separated integers',
    )

    class Meta:
        unique_together = (
            (
                'zone',
                'name',
            ),
        )

    def clean(self) -> None:
        if self.end_number < self.start_number:
            raise ValidationError('end number must be greater than start number')
        self.capacity = len(self.get_numbers())

    def save(self, **kwargs: Any) -> None:
        self.clean()
        super().save(**kwargs)
        self.zone.cache_total_capacity(save=True)

    def __str__(self) -> str:
        return f'{self.zone.room.name} – {self.zone.name} – {self.name}'

    def get_numbers(self, additional_excluded_set: Optional[Set[int]] = None) -> List[int]:
        excluded_set = self.get_excluded_set().union(additional_excluded_set or ())
        return [number for number in range(self.start_number, self.end_number + 1) if number not in excluded_set]

    def get_excluded_set(self) -> Set[int]:
        return parse_number_set(self.excluded_numbers)

    def reserve(
        self,
        *,
        program: 'Program',
        count: int,
        user: Optional[AbstractBaseUser] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        attempt_sequential: bool = True,
        excluded_numbers: Optional[Set[int]] = None,
    ) -> Iterator['Ticket']:
        reserved_numbers = set(program.tickets.filter(row=self).values_list('number', flat=True))
        unreserved_numbers = [
            number
            for number in self.get_numbers(additional_excluded_set=excluded_numbers)
            if number not in reserved_numbers
        ]

        if attempt_sequential and count > 1:
            # Find runs of sequential numbers in the unreserved numbers.
            sequential_runs = find_runs(unreserved_numbers, following_integer)
            # Filter in only those that would have at least N seats left.
            acceptable_sequential_runs = [run for run in sequential_runs if len(run) >= count]
            # If one was found, use it as the source of seat numbers to reserve.
            if acceptable_sequential_runs:
                unreserved_numbers = acceptable_sequential_runs[0]
                assert len(unreserved_numbers) >= count

        for _ in range(count):
            number = unreserved_numbers.pop(0)
            yield program.tickets.create(
                row=self,
                zone=self.zone,
                user=user,
                name=name,
                email=email,
                phone=phone,
                number=number,
            )
