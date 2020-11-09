import pytest


@pytest.mark.django_db
def test_smoke_printing(jussi_program):
    from paikkala.printing import generate_ticket_pdf
    from paikkala.printing.drawing import TicketDrawer
    from paikkala.printing.configuration import PrintingConfiguration

    assert b'%PDF' in generate_ticket_pdf(
        drawer_class=TicketDrawer,
        configuration=PrintingConfiguration(),
        program=jussi_program,
    )
