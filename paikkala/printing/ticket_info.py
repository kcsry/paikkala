from collections import namedtuple, defaultdict
from typing import List, Optional, Set

from paikkala.models import Program, Zone, Row, SeatQualifier


class TicketInfo(
    namedtuple("_TicketInfo", ("program", "zone", "row", "number", "qualifier_texts"))
):
    program: Program
    zone: Zone
    row: Row
    number: int
    qualifier_texts: List[str]

    @property
    def qualified_zone(self):
        name = self.zone
        if self.qualifier_texts:
            name = f"{name} {' '.join(self.qualifier_texts)}"
        return name


def generate_ticket_infos(
    *,
    program: Program,
    zone_ids: Optional[Set[int]],
    included_numbers: Optional[Set[int]],
    excluded_numbers: Optional[Set[int]],
):
    # TODO: this all could use smarter queries, maybe

    seat_qualifiers_by_zone_id = defaultdict(list)
    for sq in SeatQualifier.objects.filter(zone__room=program.room):
        seat_qualifiers_by_zone_id[sq.zone_id].append(sq)

    for row, numbers in program.get_rows_and_numbers():
        if zone_ids and row.zone_id not in zone_ids:
            continue
        for number in numbers:
            if included_numbers and number not in included_numbers:
                continue
            if excluded_numbers and number in excluded_numbers:
                continue
            yield TicketInfo(
                program=program,
                zone=row.zone,
                row=row,
                number=number,
                qualifier_texts=[
                    q.text
                    for q in seat_qualifiers_by_zone_id[row.zone_id]
                    if q.start_number <= number <= q.end_number
                ],
            )
