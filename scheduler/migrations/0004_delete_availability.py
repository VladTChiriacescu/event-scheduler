# Generated by Django 5.0.1 on 2024-01-31 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0003_alter_availabilitymessage_availability'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Availability',
        ),
    ]