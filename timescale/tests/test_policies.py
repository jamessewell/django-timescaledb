"""
Tests for TimescaleDB retention and compression policies.
"""
from django.test import TestCase
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from metrics.models import Metric, AnotherMetricFromTimeScaleModel
from timescale.db.models.retention import RetentionPolicy
from timescale.db.models.compression import CompressionPolicy


class RetentionPolicyTests(TestCase):
    """Tests for TimescaleDB retention policies."""
    
    def setUp(self):
        """Set up test data."""
        # Create some test data
        self.timestamp = timezone.now()
        Metric.objects.create(
            time=self.timestamp - timedelta(days=30),
            temperature=10.0,
            device=1
        )
        Metric.objects.create(
            time=self.timestamp - timedelta(days=60),
            temperature=15.0,
            device=1
        )
        Metric.objects.create(
            time=self.timestamp - timedelta(days=90),
            temperature=20.0,
            device=1
        )
    
    def test_add_retention_policy(self):
        """Test adding a retention policy."""
        # Add a retention policy to drop data older than 60 days
        job_id = Metric.timescale.add_retention_policy(
            drop_after='60 days',
            if_not_exists=True
        )
        
        # Check that the job was created
        self.assertIsNotNone(job_id)
        
        # Check that the policy exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    def test_remove_retention_policy(self):
        """Test removing a retention policy."""
        # Add a retention policy
        job_id = Metric.timescale.add_retention_policy(
            drop_after='60 days',
            if_not_exists=True
        )
        
        # Remove the policy
        result = Metric.timescale.remove_retention_policy(if_exists=True)
        
        # Check that the policy was removed
        self.assertTrue(result)
        
        # Check that the policy no longer exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNone(result)


class CompressionPolicyTests(TestCase):
    """Tests for TimescaleDB compression policies."""
    
    def setUp(self):
        """Set up test data."""
        # Create some test data
        self.timestamp = timezone.now()
        Metric.objects.create(
            time=self.timestamp - timedelta(days=30),
            temperature=10.0,
            device=1
        )
        Metric.objects.create(
            time=self.timestamp - timedelta(days=60),
            temperature=15.0,
            device=1
        )
        Metric.objects.create(
            time=self.timestamp - timedelta(days=90),
            temperature=20.0,
            device=1
        )
    
    def test_enable_compression(self):
        """Test enabling compression on a hypertable."""
        # Enable compression
        result = Metric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Check that compression was enabled
        self.assertTrue(result)
        
        # Check that compression is enabled in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT compression_enabled FROM timescaledb_information.hypertables
                WHERE hypertable_name = 'metrics_metric'
            """)
            result = cursor.fetchone()
            self.assertTrue(result[0])
    
    def test_add_compression_policy(self):
        """Test adding a compression policy."""
        # Enable compression first
        Metric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Add a compression policy to compress data older than 30 days
        job_id = Metric.timescale.add_compression_policy(
            compress_after='30 days',
            if_not_exists=True
        )
        
        # Check that the job was created
        self.assertIsNotNone(job_id)
        
        # Check that the policy exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    def test_remove_compression_policy(self):
        """Test removing a compression policy."""
        # Enable compression first
        Metric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Add a compression policy
        job_id = Metric.timescale.add_compression_policy(
            compress_after='30 days',
            if_not_exists=True
        )
        
        # Remove the policy
        result = Metric.timescale.remove_compression_policy(if_exists=True)
        
        # Check that the policy was removed
        self.assertTrue(result)
        
        # Check that the policy no longer exists in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM timescaledb_information.jobs
                WHERE job_id = %s
            """, [job_id])
            result = cursor.fetchone()
            self.assertIsNone(result)
    
    def test_get_compression_stats(self):
        """Test getting compression statistics."""
        # Enable compression
        Metric.timescale.enable_compression(
            compress_orderby=['time'],
            if_not_exists=True
        )
        
        # Get compression stats
        stats = Metric.timescale.get_compression_stats()
        
        # Check that stats were returned
        self.assertIsInstance(stats, list)
        
        # There should be at least one row for our hypertable
        self.assertTrue(len(stats) > 0)
