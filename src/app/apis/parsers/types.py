from collections import namedtuple
import json

_ContextLabel = namedtuple('ContextLabel', ['path', 'uids'])


class ContextLabel(object):
    def __call__(self, value):
        try:
            context_label = json.loads(value)
            path = context_label['path']
            uids = context_label['uids']
            if isinstance(path, str) and isinstance(uids, list):
                return _ContextLabel(path, uids)
        except:
            pass
        raise ValueError('invalid context label')

    @property
    def __schema__(self):
        return {'type': 'string', 'format': 'ContextLabel'}
