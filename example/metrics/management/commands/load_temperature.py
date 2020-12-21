from django.core.management.base import BaseCommand, CommandError
from metrics.models import Metric
from django.utils import timezone
from random import uniform
from datetime import timedelta

class Command(BaseCommand):
    help = 'Uses PSUTILS to read any temperature sensor and adds a record'

    def handle(self, *args, **options):
        for i in range(1000):
            timestamp = timezone.now() - timedelta(minutes=i * 5)
            Metric.objects.create(time=timestamp, temperature=uniform(51.1, 53.3))
        