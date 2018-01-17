import arrow
from collections import namedtuple

_ContextLabel = namedtuple('ContextLabel', ['path', 'uids'])


class ContextLabel(object):
    def __call__(self, value):
        try:
            if not value:
                return None
            parts = value.split(',')
            if len(parts) == 1:
                return _ContextLabel(parts[0], [])

            if len(parts) == 2:
                path = parts[0]
                uids = parts[1].split('|') if parts[1] else []
                return _ContextLabel(path, uids)

            raise ValueError('invalid context label')
        except:
            pass
        raise ValueError('invalid context label')

    @property
    def __schema__(self):
        return {'type': 'string', 'format': 'ContextLabel'}


_Range = namedtuple('Range', ['start', 'end'])


class DateTimeRange(object):
    def __call__(self, value: str):
        try:
            parts = value.split(',')
            if len(parts) != 2:
                return _Range(None, None)
            start, end = [arrow.get(float(val)).datetime if val else None for val in parts]
            return _Range(start, end)
        except:
            pass
        raise ValueError('invalid datetime range')

    @property
    def __schema__(self):
        return {'type': 'string', 'format': 'DateTimeRange'}


class NumberRange(object):
    def __init__(self, transformer=float):
        self.transformer = transformer

    def __call__(self, value: str):
        try:
            parts = value.split(',')
            if len(parts) != 2:
                return _Range(None, None)
            start, end = [self.transformer(float(val)) if val else None for val in parts]
            return _Range(start, end)
        except:
            pass
        raise ValueError('invalid number range')

    @property
    def __schema__(self):
        return {'type': 'string', 'format': 'NumberRange'}
