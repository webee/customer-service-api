from flask_restplus import fields
from app.apis import api
from app.apis.serializers import resource_id


new_project_result = api.inherit('new project result', resource_id, {
    'xchat_chat_id': fields.String(attribute='xchat.chat_id', description='project xchat chat id'),
})
