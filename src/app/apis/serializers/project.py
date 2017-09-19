from flask_restplus import fields
from . import api
from . import base_resource, raw_model, raw_specs
from .project_customers import project_customers
from .project_staffs import project_staffs
from .project_domain_type import project_type


_project_specs = {
    'type': fields.Nested(project_type),
    'biz_id': fields.String(),
    'customers': fields.Nested(project_customers),
    'staffs': fields.Nested(project_staffs)
}
project = api.inherit('Project', base_resource, _project_specs)


_new_project_specs = raw_specs({
    'domain': fields.String(required=True, min_length=1, max_length=32),
    'type': fields.String(required=True, min_length=1, max_length=32),
    'biz_id': fields.String(required=True, min_length=1, max_length=32),
    'customers': fields.Nested(project_customers),
    'staffs': fields.Nested(project_staffs)
})

new_project = api.model('New Project', _new_project_specs)
