from flask_restplus import fields
from app import ma
from . import api
from . import base_resource, resource_id
from .app import path_label, meta_data_item
from .staff import raw_staff, RawStaffSchema
from .customer import raw_customer, RawCustomerSchema

project = api.inherit('Project', resource_id, {
    'domain': fields.String(),
    'type': fields.String(),
    'biz_id': fields.String(),
    'tags': fields.List(fields.String),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer))
})


new_project = api.model('New Project', {
    'domain': fields.String(required=True, min_length=1, max_length=32),
    'type': fields.String(required=True, min_length=1, max_length=32),
    'biz_id': fields.String(required=True, min_length=1, max_length=32),
    'tags': fields.List(fields.String, default=[]),
    'start_msg_id': fields.Integer(required=False, min=0),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
    'scope_labels': fields.List(fields.Nested(path_label)),
    'class_labels': fields.List(fields.Nested(path_label))
})

update_project = api.model('Update Project', {
    'id': fields.Integer(),
    'domain': fields.String(),
    'type': fields.String(),
    'biz_id': fields.String(),
    'tags': fields.List(fields.String, default=[]),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
    'scope_labels': fields.List(fields.Nested(path_label)),
    'class_labels': fields.List(fields.Nested(path_label))
})

update_project_payload = api.model('Update Project Payload', {
    'tags': fields.List(fields.String, default=[]),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
    'scope_labels': fields.List(fields.Nested(path_label)),
    'class_labels': fields.List(fields.Nested(path_label))
})

project_data = api.model('Project Data', {
    'id': fields.Integer(description='project id'),
    'biz_id': fields.String(),
    'is_online': fields.Boolean(),
    'tags': fields.List(fields.String),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
})


class ProjectDataSchema(ma.Schema):
    class Meta:
        fields = ("id", "biz_id", "is_online", "tags", "owner", "leader", "customers", "meta_data")

    owner = ma.Nested(RawCustomerSchema)
    leader = ma.Nested(RawStaffSchema)
    customers = ma.List(ma.Nested(RawCustomerSchema))


project_data_schema = ProjectDataSchema()
