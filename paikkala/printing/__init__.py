from collections.abc import Iterable, Iterator
from io import BytesIO
from itertools import groupby

from paikkala.models import Program, Zone
from paikkala.printing.configuration import PrintingConfiguration
from paikkala.printing.drawing import TicketDrawer
from paikkala.printing.ticket_info import TicketInfo, generate_ticket_infos

__all__ = [
    'PrintingConfiguration',
    'TicketInfo',
    'generate_ticket_infos',
    'generate_ticket_pdf',
]


def generate_ticket_pdf(
    *,
    drawer_class: type[TicketDrawer],
    configuration: PrintingConfiguration,
    program: Program,
    zones: list[Zone] | None = None,
    included_numbers: set[int] | None = None,
    excluded_numbers: set[int] | None = None,
) -> bytes:
    from reportlab.pdfgen.canvas import Canvas

    output_bio = BytesIO()
    canvas = Canvas(output_bio)
    ticket_infos = generate_ticket_infos(
        program=program,
        zone_ids=({z.id for z in zones} if zones is not None else None),
        included_numbers=included_numbers,
        excluded_numbers=excluded_numbers,
    )

    groups: Iterable[tuple[int | None, Iterator[TicketInfo]]]
    if configuration.separate_zones:
        groups = groupby(ticket_infos, key=lambda ti: ti.zone.id)
    else:
        groups = [(None, ticket_infos)]

    drawer = drawer_class(canvas=canvas, configuration=configuration)
    for _, ticket_infos in groups:
        drawer.draw_tickets(ticket_infos)
        canvas.showPage()  # blank page between zones
    canvas.save()
    return output_bio.getvalue()
