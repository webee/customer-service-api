from flask_restplus import fields


class Any(fields.Raw):
    __schema_type__ = ["array", "boolean", "integer", "null", "number", "object", "string"]
