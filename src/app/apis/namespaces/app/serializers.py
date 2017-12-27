from flask_restplus import fields
from app.apis import api
from app.apis.serializers.xfields import any_of
from app.apis.serializers import resource_id

new_project_result = api.inherit('new project result', resource_id, {
    'xchat_chat_id': fields.String(attribute='xchat.chat_id', description='project xchat chat id'),
})

new_channel_message = api.model('New Channel Message', {
    'channel': fields.String(required=True),
    'project_domain': fields.String(required=False),
    'project_type': fields.String(required=False),
    'biz_id': fields.String(required=False),
    'project_id': fields.Integer(required=False),
    'uid': fields.String(required=True),
    'type': fields.String(required=True, enum=('text', 'file', 'image', 'voice')),
    'content': any_of(['string', 'object'], required=True)
})

project_current_session_info = api.model('Project Current Session Info', {
    'id': fields.Integer(),
    'handler': fields.String(attribute='handler.uid', help="handler's staff uid"),
    'msg_id': fields.Integer(),
    'sync_msg_id': fields.Integer(),
    'handler_msg_id': fields.Integer(),
})

try_handle_project_result = api.model('Try Handle Project Result', {
    'domain': fields.String(),
    'type': fields.String(),
    'id': fields.Integer(),
    'current_session_id': fields.Integer()
})
