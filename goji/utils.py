from click import ParamType
from datetime import datetime


class Datetime(ParamType):
    name = 'date'

    def __init__(self, format):
        self.format = format

    def convert(self, value, param, ctx):
        if value is None or isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(value, self.format)
        except ValueError as e:
            self.fail('Could not parse datetime string "{datetime_str}" formatted as {format} ({ex})'.format(
                datetime_str=value, format=self.format, ex=e,), param, ctx)
