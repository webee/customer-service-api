from flask_restplus import fields
from app import ma
from .xfields import Any
from . import api
from . import base_resource, raw_specs
from .staff import staff, raw_staff, RawStaffSchema
from .customer import raw_customer, customer, RawCustomerSchema
from .project_domain_type import project_type


project = api.inherit('Project', base_resource, {
    'type': fields.Nested(project_type),
    'biz_id': fields.String(),
    'owner': fields.Nested(customer),
    'leader': fields.Nested(staff),
    'customers': fields.List(fields.Nested(customer))
})


meta_data_item = api.model('meta data item', {
    'key': fields.String(required=True, min_length=1, max_length=32, example='username', description='名称'),
    'type': Any(required=False, example='value', description='类型'),
    'value': Any(required=True, example='测试用户', description='值'),
    'label': fields.String(required=True, example='用户名', description='显示名称'),
    'index': fields.Integer(required=False, example=1, description='显示次序'),
})


class MetaDataItemSchema(ma.Schema):
    class Meta:
        fields = ("key", "type", "value", "label", "index")


new_project = api.model('New Project', raw_specs({
    'domain': fields.String(required=True, min_length=1, max_length=32),
    'type': fields.String(required=True, min_length=1, max_length=32),
    'biz_id': fields.String(required=True, min_length=1, max_length=32),
    'start_msg_id': fields.Integer(required=False, min=0),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
    # 'scope_labels': fields.List(fields.Nested)
}))


project_data = api.model('Project Data', {
    'id': fields.Integer(description='project id'),
    'biz_id': fields.String(),
    'is_online': fields.Boolean(),
    'owner': fields.Nested(raw_customer),
    'leader': fields.Nested(raw_staff),
    'customers': fields.List(fields.Nested(raw_customer)),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
})


class ProjectDataSchema(ma.Schema):
    class Meta:
        fields = ("id", "biz_id", "is_online", "owner", "leader", "customers", "meta_data")

    owner = ma.Nested(RawCustomerSchema)
    leader = ma.Nested(RawStaffSchema)
    customers = ma.List(ma.Nested(RawCustomerSchema))
    meta_data = ma.List(ma.Nested(MetaDataItemSchema))


project_data_schema = ProjectDataSchema()
