import pytest
from django.urls import reverse

from paikkala.excs import NoCapacity
from paikkala.models import Program, Ticket


@pytest.mark.django_db
def test_reserve(jussi_program: Program, user_client) -> None:
    assert jussi_program.is_reservable()
    reserve_url = reverse('reserve', kwargs={'pk': jussi_program.pk})
    assert user_client.get(reserve_url).status_code == 200
    assert (
        user_client.post(
            reserve_url,
            {
                # No `allow_scatter` key, mimicking an unchecked checkbox: the
                # field is optional, so the form must still validate.
                'zone': jussi_program.zones[0].pk,
                'count': 5,
            },
        ).status_code
        == 302
    )
    assert Ticket.objects.filter(program=jussi_program, user=user_client.user).count() == 5


@pytest.mark.django_db
def test_reserve_allow_scatter_e2e(scatter_program, user_client):
    # Every row in scatter_program has exactly one free seat, so a two-seat
    # request can only be satisfied by scattering across rows.
    url = reverse('reserve', kwargs={'pk': scatter_program.pk})

    # Unchecked checkbox (field omitted): no single zone can fit two seats, so
    # the reservation fails. (NoCapacity is handled by downstream code; here it
    # simply propagates.)
    with pytest.raises(NoCapacity):
        user_client.post(url, {'zone': '', 'count': 2})
    assert not Ticket.objects.filter(program=scatter_program, user=user_client.user).exists()

    # Checked: the two seats are allocated from different rows.
    resp = user_client.post(url, {'zone': '', 'count': 2, 'allow_scatter': 'on'})
    assert resp.status_code == 302
    tickets = Ticket.objects.filter(program=scatter_program, user=user_client.user)
    assert tickets.count() == 2
    assert tickets.values('row').distinct().count() == 2


@pytest.mark.django_db
def test_bound_form_skips_reservation_status(jussi_program: Program, user_client) -> None:
    from paikkala.forms import ReservationForm

    zone = jussi_program.zones.first()

    # An unbound (GET) form computes the per-zone "seats remaining" figures...
    unbound = ReservationForm(instance=jussi_program, user=user_client.user)
    assert unbound.fields['zone'].reservation_statuses
    assert '(' in unbound.fields['zone'].label_from_instance(zone)

    # ...but a bound (POST) form skips that work, so labels fall back to str(zone).
    bound = ReservationForm(
        data={'zone': zone.pk, 'count': 1},
        instance=jussi_program,
        user=user_client.user,
    )
    assert bound.fields['zone'].reservation_statuses == {}
    assert bound.fields['zone'].label_from_instance(zone) == str(zone)


@pytest.mark.django_db
def test_relinquish(jussi_program: Program, user_client) -> None:
    assert jussi_program.is_reservable()
    (ticket,) = jussi_program.reserve(zone=jussi_program.zones[0], count=1, user=user_client.user)
    user_client.post(reverse('relinquish', kwargs={'pk': ticket.pk}), {'key': ticket.key})
    assert not Ticket.objects.filter(program=jussi_program, user=user_client.user).exists()


@pytest.mark.django_db
def test_inspect(jussi_program: Program, user_client) -> None:
    assert jussi_program.is_reservable()
    tickets = list(jussi_program.reserve(zone=jussi_program.zones[0], count=6, user=user_client.user))
    ticket = tickets[0]
    resp = user_client.get(reverse('inspect', kwargs={'pk': ticket.pk, 'key': ticket.key}))
    assert len(resp.context['tickets']) == 6
    assert jussi_program.name in str(resp.render().content)
