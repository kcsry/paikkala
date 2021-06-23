from typing import TYPE_CHECKING, Iterator, Tuple

from .configuration import PrintingConfiguration, cm
from .ticket_info import TicketInfo

if TYPE_CHECKING:
    from reportlab.pdfgen.canvas import Canvas


class TicketDrawer:
    def __init__(self, canvas: "Canvas", configuration: PrintingConfiguration) -> None:
        self.canvas = canvas
        self.configuration = configuration

    def draw_tickets(
        self,
        ticket_infos: Iterator[TicketInfo],
    ) -> None:
        while ticket_infos:
            self.canvas.setFont(self.configuration.font_name, self.configuration.font_size)
            for iy in range(self.configuration.n_y):
                for ix in range(self.configuration.n_x):
                    ticket = next(ticket_infos, None)
                    if not ticket:
                        return
                    page_x, page_y = self.get_ticket_coords(ix, iy)
                    self.canvas.saveState()
                    self.canvas.translate(page_x, page_y)
                    self.draw_single_ticket(ticket)
                    self.canvas.restoreState()
            self.canvas.showPage()

    def get_ticket_coords(self, ix: int, iy: int) -> Tuple[float, float]:
        ticket_margin = self.configuration.ticket_margin
        page_margin = self.configuration.page_margin

        # Compute mathematical coordinates
        page_x = ix * (self.configuration.size_x + ticket_margin)
        page_y = (1 + iy) * (self.configuration.size_y + ticket_margin)

        # Flip Y upside down and add margins
        page_y = self.configuration.page_size[1] - page_margin - page_y
        page_x = page_margin + page_x
        return page_x, page_y

    def draw_single_ticket(self, ticket: TicketInfo) -> None:
        """
        Draw a single ticket. `self.canvas` has already been translated correctly.
        """
        if self.configuration.base_image:
            self.canvas.drawImage(
                self.configuration.base_image,
                0,
                0,
                self.configuration.size_x,
                self.configuration.size_y,
            )
        if self.configuration.text_align == "left":
            draw_text = self.canvas.drawString
        elif self.configuration.text_align == "center":
            draw_text = self.canvas.drawCentredString
        for y, line in enumerate(self.configuration.get_text_lines(ticket)):
            draw_text(
                self.configuration.left_offset,
                self.configuration.size_y
                - 0.25 * cm
                - (y + 1) * self.configuration.line_spacing,
                str(line),
            )
