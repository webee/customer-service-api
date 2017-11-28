from flask_restplus import fields
from app.apis import api
from app.apis.serializers.project_domain_type import raw_project_domain_tree
from app.apis.serializers.staff import raw_staff
from app.apis.serializers.app import application


_staff_app_info_specs = {
    'staff': fields.Nested(raw_staff, attribute=lambda staff: staff),
    'app': fields.Nested(application),
    'project_domain_tree': fields.List(fields.Nested(raw_project_domain_tree), attribute="app.ordered_project_domains")
}

staff_app_info = api.model('Staff App Info', _staff_app_info_specs)
