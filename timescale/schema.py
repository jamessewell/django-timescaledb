from django.contrib.gis.db.backends.postgis.schema import PostGISSchemaEditor

from timescale.fields import TimescaleDateTimeField


class TimescaleSchemaEditor(PostGISSchemaEditor):
    sql_add_hypertable = (
        "SELECT create_hypertable("
        "{table}, {partition_column}, "
        "chunk_time_interval => interval {interval})"
    )

    sql_drop_primary_key = (
        'ALTER TABLE {table} '
        'DROP CONSTRAINT {pkey}'
    )

    def drop_primary_key(self, model):
        """
        Hypertables can't partition if the primary key is not
        the partition column.
        So we drop the mandatory primary key django creates.
        """
        db_table = model._meta.db_table
        table = self.quote_name(db_table)
        pkey = self.quote_name(f'{db_table}_pkey')

        sql = self.sql_drop_primary_key.format(table=table, pkey=pkey)

        self.execute(sql)

    def create_hypertable(self, model, field):
        """
        Create the hypertable with the partition column being the field.
        """
        partition_column = self.quote_value(field.column)
        interval = self.quote_value(field.interval)
        table = self.quote_value(model._meta.db_table)

        sql = self.sql_add_hypertable.format(
            table=table, partition_column=partition_column, interval=interval
        )

        self.execute(sql)

    def create_model(self, model):
        super().create_model(model)

        for field in model._meta.local_fields:
            if not isinstance(field, TimescaleDateTimeField):
                continue

            self.drop_primary_key(model)
            self.create_hypertable(model, field)
