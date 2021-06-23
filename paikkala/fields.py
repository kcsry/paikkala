from typing import Dict

from django.forms import ModelChoiceField, RadioSelect
from django.utils.translation import gettext_lazy as _

from paikkala.models import Program, Zone
from paikkala.models.zones import ZoneReservationStatus


class ReservationZoneSelect(RadioSelect):
    def __init__(self, attrs=None, choices=(), reservation_statuses=None, format_label=str) -> None:  # noqa: ANN001
        super().__init__(attrs, choices)
        self.reservation_statuses = reservation_statuses or {}
        self.format_label = format_label

    def create_option(self, *args, **kwargs):  # noqa
        op = super().create_option(*args, **kwargs)
        if isinstance(op['label'], Zone):
            zone = op['label']
            if zone in self.reservation_statuses:
                if self.reservation_statuses[zone].total_remaining <= 0:
                    op['attrs']['disabled'] = True
                    op['attrs']['class'] = 'text-muted'
            op['label'] = self.format_label(zone)
        return op


class ReservationZoneChoiceField(ModelChoiceField):
    widget = RadioSelect()
    reservation_statuses: Dict[Zone, ZoneReservationStatus] = {}
    label_format = _('{zone} ({remaining} seats remain)')

    def populate_reservation_statuses(self, program: Program) -> None:
        self.reservation_statuses = {
            zone: zone.get_reservation_status(program=program)
            for zone
            in self.queryset
        }

    def label_from_instance(self, obj: Zone) -> str:
        if obj in self.reservation_statuses:
            return self.format_label(obj, self.reservation_statuses[obj])
        return str(obj)

    def format_label(self, zone: Zone, info: ZoneReservationStatus) -> str:
        return str(self.label_format).format(
            zone=zone.name,
            capacity=info.total_capacity,
            reserved=info.total_reserved,
            remaining=info.total_remaining,
        )
