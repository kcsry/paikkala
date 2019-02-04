import logging
import time

from django import forms
from django.core.validators import MaxValueValidator
from django.db import IntegrityError

from paikkala.fields import ReservationZoneChoiceField, ReservationZoneSelect
from paikkala.models import Program, Zone

log = logging.getLogger(__name__)


class ReservationForm(forms.ModelForm):
    max_count = 5
    integrity_error_retries = 10

    zone = ReservationZoneChoiceField(queryset=Zone.objects.none(), empty_label=None)
    count = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        fields = ()
        model = Program

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReservationForm, self).__init__(**kwargs)
        self.mangle_count_field()
        self.mangle_zone_field()

    def mangle_zone_field(self):
        zone_field = self.fields['zone']
        zone_field.queryset = self.instance.zones.all().order_by('name')

        if isinstance(zone_field, ReservationZoneChoiceField):
            # This additional magic is required because widgets don't have access to their
            # parent fields.  That would be all too easy.
            # ReservationZoneSelect.create_option will process the `z` object here to something sane.
            zone_field.choices = [(z.id, z) for z in zone_field.queryset]
            zone_field.populate_reservation_statuses(program=self.instance)
            zone_field.widget = ReservationZoneSelect(
                attrs=None,
                choices=zone_field.choices,
                reservation_statuses=zone_field.reservation_statuses,
                format_label=zone_field.label_from_instance,
            )

    def mangle_count_field(self):
        if self.max_count:
            self.fields['count'].validators.append(MaxValueValidator(self.max_count))

    def save(self, commit=True):
        assert commit
        retry_attempts = self.integrity_error_retries
        while True:
            try:
                return list(
                    self.instance.reserve(
                        user=self.user,
                        zone=self.cleaned_data['zone'],
                        count=self.cleaned_data['count'],
                    )
                )
            except IntegrityError as ie:
                if retry_attempts <= 0:
                    raise
                retry_attempts -= 1
                log_message = (
                    'Encountered IntegrityError when reserving {count} '
                    'seats in zone {zone} for {program}; {n} retries left'
                ).format(
                    count=self.cleaned_data['count'],
                    zone=self.cleaned_data['zone'],
                    program=self.instance,
                    n=retry_attempts,
                )
                log.warning(log_message, exc_info=True)
                time.sleep(.3)
