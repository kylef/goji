from datetime import datetime

from click import ParamType


class Datetime(ParamType):
    name = 'date'

    def __init__(self, format: str):
        self.format = format

    def convert(self, value, param, ctx):
        if value is None or isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(value, self.format)
        except ValueError as e:
            self.fail(
                'Could not parse datetime string "{datetime_str}" formatted as {format} ({ex})'.format(
                    datetime_str=value,
                    format=self.format,
                    ex=e,
                ),
                param,
                ctx,
            )
