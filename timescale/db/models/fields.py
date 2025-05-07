from django.db.models import DateTimeField


class TimescaleDateTimeField(DateTimeField):
    def __init__(self, *args, interval, retain_primary_key=False, **kwargs):
        self.interval = interval
        self.retain_primary_key = retain_primary_key
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.update({
            'interval': self.interval,
            'retain_primary_key': self.retain_primary_key,
        })
        return name, path, args, kwargs