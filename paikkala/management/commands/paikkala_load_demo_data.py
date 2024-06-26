import random
from argparse import ArgumentParser
from typing import Any

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.transaction import atomic
from django.utils.crypto import get_random_string

from paikkala.demo_data import (
    SIBELIUSTALO_DEFAULT_ROOM_NAME,
    create_jussi_program,
    import_sibeliustalo_zones,
)
from paikkala.excs import NoCapacity
from paikkala.models import Zone


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--yes", "-y", default=False, action="store_true")

    @atomic
    def handle(self, yes: bool, **options: Any) -> None:
        if not yes:
            self.stderr.write('this command requires the --yes parameter, as it will mess up your database')
            return
        sibeliustalo_zones = list(Zone.objects.filter(room__name=SIBELIUSTALO_DEFAULT_ROOM_NAME))
        if not sibeliustalo_zones:
            sibeliustalo_zones = import_sibeliustalo_zones()
        room = sibeliustalo_zones[0].room
        program = room.program_set.first() or create_jussi_program(sibeliustalo_zones, room=room)
        user = User.objects.create_user(f'random-demo-{get_random_string(12)}')
        prog_zones = list(program.zones)
        for _ in range(10):
            zone = random.choice(prog_zones)
            count = random.randint(1, 5)
            try:
                tickets = list(program.reserve(zone=zone, count=count, user=user))
                self.stdout.write(f'{user}: Reserved {len(tickets):d} tickets in {zone.name}')
            except NoCapacity:
                break
