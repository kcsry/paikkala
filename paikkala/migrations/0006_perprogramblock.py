# Generated by Django 2.0.5 on 2018-06-11 17:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        ('paikkala', '0005_program_automatic_max_tickets'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerProgramBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('excluded_numbers', models.CharField(blank=True, help_text='seat numbers to block from this row in this program', max_length=128, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='paikkala.Program')),
                ('row', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='paikkala.Row')),
            ],
        ),
    ]
