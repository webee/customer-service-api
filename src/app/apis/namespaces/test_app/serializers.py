from flask_restplus import fields
from app.apis import api
from app.apis.serializers.xfields import any_of

new_msg = api.model('New Test App Channel Msg', {
    "channel": fields.String(required=True),
    "project_domain": fields.String(required=True),
    "project_type": fields.String(required=True),
    "project_biz_id": fields.String(required=True),
    "project_id": fields.Integer(required=True, min=1, example=123),
    "uid": fields.String(required=True),
    "staff_uid": fields.String(required=True),
    "type": fields.String(required=True),
    "content": any_of(['string', 'object'])
})
