from flask_restplus import fields
from .xfields import Any
from . import api
from . import base_resource, raw_model, raw_specs
from .customer import customer
from .project_customers import project_customers, raw_project_customers
from .project_staffs import project_staffs, raw_project_staffs
from .project_domain_type import project_type


project = api.inherit('Project', base_resource, {
    'type': fields.Nested(project_type),
    'biz_id': fields.String(),
    'owner': fields.Nested(customer),
    'customers': fields.Nested(project_customers),
    'staffs': fields.Nested(project_staffs)
})


meta_data_item = api.model('meta data item', {
    'key': fields.String(required=True, min_length=1, max_length=32, example='username', description='名称'),
    'type': Any(required=False, example='value', description='类型'),
    'value': Any(required=True, example='测试用户', description='值'),
    'label': fields.String(required=True, example='用户名', description='显示名称'),
    'index': fields.Integer(required=False, example=1, description='显示次序'),
})


new_project = api.model('New Project', raw_specs({
    'domain': fields.String(required=True, min_length=1, max_length=32),
    'type': fields.String(required=True, min_length=1, max_length=32),
    'biz_id': fields.String(required=True, min_length=1, max_length=32),
    'start_msg_id': fields.Integer(required=False, min=0),
    'owner': fields.Nested(customer),
    'customers': fields.Nested(project_customers),
    'staffs': fields.Nested(project_staffs),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
}))


project_data = api.inherit('Project Data', {
    'id': fields.Integer(description='project id'),
    'biz_id': fields.String(),
    'is_online': fields.Boolean(),
    'owner': fields.Nested(customer),
    'customers': fields.Nested(raw_project_customers),
    'staffs': fields.Nested(raw_project_staffs),
    'meta_data': fields.List(fields.Nested(meta_data_item)),
})
