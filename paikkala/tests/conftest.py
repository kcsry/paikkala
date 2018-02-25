import os
from datetime import timedelta

import pytest
from django.utils.timezone import now

from paikkala.models import Program
from paikkala.utils.importer import import_zones, read_csv_file

sibeliustalo_rows = list(read_csv_file(os.path.join(os.path.dirname(__file__), 'sibeliustalo.txt')))


@pytest.fixture
def sibeliustalo_zones():
    return import_zones(sibeliustalo_rows)


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
