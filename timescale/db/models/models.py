from django.db import models
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager


class TimescaleModel(models.Model):
    """
    
    TimescaleModel is an abstract class that wraps up the configuration of timescale datetime field and a customer manager with built in querysets using timescales custom functions

    """
    time = TimescaleDateTimeField(interval="1 day")

    objects = TimescaleManager()

    class Meta:
        abstract = True