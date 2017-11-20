from flask_restplus import fields
from app.apis import api
from .session import message


app_user = api.model('App User', {
    'uid': fields.String(),
    'name': fields.String(),
})


handling_session_item = api.model('Handling Session Item', {
    'id': fields.Integer(description='session id'),
    'proj_id': fields.Integer(attribute=lambda s: s.project.id),
    'is_online': fields.Boolean(attribute=lambda s: s.project.is_online),
    'owner': fields.Nested(app_user, attribute=lambda s: s.project.owner),
    'msg_id': fields.Integer(description='last msg id'),
    'msg': fields.Nested(message, allow_null=True, description='last msg'),
    'sync_msg_id': fields.Integer(),
})
