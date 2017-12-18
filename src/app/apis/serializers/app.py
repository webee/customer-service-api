from flask_restplus import fields
from . import api
from .xfields import Any

application = api.model('Application', {
    'name': fields.String(example='test', description='app name'),
    'title': fields.String(example='测试应用', description='app title'),
    'desc': fields.String(example='测试应用客服', description='app description'),
})

path_label = api.model('Path Label', {
    'type': fields.String(required=True, enum=['super', 'self', 'sub', 'all']),
    'path': fields.String(required=True)
})


meta_data_item = api.model('meta data item', {
    'label': fields.String(required=True, example='用户名', description='显示名称'),
    'type': Any(required=False, default='value', example='value', description='类型'),
    'value': Any(required=True, example='测试用户', description='值'),
})
