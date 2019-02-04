import os
from datetime import timedelta

from django.utils.timezone import now

from paikkala.models import Program, Row
from paikkala.utils.importer import import_zones, read_csv_file


def get_sibeliustalo_rows():
    return list(read_csv_file(os.path.join(os.path.dirname(__file__), 'sibeliustalo.txt')))


def import_sibeliustalo_zones():
    return import_zones(get_sibeliustalo_rows(), default_room_name='Pääsali')


def create_jussi_program(zones, room=None):
    if not room:
        room = zones[0].room
    program = Program.objects.create(
        room=room,
        name='Jussi laskeutuu katosta enkelikuoron saattelemana',
        reservation_start=now() - timedelta(hours=1),
        reservation_end=now() + timedelta(hours=1),
        max_tickets=100,
        max_tickets_per_batch=1000,
    )
    program.rows.set(Row.objects.filter(zone__in=zones))
    return program
