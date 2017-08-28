from flask_restplus import fields
from .api import api
from ..serializers import pagination, base_resource

# customer
_raw_customer_specs = {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_001'),
    'name': fields.String(required=True, min_length=1, max_length=16, example='测试客户#1')
}

raw_customer = api.model('Raw Customer', _raw_customer_specs)
customer = api.inherit('Customer', base_resource, _raw_customer_specs)
page_of_customers = api.inherit('Page of customers', pagination, {
    'items': fields.List(fields.Nested(customer))
})

# staff
_raw_staff_specs = {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_01'),
    'name': fields.String(required=True, min_length=1, max_length=16, example='测试客服#1')
}

raw_staff = api.model('Raw Staff', _raw_staff_specs)
staff = api.inherit('Staff', base_resource, _raw_staff_specs)
page_of_staffs = api.inherit('Page of staffs', pagination, {
    'items': fields.List(fields.Nested(staff))
})

# project customers
_raw_project_customers = {
    'parties': fields.List(fields.Nested(raw_customer))
}

raw_project_customers = api.model('Raw Project Customers', _raw_project_customers)
project_customers = api.inherit('Project Customers', base_resource, _raw_project_customers)

# project staffs
_raw_project_staffs = {
    'leader': fields.Nested(raw_staff),
    'assistants': fields.List(fields.Nested(raw_staff)),
    'participants': fields.List(fields.Nested(raw_staff))
}

raw_project_staffs = api.model('Raw Project Staffs', _raw_project_staffs)
project_staffs = api.inherit('Project Staffs', base_resource, _raw_project_staffs)

# project
_raw_project = {
    'domain': fields.String(required=True, min_length=1, max_length=32, example='test'),
    'type': fields.String(required=True, min_length=1, max_length=32, example='test'),
    'biz_id': fields.String(required=True, min_length=1, max_length=32, example='biz#0001'),
    'customers': fields.Nested(raw_project_customers),
    'staffs': fields.Nested(raw_project_staffs),
}

raw_project = api.model('Raw Project', _raw_project)
