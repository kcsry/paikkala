import os
from datetime import timedelta

import pytest
from django.test import Client
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from paikkala.models import Program, Row, Zone
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
        max_tickets_per_batch=1000,
    )
    program.rows.set(Row.objects.filter(zone__in=sibeliustalo_zones))
    return program


@pytest.fixture
def lattia_program():
    zone = Zone.objects.create(name='lattia')
    row = Row.objects.create(zone=zone, start_number=1, end_number=10, excluded_numbers='3,4,5')
    assert row.capacity == 7
    t = now()
    program = Program.objects.create(
        name='program',
        max_tickets=100,
        reservation_start=t,
        reservation_end=t + timedelta(days=1),
    )
    program.rows.set([row])
    return program


@pytest.fixture
def user_client(random_user):
    client = Client()
    client.force_login(random_user)
    client.user = random_user
    return client


@pytest.fixture
def random_user(django_user_model):
    return django_user_model.objects.create_user(username=get_random_string())
