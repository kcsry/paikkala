import pytest

from paikkala.models import Program, Ticket


@pytest.mark.django_db
def test_sibeliustalo_permanto_qualifiers(jussi_program: Program):
    zone = jussi_program.zones.get(name='Permanto')
    row = zone.rows.get(name='6')
    left_ticket: Ticket = jussi_program.tickets.create(
        zone=zone,
        row=row,
        number=row.start_number,
    )
    assert left_ticket.qualifier_texts == ['Vasen']
    assert 'Vasen' in str(left_ticket)

    right_ticket: Ticket = jussi_program.tickets.create(
        zone=zone,
        row=row,
        number=row.end_number,
    )
    assert right_ticket.qualifier_texts == ['Oikea']
    assert 'Oikea' in str(right_ticket)
