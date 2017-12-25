from flask_restplus import fields
from app import ma
from . import api
from .app import data_item

raw_customer = api.model('Raw Customer', {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_001'),
    'name': fields.String(required=False, max_length=100, default='', example='测试客户#1'),
    'mobile': fields.String(required=False, max_length=16, default='', example='18812345678'),
    'meta_data': fields.List(fields.Nested(data_item)),
    'is_online': fields.Boolean(required=False, readonly=True),
})


class RawCustomerSchema(ma.Schema):
    class Meta:
        fields = ("uid", "name", "mobile", "meta_data", 'is_online')


raw_customer_schema = RawCustomerSchema()
