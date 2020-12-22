from django.db import models
from .fields import TimescaleDateTimeField
from timescale.db


class TimescaleModel(models.Model):
    time = TimescaleDateTimeField(interval="1 day")

    class Meta:
        abstract = True