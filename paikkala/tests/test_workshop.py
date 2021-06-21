import pytest
from django.contrib.auth.models import AnonymousUser
from django.forms import HiddenInput
from django.urls import reverse

from paikkala.excs import (
    BatchSizeOverflow, ContactRequired, MaxTicketsPerUserReached, MaxTicketsReached, NoCapacity, Unreservable,
    UserRequired
)
from paikkala.models import Program
from django.utils.encoding import force_str


@pytest.mark.django_db
def test_workshop_program(workshop_program):
    assert workshop_program


@pytest.mark.django_db
def test_missing_contact(workshop_program, workshop_zone, user_client):
    with pytest.raises(ContactRequired):
        tickets = list(workshop_program.reserve(zone=workshop_zone, count=1, user=user_client.user))


@pytest.mark.django_db
def test_with_contact(workshop_program, workshop_zone, workshop_row, user_client):
    assert workshop_program.is_reservable()
    tickets = list(workshop_program.reserve(
        zone=workshop_zone,
        count=2,
        user=user_client.user,
        name='Nimi',
        email='user@example.com',
        phone='0',
    ))
    assert(len(tickets) == 2)
    ticket = tickets[0]
    resp = user_client.get(reverse('inspect', kwargs={'pk': ticket.pk, 'key': ticket.key}))
    assert not resp.context['show_seats']
    for ticket in tickets:
        assert ticket.key in force_str(resp.render().content)


@pytest.mark.django_db
def test_form(workshop_program, workshop_zone, workshop_row, user_client):
    assert workshop_program.is_reservable()
    resp = user_client.get(reverse('reserve', kwargs={'pk': workshop_program.pk}))
    assert isinstance(resp.context['form'].fields['zone'].widget, HiddenInput)
