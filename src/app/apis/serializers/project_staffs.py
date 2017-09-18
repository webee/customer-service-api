from flask_restplus import fields
from . import api
from . import base_resource, raw_model
from .staff import staff


_project_staffs_specs = {
    'leader': fields.Nested(staff),
    'assistants': fields.List(fields.Nested(staff)),
    'participants': fields.List(fields.Nested(staff))
}
project_staffs = api.inherit('Project Staffs', base_resource, _project_staffs_specs)
raw_project_staffs = raw_model(project_staffs)
