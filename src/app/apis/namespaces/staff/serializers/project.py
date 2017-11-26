from flask_restplus import fields
from app.apis import api


app_user = api.model('App User', {
    'uid': fields.String(),
    'name': fields.String(),
})

message = api.model('Message Result', {
    'channel': fields.String(),
    'user_type': fields.String(),
    'user_id': fields.String(),
    'msg_id': fields.Integer(),
    'domain': fields.String(),
    'type': fields.String(),
    'content': fields.String(),
    'ts': fields.Float(attribute=lambda msg: msg.ts.timestamp()),
    'session_id': fields.Integer(),
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

fetch_msgs_result = api.model('Fetch Msgs Result', {
    'msgs': fields.List(fields.Nested(message)),
    'has_more': fields.Boolean(description='is has more msgs?'),
})
