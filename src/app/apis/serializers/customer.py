from flask_restplus import fields
from . import api
from . import pagination, base_resource


_raw_customer_specs = {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_001'),
    'name': fields.String(required=False, min_length=1, max_length=16, example='测试客户#1')
}

raw_customer = api.model('Raw Customer', _raw_customer_specs)
customer = api.inherit('Customer', base_resource, _raw_customer_specs)
page_of_customers = api.inherit('Page of customers', pagination, {
    'items': fields.List(fields.Nested(customer))
})
