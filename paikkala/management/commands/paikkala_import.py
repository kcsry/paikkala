from django.core.management import BaseCommand
from django.db.transaction import atomic

from paikkala.utils.importer import read_csv_file, import_zones


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename')

    @atomic
    def handle(self, filename, **options):
        rows = list(read_csv_file(filename))
        for zone in import_zones(rows):
            self.stdout.write(
                '%s: capacity %d, rows %s' % (
                    zone,
                    zone.capacity,
                    ', '.join(name for name in zone.rows.values_list('name', flat=True)),
                )
            )
