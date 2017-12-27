from flask_restplus import fields
from app.apis import api
from app.apis.serializers.staff import raw_staff
from app.apis.serializers.app import application, access_function
from app.apis.serializers.xfields import any_of

staff_app_info = api.model('Staff App Info', {
    'staff': fields.Nested(raw_staff),
    'app': fields.Nested(application),
    'project_domains': any_of(['array']),
    'staffs': fields.List(fields.Nested(raw_staff))
})
