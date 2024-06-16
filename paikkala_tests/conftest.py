from datetime import timedelta

import pytest
from django.test import Client
from django.utils.crypto import get_random_string
from django.utils.timezone import now

from paikkala.demo_data import (
    create_jussi_program,
    import_sibeliustalo_zones,
)
from paikkala.models import Program, Room, Row, Zone
from paikkala_tests.utils import (
    create_scatter_program,
    create_workshop_program,
    create_workshop_room,
    create_workshop_row,
    create_workshop_zone,
)


@pytest.fixture
def sibeliustalo_zones():
    return import_sibeliustalo_zones()


@pytest.fixture
def jussi_program(sibeliustalo_zones):
    return create_jussi_program(sibeliustalo_zones)


@pytest.fixture
def scatter_program(sibeliustalo_zones):
    return create_scatter_program(sibeliustalo_zones)


@pytest.fixture
def workshop_room():
    return create_workshop_room()


@pytest.fixture
def workshop_zone(workshop_room):
    return create_workshop_zone(workshop_room)


@pytest.fixture
def workshop_row(workshop_zone):
    return create_workshop_row(workshop_zone)


@pytest.fixture
def workshop_program(workshop_room, workshop_row):
    return create_workshop_program(workshop_room, workshop_row)


@pytest.fixture
def lattia_program():
    room = Room.objects.create(name='huone')
    zone = Zone.objects.create(name='lattia', room=room)
    row = Row.objects.create(zone=zone, start_number=1, end_number=10, excluded_numbers='3,4,5')
    assert row.capacity == 7
    t = now()
    program = Program.objects.create(
        room=zone.room,
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
    return django_user_model.objects.create_user(username=get_random_string(12))
