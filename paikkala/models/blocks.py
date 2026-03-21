from typing import Set

from django.db import models
from django.utils.functional import cached_property

from paikkala.utils.ranges import parse_number_set, validate_number_set


class PerProgramBlock(models.Model):
    program = models.ForeignKey('Program', related_name='blocks', on_delete=models.CASCADE)
    row = models.ForeignKey('Row', related_name='+', on_delete=models.CASCADE)
    excluded_numbers = models.CharField(
        blank=True,
        max_length=128,
        validators=[validate_number_set],
        help_text='seat numbers to block from this row in this program',
    )

    @cached_property
    def excluded_set(self) -> Set[int]:
        return parse_number_set(self.excluded_numbers)
