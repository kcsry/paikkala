from django.core.management import BaseCommand
from django.db.transaction import atomic

from paikkala.utils.importer import read_csv_file, import_zones


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('zone_filename')
        parser.add_argument('qualifier_filename', required=False)

    @atomic
    def handle(self, zone_filename, qualifier_filename, **options):
        z_rows = list(read_csv_file(zone_filename))
        q_rows = (list(read_csv_file(qualifier_filename)) if qualifier_filename else ())
        for zone in import_zones(row_csv_list=z_rows, qualifier_csv_list=q_rows):
            self.stdout.write(
                '%s: capacity %d, rows %s' % (
                    zone,
                    zone.capacity,
                    ', '.join(name for name in zone.rows.values_list('name', flat=True)),
                )
            )
