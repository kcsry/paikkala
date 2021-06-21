import pytest
from django.urls import reverse

from paikkala.models import Ticket


@pytest.mark.django_db
def test_reserve(jussi_program, user_client):
    assert jussi_program.is_reservable()
    reserve_url = reverse('reserve', kwargs={'pk': jussi_program.pk})
    assert user_client.get(reserve_url).status_code == 200
    assert user_client.post(reserve_url, {
        'zone': jussi_program.zones[0].pk,
        'count': 5,
    }).status_code == 302
    assert Ticket.objects.filter(program=jussi_program, user=user_client.user).count() == 5


@pytest.mark.django_db
def test_relinquish(jussi_program, user_client):
    assert jussi_program.is_reservable()
    ticket, = jussi_program.reserve(zone=jussi_program.zones[0], count=1, user=user_client.user)
    user_client.post(reverse('relinquish', kwargs={'pk': ticket.pk}), {'key': ticket.key})
    assert not Ticket.objects.filter(program=jussi_program, user=user_client.user).exists()


@pytest.mark.django_db
def test_inspect(jussi_program, user_client):
    assert jussi_program.is_reservable()
    tickets = list(jussi_program.reserve(zone=jussi_program.zones[0], count=6, user=user_client.user))
    ticket = tickets[0]
    resp = user_client.get(reverse('inspect', kwargs={'pk': ticket.pk, 'key': ticket.key}))
    assert len(resp.context['tickets']) == 6
    assert jussi_program.name in str(resp.render().content)
