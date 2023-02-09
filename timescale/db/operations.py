from django.contrib.postgres.operations import CreateExtension


class TimescaleExtension(CreateExtension):
    def __init__(self):
        self.name = "timescaledb"