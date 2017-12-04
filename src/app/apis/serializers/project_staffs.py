from flask_restplus import fields
from app import ma
from . import api
from . import base_resource, raw_model
from .staff import staff, RawStaffSchema


_project_staffs_specs = {
    'leader': fields.Nested(staff),
    'assistants': fields.List(fields.Nested(staff)),
    'participants': fields.List(fields.Nested(staff))
}
project_staffs = api.inherit('Project Staffs', base_resource, _project_staffs_specs)
raw_project_staffs = raw_model(project_staffs)


class RawProjectStaffsSchema(ma.Schema):
    class Meta:
        fields = ("leader", "assistants", "participants")

    leader = ma.Nested(RawStaffSchema)
    assistants = ma.List(ma.Nested(RawStaffSchema))
    participants = ma.List(ma.Nested(RawStaffSchema))
