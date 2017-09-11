from flask_restplus import fields
from .. import api, raw_model
from ..serializers import pagination, base_resource


# customer
_raw_customer_specs = {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_001'),
    'name': fields.String(required=True, min_length=1, max_length=16, example='测试客户#1')
}

customer = api.inherit('Customer', base_resource, _raw_customer_specs)
page_of_customers = api.inherit('Page of customers', pagination, {
    'items': fields.List(fields.Nested(customer))
})


# staff
_raw_staff_specs = {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_01'),
    'name': fields.String(required=True, min_length=1, max_length=16, example='测试客服#1')
}

staff = api.inherit('Staff', base_resource, _raw_staff_specs)
page_of_staffs = api.inherit('Page of staffs', pagination, {
    'items': fields.List(fields.Nested(staff))
})


# project customers
_project_customers_specs = {
    'parties': fields.List(fields.Nested(customer))
}
project_customers = api.inherit('Project Customers', base_resource, _project_customers_specs)
raw_project_customers = raw_model(project_customers)


# project staffs
_project_staffs_specs = {
    'leader': fields.Nested(staff),
    'assistants': fields.List(fields.Nested(staff)),
    'participants': fields.List(fields.Nested(staff))
}
project_staffs = api.inherit('Project Staffs', base_resource, _project_staffs_specs)
raw_project_staffs = raw_model(project_staffs)


# project domain
_project_domain_specs = {
    'name': fields.String(required=True, min_length=1, max_length=32),
    'desc': fields.String(required=True, min_length=1, max_length=64),
}
project_domain = api.inherit('Project Domain', base_resource, _project_domain_specs)


# project type
_project_type_specs = {
    'domain': fields.Nested(project_domain),
    'name': fields.String(required=True, min_length=1, max_length=32),
    'desc': fields.String(required=True, min_length=1, max_length=64),
}
project_type = api.inherit('Project Type', base_resource, _project_type_specs)


# project
_raw_project_specs = {
    'domain': fields.String(required=True, min_length=1, max_length=32),
    'type': fields.String(required=True, min_length=1, max_length=32),
    'biz_id': fields.String(required=True, min_length=1, max_length=32),
    'customers': fields.Nested(raw_model(project_customers)),
    'staffs': fields.Nested(raw_model(project_staffs))
}

_project_specs = {
    'type': fields.Nested(project_type),
    'biz_id': fields.String(),
    'customers': fields.Nested(project_customers),
    'staffs': fields.Nested(project_staffs)
}
project = api.inherit('Project', base_resource, _project_specs)
raw_project = api.model('Raw Project', _raw_project_specs)
