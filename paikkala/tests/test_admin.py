import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string

from paikkala.models import Program


@pytest.mark.django_db
def test_program_creation(admin_client, sibeliustalo_zones):
    zone = next(z for z in sibeliustalo_zones if z.name == 'Permanto')
    row_ids = zone.rows.values_list('id', flat=True)
    room = sibeliustalo_zones[0].room
    name = get_random_string()
    add_url = reverse('admin:paikkala_program_add')
    admin_client.get(add_url)
    resp = admin_client.post(add_url, {
        'event_name': 'dässgön',
        'name': name,
        'room': room.id,
        'rows': tuple(row_ids),
        'max_tickets': '100',
        'max_tickets_per_user': '1000',
        'max_tickets_per_batch': '50',
        'blocks-TOTAL_FORMS': '3',
        'blocks-INITIAL_FORMS': 0,
        'blocks-MIN_NUM_FORMS': 0,
        'blocks-MAX_NUM_FORMS': 1000,
    }, follow=True)
    assert resp.status_code == 200
    assert Program.objects.get(name=name)
