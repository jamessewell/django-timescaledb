from django.db import models
from timescale.db.models.querysets import TimescaleQuerySet

class TimescaleManager(models.Manager):

    def get_queryset(self):
        return TimescaleQuerySet(self.model, using=self._db)
    
    def time_bucket(self, field, interval):
        return self.get_queryset().time_bucket(field, interval)