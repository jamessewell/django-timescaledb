from django.db import models
from timescale.db.models.querysets import *
from typing import Optional, Union, List, Dict, Any
from datetime import datetime, timedelta


class TimescaleManager(models.Manager):
    """
    A custom model manager specifically designed around the Timescale
    functions and tooling that has been ported to Django's ORM.
    """

    def get_queryset(self):
        return TimescaleQuerySet(self.model, using=self._db)

    def time_bucket(self, field, interval):
        return self.get_queryset().time_bucket(field, interval)

    def time_bucket_ng(self, field, interval):
        return self.get_queryset().time_bucket_ng(field, interval)

    def time_bucket_gapfill(self, field: str, interval: str, start: datetime, end: datetime, datapoints: Optional[int] = None):
        return self.get_queryset().time_bucket_gapfill(field, interval, start, end, datapoints)

    def histogram(self, field: str, min_value: float, max_value: float, num_of_buckets: int = 5):
        return self.get_queryset().histogram(field, min_value, max_value, num_of_buckets)

    def lttb(self, time: str, value: str, num_of_counts: int = 20):
        return self.get_queryset().lttb(time, value, num_of_counts)

    # Retention Policy Methods
    def add_retention_policy(
        self,
        drop_after: Union[str, int, timedelta],
        schedule_interval: Optional[Union[str, timedelta]] = None,
        if_not_exists: bool = False,
        drop_created_before: Optional[Union[str, timedelta]] = None,
        initial_start: Optional[datetime] = None,
        timezone: Optional[str] = None
    ) -> int:
        """
        Add a retention policy to automatically remove old data from the hypertable.

        Args:
            drop_after: Chunks older than this interval will be dropped
            schedule_interval: The interval between policy executions
            if_not_exists: If True, don't error if policy already exists
            drop_created_before: Alternative to drop_after, drops chunks created before this interval
            initial_start: Time the policy is first run
            timezone: Timezone for the policy

        Returns:
            The job ID of the created policy
        """
        from timescale.db.models.retention import RetentionPolicy
        return RetentionPolicy.add_retention_policy(
            self.model,
            drop_after=drop_after,
            schedule_interval=schedule_interval,
            if_not_exists=if_not_exists,
            drop_created_before=drop_created_before,
            initial_start=initial_start,
            timezone=timezone
        )

    def remove_retention_policy(self, if_exists: bool = False) -> bool:
        """
        Remove a retention policy from the hypertable.

        Args:
            if_exists: If True, don't error if policy doesn't exist

        Returns:
            True if the policy was removed, False otherwise
        """
        from timescale.db.models.retention import RetentionPolicy
        return RetentionPolicy.remove_retention_policy(self.model, if_exists=if_exists)

    # Compression Policy Methods
    def add_compression_policy(
        self,
        compress_after: Union[str, int, timedelta],
        schedule_interval: Optional[Union[str, timedelta]] = None,
        if_not_exists: bool = False,
        compress_created_before: Optional[Union[str, timedelta]] = None,
        initial_start: Optional[datetime] = None,
        timezone: Optional[str] = None
    ) -> int:
        """
        Add a compression policy to automatically compress chunks in the hypertable.

        Args:
            compress_after: Chunks older than this interval will be compressed
            schedule_interval: The interval between policy executions
            if_not_exists: If True, don't error if policy already exists
            compress_created_before: Alternative to compress_after, compresses chunks created before this interval
            initial_start: Time the policy is first run
            timezone: Timezone for the policy

        Returns:
            The job ID of the created policy
        """
        from timescale.db.models.compression import CompressionPolicy
        return CompressionPolicy.add_compression_policy(
            self.model,
            compress_after=compress_after,
            schedule_interval=schedule_interval,
            if_not_exists=if_not_exists,
            compress_created_before=compress_created_before,
            initial_start=initial_start,
            timezone=timezone
        )

    def remove_compression_policy(self, if_exists: bool = False) -> bool:
        """
        Remove a compression policy from the hypertable.

        Args:
            if_exists: If True, don't error if policy doesn't exist

        Returns:
            True if the policy was removed, False otherwise
        """
        from timescale.db.models.compression import CompressionPolicy
        return CompressionPolicy.remove_compression_policy(self.model, if_exists=if_exists)

    def enable_compression(
        self,
        compress_segmentby: Optional[List[str]] = None,
        compress_orderby: Optional[List[str]] = None,
        compress_chunk_time_interval: Optional[Union[str, timedelta]] = None,
        if_not_exists: bool = False
    ) -> bool:
        """
        Enable compression on the hypertable.

        Args:
            compress_segmentby: List of columns to segment by
            compress_orderby: List of columns to order by
            compress_chunk_time_interval: Time interval for compression chunks
            if_not_exists: If True, don't error if compression is already enabled

        Returns:
            True if compression was enabled, False otherwise
        """
        from timescale.db.models.compression import CompressionPolicy
        return CompressionPolicy.enable_compression(
            self.model,
            compress_segmentby=compress_segmentby,
            compress_orderby=compress_orderby,
            compress_chunk_time_interval=compress_chunk_time_interval,
            if_not_exists=if_not_exists
        )

    def get_compression_stats(self) -> List[Dict[str, Any]]:
        """
        Get compression statistics for the hypertable.

        Returns:
            A list of dictionaries containing compression statistics
        """
        from timescale.db.models.compression import CompressionPolicy
        return CompressionPolicy.get_compression_stats(self.model)
