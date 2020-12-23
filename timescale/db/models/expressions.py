from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.functions.mixins import (
    FixDurationInputMixin, NumericOutputFieldMixin,
)
from django.utils import timezone
from datetime import timedelta

class Interval(models.Func):
    function = 'INTERVAL'
    template = "%(function)s %(expressions)s"

    def __init__(self, interval):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        super().__init__(interval)
    

class TimeBucket(models.Func):
    function = 'time_bucket'
    name = "time_bucket"

    def __init__(self, expression, interval):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        super().__init__(interval, expression)


class TimeBucketGapFill(models.Func):
    function = 'time_bucket_gapfill'
    name = "time_bucket_gapfill"

    def __init__(self, expression, interval, start, end, datapoints=240):
        if not isinstance(interval, models.Value):
            interval = Interval(interval) / datapoints
        super().__init__(interval, expression, start, end)