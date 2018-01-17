from flask_restplus import fields
from . import api
from .xfields import Any, any_of

access_function = api.model('Access Function', {
    'name': fields.String(required=True, min_length=1, max_length=16, example='addRemark'),
    'label': fields.String(required=True, min_length=1, max_length=16, example='添加备注'),
})

label_info = api.model('Label Info', {
    'code': fields.String(required=True, min_length=1, example="1"),
    'name': fields.String(required=True, min_lenght=1, example="角色#1"),
    'alias_to': any_of(["string", "null"], required=False, example="a.b.c"),
    'children': fields.List(fields.Raw(title='Label Info'))
})

update_application_payload = api.model('Update Application Payload', {
    'appid': fields.String(),
    'appkey': fields.String(),
    'urls': any_of(['object']),
    'access_functions': fields.List(fields.Nested(access_function)),
    'staff_label_tree': fields.List(fields.Nested(label_info)),
    'configs': fields.Raw(example={})
})

application = api.model('Application', {
    'name': fields.String(example='test', description='app name'),
    'title': fields.String(example='测试应用', description='app title'),
    'desc': fields.String(example='测试应用客服', description='app description'),
    'access_functions': fields.List(fields.Nested(access_function)),
    'staff_label_tree': fields.Raw(),
    'configs': fields.Raw(),
    'updated': fields.Float(attribute=lambda x: x.updated.timestamp()),
})

path_label = api.model('Path Label', {
    'type': fields.String(required=True,
                          enum=['up', 'up+', 'super', 'self', 'self.', 'member', 'sub', 'self+', 'self++', 'member+',
                                'all']),
    'path': fields.String(required=True)
})

data_item = api.model('data item', {
    'label': fields.String(required=True, example='用户名', description='显示名称'),
    'type': Any(required=False, default='value', example='value', description='类型'),
    'value': Any(required=True, example='测试用户', description='值'),
})
