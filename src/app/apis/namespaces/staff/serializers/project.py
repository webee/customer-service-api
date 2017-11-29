from flask_restplus import fields
from app.apis import api
from app.apis.serializers.project import project_data


app_user = api.model('App User', {
    'uid': fields.String(),
    'name': fields.String(),
})

message = api.model('Message Result', {
    'channel': fields.String(),
    'user_type': fields.String(),
    'user_id': fields.String(),
    'tx_key': fields.Integer(),
    'rx_key': fields.Integer(),
    'msg_id': fields.Integer(),
    'domain': fields.String(),
    'type': fields.String(),
    'content': fields.String(),
    'ts': fields.Float(attribute=lambda msg: msg.ts.timestamp()),
    'session_id': fields.Integer(),
})

session_item = api.model('Session Item', {
    'id': fields.Integer(description='session id'),
    'project': fields.Nested(project_data),
    'msg_id': fields.Integer(description='last msg id'),
    'msg': fields.Nested(message, allow_null=True, description='last msg'),
    'msg_ts': fields.Float(attribute=lambda s: s.msg_ts.timestamp()),
    'sync_msg_id': fields.Integer(),
})

fetch_msgs_result = api.model('Fetch Msgs Result', {
    'msgs': fields.List(fields.Nested(message)),
    'has_more': fields.Boolean(description='is has more msgs?'),
})
