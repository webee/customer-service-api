from flask_restplus import fields


class Any(fields.Raw):
    __schema_type__ = ["array", "boolean", "integer", "null", "number", "object", "string"]


def any_of(types, *args, **kwargs):
    class AnyOfType(fields.Raw):
        __schema_type__ = list(types)

    return AnyOfType(*args, **kwargs)
