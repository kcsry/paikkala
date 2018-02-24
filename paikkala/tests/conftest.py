import os
from datetime import timedelta

import pytest
from django.utils.timezone import now

from paikkala.models import Zone, Program


def read_csv(infp, separator=','):
    headers = None
    for line in infp:
        line = line.strip().split(separator)
        if not headers:
            headers = line
            continue
        yield dict(zip(headers, line))


def read_csv_file(filename, separator=','):
    with open(filename, encoding='utf-8') as infp:
        yield from read_csv(infp, separator)


sibeliustalo_rows = list(read_csv_file(os.path.join(os.path.dirname(__file__), 'sibeliustalo.txt')))


@pytest.fixture
def sibeliustalo_zones():
    zones = {}
    for r_dict in sibeliustalo_rows:
        zone = zones.get(r_dict['zone'])
        if not zone:
            zone = zones[r_dict['zone']] = Zone.objects.create(name=r_dict['zone'])
        row = zone.rows.create(
            start_number=int(r_dict['start']),
            end_number=int(r_dict['end']),
            name=int(r_dict['row']),
        )
        assert row.capacity > 0
    return list(zones.values())


@pytest.fixture
def jussi_program(sibeliustalo_zones):
    program = Program.objects.create(
        name='Jussi laskeutuu katosta enkelikuoron saattelemana',
        reservation_start=now() - timedelta(hours=1),
        reservation_end=now() + timedelta(hours=1),
        max_tickets=100,
    )
    program.zones.set(sibeliustalo_zones)
    return program
