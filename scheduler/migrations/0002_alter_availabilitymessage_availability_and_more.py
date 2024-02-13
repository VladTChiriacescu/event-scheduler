# Generated by Django 5.0.1 on 2024-01-29 12:09

import django.db.models.deletion
import django_mysql.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availabilitymessage',
            name='availability',
            field=django_mysql.models.ListCharField(models.CharField(max_length=24), max_length=250, size=10),
        ),
        migrations.AlterField(
            model_name='availabilitymessage',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scheduler.event'),
        ),
    ]