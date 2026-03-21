#!/usr/bin/env python3

from collections import namedtuple
from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.db.models import Count

from paikkala.models.blocks import PerProgramBlock
from paikkala.models.tickets import Ticket
from paikkala.models.zones import Zone

if TYPE_CHECKING:
    from paikkala.models.programs import Program


CachedQualifier = namedtuple("CachedQualifier", ["text", "start", "end"])


@dataclass
class PaikkalaCache:
    """
    A cache object meant to be used during a single reservation. Attempts to optimise out as many
    database roundtrips as possible.
    """

    zone_to_seat_qualifiers: dict[int, list[CachedQualifier]]
    """dict of zone ID to a list of seat qualifiers"""

    def __init__(self, program: "Program"):
        all_rows = program.rows.all().prefetch_related("zone")
        all_zones = Zone.objects.filter(rows__in=all_rows).distinct()
        all_blocks = PerProgramBlock.objects.filter(program=program, row__in=all_rows)
        reserved_places_per_row = (
            Ticket.objects.filter(program=program)
            .values("zone", "row")
            .annotate(n=Count("id"))
            .values_list("zone", "row", "n")
        )