# Generated by Django 2.1.7 on 2019-04-27 11:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paikkala', '0012_excluded_numbers_validator'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeatQualifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_number', models.IntegerField()),
                ('end_number', models.IntegerField()),
                ('text', models.CharField(max_length=64)),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seat_qualifiers', to='paikkala.Zone')),
            ],
        ),
        migrations.AddField(
            model_name='ticket',
            name='qualifier_text_cache',
            field=models.TextField(blank=True, editable=False),
        ),
    ]
