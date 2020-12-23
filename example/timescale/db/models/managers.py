from django.db import models
from timescale.db.models.querysets import *

class TimescaleManager(models.Manager):
    """
    A custom model manager specifically designed around the Timescale
    functions and tooling that has been ported to Django's ORM.
    """

    def get_queryset(self):
        return TimescaleQuerySet(self.model, using=self._db)
    
    def time_bucket(self, field, interval):
        return self.get_queryset().time_bucket(field, interval)
    
    def time_bucket_gapfill(self, field: str, interval: str, start: datetime, end: datetime, datapoints: int=240):
        return self.get_queryset().time_bucket_gapfill(field, interval, start, end, datapoints)

    def histogram(self, field: str, min_value: float, max_value: float, num_of_buckets: int = 5):
        return self.get_queryset().histogram(field, min_value, max_value, num_of_buckets)