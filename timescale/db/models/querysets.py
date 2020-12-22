from django.db import models
from timescale.db.models.expressions import TimeBucket
from typing import Dict

class TimescaleQuerySet(models.QuerySet):

    def time_bucket(self, field: str, interval: str, annotations: Dict = None):
        """
        """
        if annotations:
            return self.all().values(bucket=TimeBucket(field, interval)).order_by('-bucket').annotate(**annotations)
        return self.all().values(bucket=TimeBucket(field, interval)).order_by('-bucket')
    
    def to_list(self, normalise_datetimes: bool = False):
        if normalise_datetimes:
            normalised = []
            for b in list(self):
                b["bucket"] = b["bucket"].isoformat()
                normalised.append(b)
            return normalised
        return list(self)
