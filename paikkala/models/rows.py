from django.core.exceptions import ValidationError
from django.core.validators import validate_comma_separated_integer_list
from django.db import models


class Row(models.Model):
    zone = models.ForeignKey('paikkala.Zone', related_name='rows', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    start_number = models.IntegerField()
    end_number = models.IntegerField()
    capacity = models.IntegerField(editable=False, default=0)
    excluded_numbers = models.CharField(
        blank=True,
        max_length=128,
        validators=[validate_comma_separated_integer_list],
        help_text='seat numbers to consider not part of the row; comma-separated integers',
    )

    def clean(self):
        if self.end_number < self.start_number:
            raise ValidationError('end number must be greater than start number')
        self.capacity = len(self.get_numbers())

    def save(self, **kwargs):
        self.clean()
        super().save(**kwargs)
        self.zone.cache_total_capacity(save=True)

    def __str__(self):
        return '{zone} – {name}'.format(zone=self.zone.name, name=self.name)

    def get_numbers(self):
        excluded_set = self.get_excluded_set()
        return [
            number
            for number
            in range(self.start_number, self.end_number + 1)
            if number not in excluded_set
        ]

    def get_excluded_set(self):
        return set(int(number) for number in self.excluded_numbers.split(',') if number and number.isdigit())

    def reserve(self, program, count, user=None):
        reserved_numbers = set(program.tickets.filter(row=self).values_list('number', flat=True))
        unreserved_numbers = [number for number in self.get_numbers() if number not in reserved_numbers]
        for x in range(count):
            number = unreserved_numbers.pop(0)
            yield program.tickets.create(
                row=self,
                zone=self.zone,
                user=user,
                number=number,
            )
