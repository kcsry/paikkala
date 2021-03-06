# Generated by Django 2.2.4 on 2019-08-18 11:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('paikkala', '0014_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='numbered_seats',
            field=models.BooleanField(default=True, help_text='Are seats numbered and should the numbers be shown to the user?'),
        ),
        migrations.AddField(
            model_name='program',
            name='require_contact',
            field=models.BooleanField(default=False, help_text='Require contact information (name, email, phone number) from the user?'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='phone',
            field=models.TextField(blank=True, null=True),
        ),
    ]
