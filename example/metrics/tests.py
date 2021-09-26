from django.test import TestCase
from metrics.models import Metric
from datetime import datetime
import pandas as pd
import pytz


class TimeBucketTestCase(TestCase):
    def setUp(self):
        # Create sample data
        timestamps = pd.date_range(end = datetime.today(), periods = 100).to_pydatetime().tolist()
        for timestamp in timestamps:
            Metric.objects.create(time=pytz.utc.localize(timestamp))
    
    def test_time_bucket_offset(self):
        assert('INTERVAL' in str(Metric.timescale.filter(time__range=('2021-08-30', '2021-11-30')).time_bucket('time', "1 hour", offset="-1 hour").query))
        
        
