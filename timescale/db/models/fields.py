from django.db.models import DateTimeField


class TimescaleDateTimeField(DateTimeField):
    def __init__(self, *args, interval, **kwargs):
        self.interval = interval
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['interval'] = self.interval

        return name, path, args, kwargs