from flask_restplus import fields
from app import ma
from . import api
from .app import meta_data_item

raw_customer = api.model('Raw Customer', {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_001'),
    'name': fields.String(required=False, min_length=1, max_length=16, example='测试客户#1'),
    'mobile': fields.String(required=False, min_length=1, max_length=16, example='18812345678'),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
})


class RawCustomerSchema(ma.Schema):
    class Meta:
        fields = ("uid", "name", "mobile", "meta_data")


raw_customer_schema = RawCustomerSchema()
