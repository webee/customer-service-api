from flask_restplus import fields
from app.apis import api
from app.apis.serializers.project import project_data, ProjectDataSchema, MessageSchema, message
from app.apis.serializers.staff import RawStaffSchema
from app import ma

app_user = api.model('App User', {
    'uid': fields.String(),
    'name': fields.String(),
})


session_item = api.model('Session Item', {
    'id': fields.Integer(description='session id'),
    'project': fields.Nested(project_data),
    'created': fields.Float(attribute=lambda s: s.created.timestamp()),
    'closed': fields.Float(attribute=lambda s: s.closed and s.closed.timestamp()),
    'msg_id': fields.Integer(description='last msg id'),
    'msg': fields.Nested(message, allow_null=True, description='last msg'),
    'msg_ts': fields.Float(attribute=lambda s: s.msg_ts.timestamp()),
    'sync_msg_id': fields.Integer(),
    'handler_msg_id': fields.Integer(),
})


class SessionItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'project', 'created', 'closed', 'handler', 'msg_id', 'msg', 'msg_ts', 'sync_msg_id', 'handler_msg_id')

    project = ma.Nested(ProjectDataSchema)
    created = ma.Function(lambda s: s.created.timestamp())
    closed = ma.Function(lambda s: s.closed and s.closed.timestamp())
    handler = ma.Nested(RawStaffSchema)
    msg = ma.Nested(MessageSchema)
    msg_ts = ma.Function(lambda s: s.msg_ts.timestamp())


session_item_schema = SessionItemSchema()

