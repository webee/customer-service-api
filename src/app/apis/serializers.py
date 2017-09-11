from flask_restplus import fields
from . import api


# 分页结果
pagination = api.model('A Page of Results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

# 资源id
resource_id = api.model('Resource ID', {
    'id': fields.Integer(readonly=True, description='resource id')
})


# 资源基本信息id, created, updated
base_resource = api.inherit('Resource Base', resource_id, {
    'created': fields.DateTime(readonly=True, descrption='created time'),
    'updated': fields.DateTime(readonly=True, description='updated time')
})
