from django.db import models
from timescale.fields import TimescaleDateTimeField
from timescale.expressions import TimeBucket
from typing import Dict

class TimescaleQuerySet(models.QuerySet):

    def time_bucket(self, field: str, interval: str, annotations: Dict = None):
        """
        """
        if annotations:
            return self.all().values(bucket=TimeBucket(field, interval)).order_by('-bucket').annotate(**annotations)
        return self.all().values(bucket=TimeBucket(field, interval)).order_by('-bucket')
    
    def to_list(self, normalise_datetimes: bool = True):
        if normalise_datetimes:
            normalised = []
            for b in list(self):
                b["bucket"] = b["bucket"].isoformat()
                normalised.append(b)
            return normalised
        return list(self)

class TimescaleManager(models.Manager):

    def get_queryset(self):
        return TimescaleQuerySet(self.model, using=self._db)
    
    def time_bucket(self, field, interval):
        return self.get_queryset().time_bucket(field, interval)

# Create your models here.
class Metric(models.Model):
    time = TimescaleDateTimeField(interval="1 day")
    temperature = models.FloatField(default=0.0)

    objects = models.Manager()
    timescale = TimescaleManager()