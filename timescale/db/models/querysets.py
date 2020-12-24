from django.db import models
from timescale.db.models.expressions import TimeBucket, TimeBucketGapFill
from timescale.db.models.aggregates import Histogram
from typing import Dict
from datetime import datetime

class TimescaleQuerySet(models.QuerySet):

    def time_bucket(self, field: str, interval: str, annotations: Dict = None):
        """
        Wraps the TimescaleDB time_bucket function into a queryset method.
        """
        if annotations:
            return self.values(bucket=TimeBucket(field, interval)).order_by('-bucket').annotate(**annotations)
        return self.values(bucket=TimeBucket(field, interval)).order_by('-bucket')
    
    def time_bucket_gapfill(self, field: str, interval: str, start: datetime, end: datetime, datapoints: int=240):
        """
        Wraps the TimescaleDB time_bucket_gapfill function into a queryset method.
        """
        return self.values(bucket=TimeBucketGapFill(field, interval, start, end, datapoints))

    def histogram(self, field: str, min_value: float, max_value: float, num_of_buckets: int = 5):
        """
        Wraps the TimescaleDB histogram function into a queryset method.
        """
        return self.values(histogram=Histogram(field, min_value, max_value, num_of_buckets))

    def to_list(self, normalise_datetimes: bool = False):
        if normalise_datetimes:
            normalised = []
            for b in list(self):
                b["bucket"] = b["bucket"].isoformat()
                normalised.append(b)
            return normalised
        return list(self)
