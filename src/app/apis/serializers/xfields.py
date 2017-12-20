from flask_restplus import fields


class Any(fields.Raw):
    __schema_type__ = ["array", "boolean", "integer", "null", "number", "object", "string"]
    #: The JSON/Swagger schema format
    __schema_format__ = None
    #: An optional JSON/Swagger schema example
    __schema_example__ = "any_of(%s)" % ', '.join(__schema_type__)


def any_of(types, *args, **kwargs):
    class AnyOfType(fields.Raw):
        __schema_type__ = list(types)
        __schema_example__ = "any_of(%s)" % ', '.join(__schema_type__)

    return AnyOfType(*args, **kwargs)
