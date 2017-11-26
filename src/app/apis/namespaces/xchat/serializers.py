from flask_restplus import fields
from app.apis import api


notified_event = api.model('notified event', {
    'event': fields.String(required=True, example='msg', description='notify event name'),
    # 'data': fields.Raw(required=True),
})


notified_msg = api.model('notified msg', {
    'kind': fields.String(required=True, enum=('chat', 'chat_notify'), example='chat', description='msg kind'),
    'chat_id': fields.String(required=True, example='group.1', description='msg kind'),
    'user': fields.String(required=True, example='cs:test:customer:u#001', description='xchat chat member uid'),
    'id': fields.Integer(required=False, min=1, description='msg id'),
    'msg': fields.String(required=True, description='msg content'),
    'ts': fields.Integer(required=True, description='msg timestamp(unit: s)'),
    'domain': fields.String(required=False, example='cs', description='msg domain'),
})


user_status = api.model('user status', {
    'user': fields.String(required=True),
    'status': fields.String(required=True, enum=('online', 'offline')),
})

notified_user_status = api.model('notified user status', {
    'statuses': fields.List(fields.Nested(user_status), required=True),
})
