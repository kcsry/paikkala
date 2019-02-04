# Generated by Django 2.1.5 on 2019-02-04 15:36

from django.db import migrations


def assign_default_room(apps, schema_editor):
    Room = apps.get_model('paikkala', 'Room')
    Zone = apps.get_model('paikkala', 'Zone')
    Program = apps.get_model('paikkala', 'Program')
    default_room = (Room.objects.first() or Room.objects.create(name='Room'))
    Zone.objects.filter(room__isnull=True).update(room=default_room)
    Program.objects.filter(room__isnull=True).update(room=default_room)


class Migration(migrations.Migration):
    dependencies = [
        ('paikkala', '0008_room'),
    ]

    operations = [
        migrations.RunPython(assign_default_room, migrations.RunPython.noop),
    ]