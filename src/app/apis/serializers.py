from flask_restplus import fields
from . import api


pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

resource_id = api.model('resource id', {
    'id': fields.Integer(readonly=True, description='resource id')
})


base_resource = api.inherit('resource base', resource_id, {
    'created': fields.DateTime(readonly=True),
    'updated': fields.DateTime(readonly=True)
})
