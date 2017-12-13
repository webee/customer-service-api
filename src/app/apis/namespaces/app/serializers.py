from flask_restplus import fields
from app.apis import api
from app.apis.serializers.xfields import any_of
from app.apis.serializers import resource_id

new_project_result = api.inherit('new project result', resource_id, {
    'xchat_chat_id': fields.String(attribute='xchat.chat_id', description='project xchat chat id'),
})

new_channel_message = api.model('New Channel Message', {
    'channel': fields.String(required=True),
    'uid': fields.String(required=True),
    'type': fields.String(required=True, enum=('text', 'file', 'image', 'voice')),
    'content': any_of(['string', 'object'], required=True)
})
