from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.functions.mixins import (
    FixDurationInputMixin,
    NumericOutputFieldMixin,
)
from django.utils import timezone
from datetime import timedelta
from timescale.db.models.fields import TimescaleDateTimeField

class Interval(models.Func):
    """
    A helper class to format the interval used by the time_bucket_gapfill function to generate correct timestamps.
    Accepts an interval e.g '1 day', '5 days', '1 hour'
    """

    function = "INTERVAL"
    template = "%(function)s %(expressions)s"

    def __init__(self, interval, *args, **kwargs):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        super().__init__(interval, *args, **kwargs)


class TimeBucket(models.Func):
    """
    Implementation of the time_bucket function from Timescale.

    Read more about it here - https://docs.timescale.com/latest/using-timescaledb/reading-data#time-bucket

    Response:

    [
        {'bucket': '2020-12-22T10:00:00+00:00', 'devices': 12},
        {'bucket': '2020-12-22T09:00:00+00:00', 'devices': 12},
        {'bucket': '2020-12-22T08:00:00+00:00', 'devices': 12},
        {'bucket': '2020-12-22T07:00:00+00:00', 'devices': 12},
    ]

    """

    function = "time_bucket"
    name = "time_bucket"

    def __init__(self, expression, interval, *args, **kwargs):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        output_field = TimescaleDateTimeField(interval=interval)
        super().__init__(interval, expression, output_field=output_field)


class TimeBucketGapFill(models.Func):
    """
    IMplementation of the time_bucket_gapfill function from Timescale

    Read more about it here - https://docs.timescale.com/latest/using-timescaledb/reading-data#gap-filling

    Response:

    [
        ...
        {'bucket': '2020-12-22T11:36:00+00:00', 'temperature__avg': 52.7127405105567},
        {'bucket': '2020-12-22T11:42:00+00:00', 'temperature__avg': None},
        ...
    ]
    """

    function = "time_bucket_gapfill"
    name = "time_bucket_gapfill"

    def __init__(
        self, expression, interval, start, end, *args, datapoints=240, **kwargs
    ):
        if not isinstance(interval, models.Value):
            interval = Interval(interval) / datapoints
        output_field = TimescaleDateTimeField(interval=interval)
        super().__init__(interval, expression, start, end, output_field=output_field)
