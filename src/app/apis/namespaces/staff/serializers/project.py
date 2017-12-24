from flask_restplus import fields
from app.apis import api
from app.apis.serializers.project import project_data, ProjectDataSchema
from app.apis.serializers.staff import RawStaffSchema
from app import ma

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
    'handler_msg_id': fields.Integer(),
})

fetch_msgs_result = api.model('Fetch Msgs Result', {
    'msgs': fields.List(fields.Nested(message)),
    'has_more': fields.Boolean(description='is has more msgs?'),
})


class MessageSchema(ma.Schema):
    class Meta:
        fields = ("channel", "user_type", "user_id", "tx_key", "rx_key", "msg_id", "domain", "type", "content", "ts",
                  "session_id")

    ts = ma.Function(lambda msg: msg.ts.timestamp())


class SessionItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'project', 'closed', 'handler', 'msg_id', 'msg', 'msg_ts', 'sync_msg_id', 'handler_msg_id')

    project = ma.Nested(ProjectDataSchema)
    closed = ma.Function(lambda s: s.closed and s.closed.timestamp())
    handler = ma.Nested(RawStaffSchema)
    msg = ma.Nested(MessageSchema)
    msg_ts = ma.Function(lambda s: s.msg_ts.timestamp())


session_item_schema = SessionItemSchema()


class FetchMsgsResultSchema(ma.Schema):
    class Meta:
        fields = ("msgs", "has_more")

    msgs = ma.List(ma.Nested(MessageSchema))

fetch_msgs_result_schema = FetchMsgsResultSchema()
