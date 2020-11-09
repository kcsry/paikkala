from typing import List

from .ticket_info import TicketInfo

inch = 72.0
cm = inch / 2.54
A4 = (21.0 * cm, 29.7 * cm)


class PrintingConfiguration:
    base_image = None
    size_x = 8.0 * cm
    size_y = 5.0 * cm
    n_x = 2
    n_y = 5
    ticket_margin = 0.5 * cm
    page_margin = 1.5 * cm
    page_size = A4
    line_spacing = 16
    font_name = "Helvetica"
    font_size = 12
    text_align = "left"
    left_offset = 0.45 * cm
    separate_zones = True

    def get_text_lines(self, ticket_info: TicketInfo) -> List[str]:
        return [
            ticket_info.program,
            ticket_info.qualified_zone,
            str(ticket_info.number),
        ]
