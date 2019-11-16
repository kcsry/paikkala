from django.core.management import BaseCommand
from django.db.transaction import atomic

from paikkala.utils.importer import import_zones, read_csv_file


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--zone-filename', '-z', required=True)
        parser.add_argument('--qualifier-filename', '-q', required=False)
        parser.add_argument('--default-room-name', default='Room')

    @atomic
    def handle(self, zone_filename, qualifier_filename, default_room_name, **options):
        z_rows = list(read_csv_file(zone_filename))
        q_rows = (list(read_csv_file(qualifier_filename)) if qualifier_filename else ())
        for zone in import_zones(
            row_csv_list=z_rows,
            qualifier_csv_list=q_rows,
            default_room_name=default_room_name,
            verbose=True,
        ):
            self.stdout.write(
                '%s: capacity %d, rows %s, %d qualifiers' % (
                    zone,
                    zone.capacity,
                    ', '.join(name for name in zone.rows.values_list('name', flat=True)),
                    zone.seat_qualifiers.count(),
                )
            )
