from functools import wraps
from flask_restplus.utils import merge


def add_response_doc(func, fields, as_list, code=200, description=None, **kwargs):
    doc = {
        'responses': {
            code: (description, [fields]) if as_list else (description, fields)
        },
        '__mask__': kwargs.get('mask', True),  # Mask values can't be determined outside app context
    }
    func.__apidoc__ = merge(getattr(func, '__apidoc__', {}), doc)

    return func


def response_with(fields, as_list=False, code=200, description=None, **kwargs):
    '''
    !!DOC ONLY
    A decorator specifying the fields to use for serialization.

    :param bool as_list: Indicate that the return type is a list (for the documentation)
    :param int code: Optionally give the expected HTTP response code if its different from 200

    '''
    def wrapper(func):
        return add_response_doc(func, fields, as_list, code, description, **kwargs)

    return wrapper


def response_list_with(fields, **kwargs):
    '''
    !!DOC ONLY
    A shortcut decorator for :meth:`~Api.marshal_with` with ``as_list=True``'''
    return response_with(fields, True, **kwargs)


def marshal_with(schema, response_fields=None, as_list=False):
    def wrapper(func):
        if response_fields:
            func = add_response_doc(func, response_fields, as_list)

        @wraps(func)
        def _wrapper(*args, **kwargs):
            return schema.jsonify(func(*args, **kwargs), many=as_list)
        return _wrapper

    return wrapper


def marshal_list_with(schema, response_fields=None):
    return marshal_with(schema, response_fields, as_list=True)
