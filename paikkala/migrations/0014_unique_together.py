# Generated by Django 2.1.7 on 2019-04-28 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paikkala', '0013_seat_qualifiers'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='row',
            unique_together={('zone', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='zone',
            unique_together={('room', 'name')},
        ),
    ]
