from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=80)
    email = models.CharField(max_length=80)
    company = models.CharField(max_length=80)
    country = models.CharField(max_length=80)


# Temporarily store availability messages in the database.
# This will be replaced by a message queue in the next chapter.


class Event(models.Model):
    name = models.CharField(max_length=80)
    window = models.CharField(max_length=80, default=None)
    company = models.CharField(max_length=80)
    country = models.CharField(max_length=80)
    start_date = models.CharField(max_length=80, default='')
    employees = models.ManyToManyField(Employee, default=None, related_name='models')


class AvailabilityMessage(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    availability = models.CharField(max_length=256)
