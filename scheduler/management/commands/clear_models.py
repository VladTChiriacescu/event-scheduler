from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from scheduler.models import Employee, Availability, AvailabilityMessage, Event


class Command(BaseCommand):
    def handle(self, *args, **options):
        Employee.objects.all().delete()
        User.objects.all().delete()
        Availability.objects.all().delete()
        AvailabilityMessage.objects.all().delete()
        Event.objects.all().delete()
