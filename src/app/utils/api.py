from functools import wraps
from schema import SchemaError
from flask import request, _request_ctx_stack
from werkzeug.local import LocalProxy
from app.errors import BadRequestError


current_data = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_data', None))


def _require_data(schema=None):
    data = request.get_json()
    if data is None:
        raise BadRequestError(details='need json data')

    if schema:
        try:
            data = schema.validate(data)
        except SchemaError as e:
            raise BadRequestError(details=e.code)

    _request_ctx_stack.top.current_data = data


def require_data(schema=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _require_data(schema)
            return fn(*args, **kwargs)
        return decorator
    return wrapper
