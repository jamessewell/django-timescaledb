from django.db import models


class TimeBucket(models.Func):
    function = 'time_bucket'

    def __init__(self, expression, interval):
        if not isinstance(interval, models.Value):
            interval = models.Value(interval)
        super().__init__(interval, expression)
