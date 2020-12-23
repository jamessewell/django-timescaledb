from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")

    objects = TimescaleManager()

    class Meta:
        abstract = True