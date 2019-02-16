from django.db import models

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

    def get_excluded_set(self):
        return parse_number_set(self.excluded_numbers)
