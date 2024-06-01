from __future__ import annotations

import os
from datetime import timedelta

from django.utils.timezone import now

from paikkala.models import Program, Room, Row, Zone
from paikkala.utils.importer import import_zones, read_csv_file

SIBELIUSTALO_DEFAULT_ROOM_NAME = 'Pääsali'


def get_sibeliustalo_rows():
    return list(read_csv_file(os.path.join(os.path.dirname(__file__), 'sibeliustalo.txt')))


def get_sibeliustalo_qualifiers():
    return list(read_csv_file(os.path.join(os.path.dirname(__file__), 'sibeliustalo-qualifiers.txt')))


def import_sibeliustalo_zones():
    return import_zones(
        row_csv_list=get_sibeliustalo_rows(),
        qualifier_csv_list=get_sibeliustalo_qualifiers(),
        default_room_name=SIBELIUSTALO_DEFAULT_ROOM_NAME,
    )


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


def create_scatter_program(zones: list[Zone], room=None):
    if not room:
        room = zones[0].room
    program = Program.objects.create(
        room=room,
        name='Hyvin suosittu ohjelmanumero',
        reservation_start=now() - timedelta(hours=1),
        reservation_end=now() + timedelta(hours=1),
        max_tickets=1_000_000,
        max_tickets_per_batch=1_000_000,
    )
    program.rows.set(Row.objects.filter(zone__in=zones))

    for zone in zones:
        row: Row
        for row in zone.rows.all():
            # Leave one seat per row
            _ = list(row.reserve(
                program=program,
                count=row.capacity - 1,
                user=None,
                name='Señor Developer',
                email='test@localhost',
                phone=None,
                attempt_sequential=False,
                excluded_numbers=None,
            ))

        status = zone.get_reservation_status(program)
        assert status.total_remaining == zone.rows.count()

    return program


def create_workshop_room():
    return Room.objects.create(
        name='Pajatila',
    )


def create_workshop_zone(room):
    return Zone.objects.create(
        room=room,
        name='15 hengen paja',
        capacity=15,
    )


def create_workshop_row(zone):
    return Row.objects.create(
        zone=zone,
        name='Numeroimaton paikka',
        start_number=1,
        end_number=15,
    )


def create_workshop_program(room, row):
    program = Program.objects.create(
        room=room,
        name='Aamukahvipaja',
        reservation_start=now() - timedelta(hours=1),
        reservation_end=now() + timedelta(hours=1),
        max_tickets=15,
        max_tickets_per_batch=2,
        numbered_seats=False,
        require_contact=True,
    )
    program.rows.set([row])
    program.save()
    return program
