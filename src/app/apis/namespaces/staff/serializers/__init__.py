from flask_restplus import fields
from app.apis import api
from app.apis.serializers.app import application
from app.apis.serializers.xfields import any_of
from .staff import staff_data

staff_app_info = api.model('Staff App Info', {
    'staff': fields.Nested(staff_data),
    'app': fields.Nested(application),
    'project_domains': any_of(['array']),
    'staffs': fields.List(fields.Nested(staff_data))
})
