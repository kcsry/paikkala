# Generated by Django 2.1.5 on 2019-02-04 15:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paikkala', '0009_default_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='paikkala.Room'),
        ),
        migrations.AlterField(
            model_name='zone',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='paikkala.Room'),
        ),
    ]
