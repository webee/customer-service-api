from flask_restplus import fields
from . import api


application = api.model('Application', {
    'name': fields.String(example='test', description='app name'),
    'title': fields.String(example='测试应用', description='app title'),
    'desc': fields.String(example='测试应用客服', description='app description'),
})
