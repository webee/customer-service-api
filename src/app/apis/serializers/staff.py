from flask_restplus import fields
from app import ma
from . import api
from .app import path_label


_raw_staff_specs = {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_01'),
    'name': fields.String(required=False, min_length=1, max_length=16, example='测试客服#1')
}

raw_staff = api.model('Raw Staff', {
    'uid': fields.String(),
    'name': fields.String(),
    'is_online': fields.Boolean(required=False, readonly=True),
})

new_staff = api.model('New Staff', {
    'uid': fields.String(required=True, min_length=1, max_length=32, example='test_01'),
    'name': fields.String(required=False, min_length=1, max_length=16, example='测试客服#1'),
    'context_labels': fields.List(fields.Nested(path_label))
})


class RawStaffSchema(ma.Schema):
    class Meta:
        fields = ("uid", "name", "is_online")
