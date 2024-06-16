import pytest


@pytest.mark.django_db
def test_smoke_printing(jussi_program):
    pytest.importorskip('reportlab')
    from paikkala.printing import generate_ticket_pdf
    from paikkala.printing.configuration import PrintingConfiguration
    from paikkala.printing.drawing import TicketDrawer

    assert b'%PDF' in generate_ticket_pdf(
        drawer_class=TicketDrawer,
        configuration=PrintingConfiguration(),
        program=jussi_program,
    )
