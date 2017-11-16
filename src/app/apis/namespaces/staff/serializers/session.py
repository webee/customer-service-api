from flask_restplus import fields
from app.apis import api


_new_message = {
    'domain': fields.String(default='', required=False, min_length=0, max_length=16),
    'type': fields.String(default='', required=False, min_length=0, max_length=24),
    'content': fields.String(required=True, min_length=1, max_length=64*1024),
}

new_message = api.model('New Message', _new_message)


message = api.model('Message Result', {
    'channel': fields.String(),
    'user_type': fields.String(),
    'user_id': fields.String(),
    'msg_id': fields.Integer(),
    'domain': fields.String(),
    'type': fields.String(),
    'content': fields.String(),
    'ts': fields.Float(attribute=lambda msg: msg.ts.timestamp()),
})

fetch_msgs_result = api.model('Fetch Msgs Result', {
    'msgs': fields.List(fields.Nested(message)),
    'has_more': fields.Boolean(description='is has more msgs?'),
})
