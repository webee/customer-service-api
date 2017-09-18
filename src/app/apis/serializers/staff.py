from flask_restplus import fields
from . import api
from . import pagination, base_resource


_raw_staff_specs = {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_01'),
    'name': fields.String(required=True, min_length=1, max_length=16, example='测试客服#1')
}

staff = api.inherit('Staff', base_resource, _raw_staff_specs)
page_of_staffs = api.inherit('Page of staffs', pagination, {
    'items': fields.List(fields.Nested(staff))
})
